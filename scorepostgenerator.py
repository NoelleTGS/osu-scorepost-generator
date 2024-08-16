import requests.exceptions
from ossapi import Ossapi
from ossapi.enums import RankStatus
from osu import Client
import dotenv
import os
import sys
import pyperclip as pc
from circleguard import *
import webbrowser
from functions import calculate_pp, mod_sort
import argparse

dotenv.load_dotenv()

try:
    cg = Circleguard(os.getenv("OSU_API_KEY"))
    client_id = int(os.getenv("OSU_CLIENT_ID"))
    client_secret = os.getenv("OSU_CLIENT_SECRET")
    legacy_mode = os.getenv("LEGACY_MODE")
except (TypeError, ValueError):
    print("An error occurred while setting environment variables. Ensure you have the .env file in the same directory "
          "as the script, and that all variables are filled in.")
    input("\nPress Enter to quit...")
    sys.exit()

callback_url = "http://localhost:7270/"
try:
    api = Ossapi(client_id, client_secret, callback_url)
except PermissionError:
    print("Error connecting to your OAuth client. Please make sure you have included the correct client ID and client "
          "secret in the .env file.")
    input("\nPress Enter to quit...")
    sys.exit()
api_osupy = Client.from_client_credentials(client_id, client_secret, callback_url)

if len(sys.argv) > 1:
    parser = argparse.ArgumentParser(description="Retrieve an osu! score and create a scorepost from it.")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("-m", "--mode", required=True, help="The mode of the score you wish to retrieve.")

    group = parser.add_mutually_exclusive_group(required=True)
    group_user = group.add_argument("-u", "--user", help="The username of the player whose score you wish to retrieve.")
    group_score = group.add_argument("-s", "--score", type=int, help="The ID of the score you wish to retrieve.")

    user_group = parser.add_mutually_exclusive_group()
    user_group.add_argument("-b", "--best", action="store_true", help="Retrieve the best score.")
    user_group.add_argument("-r", "--recent", action="store_true", help="Retrieve the recent score.")

    args = parser.parse_args()

gamemode = input("Mode (osu, taiko, fruits, mania): ")
if gamemode not in ["osu", "taiko", "fruits", "mania"]:
    print("Invalid mode.")
    input("\nPress Enter to quit...")
    sys.exit()
input_mode = input("User or score: ")
if input_mode == "user":
    currentUser = input("Enter a username: ")
    try:
        currentUser = api.user(currentUser)
    except ValueError:
        print("User not found.")
        input("\nPress Enter to quit...")
        sys.exit()
    mode = input("Best or recent: ")
    if mode == "recent":
        fails = input("Consider fails? (Y/n) ")
        if fails == "Y" or fails == "y" or fails == "":
            fails = True
        if fails == "N" or fails == "n":
            fails = False
    else:
        fails = True

    try:
        score = api.user_scores(currentUser.id, mode, include_fails=fails, mode=gamemode, limit=1, legacy_only=legacy_mode)[0]
    except IndexError:
        print("No scores found.")
        input("\nPress Enter to quit...")
        sys.exit()
    except ValueError:
        print("Invalid score type. Please enter \"best\" or \"recent\".")
        input("\nPress Enter to quit...")
        sys.exit()
    try:
        score_osupy = api_osupy.get_score_by_id(score.mode.value, score.id)
        scoreID = score.id
    except requests.exceptions.HTTPError:
        score_osupy = api_osupy.get_score_by_id_only(score.id)
        scoreID = score.id
elif input_mode == "score":
    scoreID = int(input("Enter score ID: "))
    try:
        score = api.score(scoreID)
        currentUser = api.user(score.user())
        score_osupy = api_osupy.get_score_by_id_only(scoreID)
    except IndexError:
        print("Score not found.")
        input("\nPress Enter to quit...")
        sys.exit()
else:
    print("Invalid entry.")
    input("\nPress Enter to quit...")
    sys.exit()

attributes = api.beatmap_attributes(beatmap_id=score.beatmap.id, mods=score.mods, ruleset=score.mode).attributes
beatmap = api.beatmap(beatmap_id=score.beatmap.id)
star = "%.2f" % round(attributes.star_rating, 2)
max_combo = attributes.max_combo

post = ""
if score.mode.value != 'osu':
    post += "[osu!" + str(score.mode.name.lower()) + "] "
