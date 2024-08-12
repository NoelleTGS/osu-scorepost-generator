from ossapi import Ossapi
from ossapi.enums import RankStatus
from osu import Client
import dotenv
import os
from sys import exit
import pyperclip as pc
from circleguard import *
import webbrowser
from functions import calculate_pp, mod_sort

dotenv.load_dotenv()

cg = Circleguard(os.getenv("OSU_API_KEY"))

client_id = int(os.getenv("OSU_CLIENT_ID"))
client_secret = os.getenv("OSU_CLIENT_SECRET")
callback_url = "http://localhost:7270/"
try:
    api = Ossapi(client_id, client_secret, callback_url)
except PermissionError:
    print("Error connecting to your OAuth client. Please make sure you have included the correct client ID and client "
          "secret in the .env file.")
    quit()
legacy_mode = os.getenv("LEGACY_MODE")
api_osupy = Client.from_client_credentials(client_id, client_secret, callback_url)

gamemode = input("Mode (osu, taiko, fruits, mania): ")
inputMode = input("User or score: ")
if inputMode == "user":
    currentUser = input("Enter a username: ")
    try:
        currentUser = api.user(currentUser)
    except ValueError:
        print("User not found.")
        exit()
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
        score_osupy = api_osupy.get_score_by_id(score.mode.value, score.id)
    except IndexError:
        print("No scores found.")
        exit()
elif inputMode == "score":
    scoreID = int(input("Enter score ID: "))
    try:
        score = api.score(scoreID)
        currentUser = api.user(score.user())
        score_osupy = api_osupy.get_score_by_id_only(scoreID)
    except IndexError:
        print("Score not found.")
        exit()
else:
    print("Invalid entry.")
    quit()


beatmap = api.beatmap(beatmap_id=score.beatmap.id)
star = "%.2f" % round(
    api.beatmap_attributes(beatmap_id=score.beatmap.id, mods=score.mods, ruleset=gamemode).attributes.star_rating, 2)
maxcombo = beatmap.max_combo

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

if score_mods and not (len(score_mods) == 1 and score_mods[0][0] == 'CL'):
    post += "+"
    for mod in score_mods:
        if mod[0] in ['DT', 'HT', 'NC', 'DC']:
            if mod[1] and 'speed_change' in mod[1]:
                post += f"{mod[0]}({mod[1]['speed_change']}x)"
            else:
                post += mod[0]
        elif mod[0] != 'CL':
            post += mod[0]
    post += " "

lazermods = []
for mod in score_osupy.mods:
    if mod.settings:
        lazermods.append({'acronym': mod.mod.value, 'settings': mod.settings})
    else:
        lazermods.append({'acronym': mod.mod.value})

if score.statistics.count_miss == 0 and score.max_combo > (beatmap.max_combo * 0.99):
    score.perfect = True

accuracy = "%.2f" % round(score_osupy.accuracy * 100, 2)
if accuracy == "100.00":
    post += "SS "
else:
    post += "%.2f" % round(score_osupy.accuracy * 100, 2) + "% "
if score.perfect:
    if accuracy != "100.00":
        post += "FC "
else:
    post += str(score.max_combo) + "/" + str(beatmap.max_combo) + " "
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
    pp = calculate_pp("curr", score, maxcombo, lazermods)
else:
    pp = score.pp
if beatmap.status == RankStatus.RANKED:
    if score.passed and score.pp is not None:
        post += str(round(pp)) + "pp "
    else:
        post += str(round(pp)) + "pp if submitted "
else:
    post += str(round(pp)) + "pp if ranked "
if not score.perfect:
    post += "(" + str(round(calculate_pp("fc", score, maxcombo, lazermods))) + "pp if FC) "

if score.replay:
    try:
        replay = ReplayOssapi(api.download_score(score.id))
    except Exception:
        replay = ReplayOssapi(api.download_score_mode(score.mode, score.id))
    try:
        post += "| " + str("%.2f" % round(cg.ur(replay), 2))
    except InvalidKeyException:
        print("Invalid API key. Please make sure you have added your API key in the \"OSU_API_KEY\" section "
              "of the .env file.")
    except TypeError:
        print("An error occurred while fetching UR. UR for modes other than osu!std is not currently available.")
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