post += currentUser.username + " | "
post += score.beatmapset.artist + " - " + score.beatmapset.title + " [" + beatmap.version + "] "
post += "(" + score.beatmapset.creator + ", " + str(star) + "*) "

# This is utterly disgusting.
score_mods = []
for mod in score_osupy.mods:
    score_mods.append((mod.mod.value, mod.settings))
score_mods.sort(key=lambda mod: mod_sort(mod[0]))

if score_mods and (not (len(score_mods) == 1 and score_mods[0][0] == 'CL') or score_osupy.build_id is not None):
    post += "+"
    for mod in score_mods:
        if mod[0] in ['DT', 'HT', 'NC', 'DC']:
            if mod[1] and 'speed_change' in mod[1]:
                post += f"{mod[0]}({mod[1]['speed_change']}x)"
            else:
                post += mod[0]
        elif mod[0] != 'CL' or score_osupy.build_id is not None:
            post += mod[0]
    post += " "

lazer_mods = []
for mod in score_osupy.mods:
    if mod.settings:
        lazer_mods.append({'acronym': mod.mod.value, 'settings': mod.settings})
    else:
        lazer_mods.append({'acronym': mod.mod.value})

if score.statistics.count_miss == 0 and score.max_combo > (max_combo * 0.99) and score.mode.value == 'osu':
    score.perfect = True

if score.mode.value == 'mania' and bool(legacy_mode):
    raw_acc = score.accuracy
else:
    raw_acc = score_osupy.accuracy
accuracy = "%.2f" % round(raw_acc * 100, 2)
if accuracy == "100.00":
    post += "SS "
else:
    post += "%.2f" % round(raw_acc * 100, 2) + "% "
if score.perfect:
    if accuracy != "100.00":
        post += "FC "
else:
    if score.mode.value != 'mania':
        post += str(score.max_combo) + "/" + str(max_combo) + " "
if score.statistics.count_miss > 0:
    post += str(score.statistics.count_miss) + "xMiss "
if not score.passed:
    post += "FAIL "

leaderboard = api.beatmap_scores(beatmap_id=score.beatmap.id, legacy_only=legacy_mode).scores
for index, item in enumerate(leaderboard):
    if item.id == score.best_id:
        post += "#" + str(index + 1) + " "
        break

if beatmap.status == RankStatus.LOVED:
    post += "💖 "

post += "| "

if score.pp is None:
    if score.beatmap.convert:
        pp = calculate_pp("curr", score, max_combo, lazer_mods, score.mode.value)
    else:
        pp = calculate_pp("curr", score, max_combo, lazer_mods)
else:
    pp = score.pp
if beatmap.status == RankStatus.RANKED:
    if score.passed and score.pp is not None:
        post += str(round(pp)) + "pp "
    else:
        post += str(round(pp)) + "pp if submitted "
else:
    post += str(round(pp)) + "pp if ranked "
if not score.perfect and score.mode.value != 'mania':
    if score.beatmap.convert:
        post += "(" + str(round(calculate_pp("fc", score, max_combo, lazer_mods, score.mode.value))) + "pp if FC) "
    else:
        post += "(" + str(round(calculate_pp("fc", score, max_combo, lazer_mods))) + "pp if FC) "

if score.replay and score.mode.value == "osu":
    try:
        replay = ReplayOssapi(api.download_score(scoreID))
    except (NameError, ValueError):
        replay = ReplayOssapi(api.download_score_mode(score.mode, score.id))
    try:
        post += "| " + str("%.2f" % round(cg.ur(replay), 2))
    except InvalidKeyException:
        print("Invalid API key. Please make sure you have added your API key in the \"OSU_API_KEY\" section "
              "of the .env file.")
    else:
        if "DT" in str(score.mods) or "HT" in str(score.mods):
            post += " cv. UR "
        else:
            post += " UR "

print(post)
try:
    pc.copy(post)
    print("Copied to clipboard.")
except pc.PyperclipException:
    print("An error occurred when coping to clipboard. If you're using Linux, make sure you have either xsel or xclip "
          "installed.")

if input("Open browser? (y/N) ") == ("y" or "yes"):
    webbrowser.open_new_tab("https://www.reddit.com/r/osugame/submit/?type=IMAGE")
