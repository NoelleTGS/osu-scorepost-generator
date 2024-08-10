from ossapi import Ossapi
from ossapi.enums import RankStatus
from osu import Client
from rosu_pp_py import Beatmap, Calculator
import dotenv
import requests
import os
from sys import exit
import pyperclip as pc
from circleguard import *
import webbrowser

dotenv.load_dotenv()

cg = Circleguard(os.getenv("CIRCLEGUARD_API_KEY"))

client_id = int(os.getenv("OSU_CLIENT_ID"))
client_secret = os.getenv("OSU_CLIENT_SECRET")
callback_url = "http://localhost:7270/"
try:
    api = Ossapi(client_id, client_secret, callback_url)
except PermissionError:
    print("Error connecting to your OAuth client. Please make sure you have included the correct client ID and client "
          "secret in the .env file.")
    quit()
legacy_only = os.getenv("LEGACY_ONLY")
api_osupy = Client.from_client_credentials(client_id, client_secret, callback_url)


def acc_if_fc(score):
    count300 = score.statistics.count_300
    count100 = score.statistics.count_100
    count50 = score.statistics.count_50
    acc = (300 * count300 + 100 * count100 + 50 * count50) / (300 * (count300 + count100 + count50))
    return acc * 100


def downloadmap(score):
    print("Downloading beatmap...")
    url = "https://osu.ppy.sh/osu/" + str(score.beatmap.id)
    r = requests.get(url)
    open('osu.osu', 'wb').write(r.content)


def calculatePP(function, score, maxcombo):
    if maxcombo == 0: return 0
    downloadmap(score)
    mapfile = Beatmap(path="osu.osu")
    calc = Calculator(mods=score.mods.value)
    if function == "curr":
        print("Calculating score PP...")
        calc.set_acc(score.accuracy * 100)
        calc.set_n_misses(score.statistics.count_miss)
        calc.set_combo(score.max_combo)
    elif function == "fc":
        print("Calculating PP if FC...")
        calc.set_acc(acc_if_fc(score))
        calc.set_n_misses(0)
        calc.set_combo(maxcombo)
    elif function == "ss":
        print("Calculating PP if SS...")
        calc.set_acc(100.00)
        calc.set_n_misses(0)
        calc.set_combo(maxcombo)
    else:
        print("Invalid entry.")
        quit()
    perf = calc.performance(mapfile)
    try:
        os.remove("osu.osu")
    except OSError as x:
        print("Error occurred: %s : %s" % ("osu", x.strerror))
    return perf.pp


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
        if fails == "Y" or fails == "y" or fails == "": fails = True
        if fails == "N" or fails == "n": fails = False
    else:
        fails = True

    try:
        score = api.user_scores(currentUser.id, mode, include_fails=fails, mode=gamemode, limit=1, legacy_only=legacy_only)[0]
    except IndexError:
        print("No scores found.")
        exit()
elif inputMode == "score":
    scoreID = int(input("Enter score ID: "))
    try:
        score = api.score(scoreID)
        currentUser = api.user(score.user())
    except IndexError:
        print("Score not found.")
        exit()
else:
    print("Invalid entry.")
    quit()

try:
    score_osupy = api_osupy.get_score_by_id_only(score.id)
except requests.exceptions.HTTPError:
    score_osupy = api_osupy.get_score_by_id(score.mode.value, score.id)
beatmap = api.beatmap(beatmap_id=score.beatmap.id)
star = "%.2f" % round(
    api.beatmap_attributes(beatmap_id=score.beatmap.id, mods=score.mods, ruleset=gamemode).attributes.star_rating, 2)
maxcombo = beatmap.max_combo

post = ""
post += currentUser.username + " | "
post += score.beatmapset.artist + " - " + score.beatmapset.title + " [" + beatmap.version + "] "
post += "(" + score.beatmapset.creator + ", " + str(star) + "*) "

# This is disgusting. I hope all you CL haters are happy.
# Yes I know there are better ways to do this, I'm leaving it like this to prove a point.
if not (len(score_osupy.mods) == 1 and score_osupy.mods[0].mod.value == 'CL'):
    post += "+" + "".join(mod.mod.value for mod in score_osupy.mods if mod.mod.value != 'CL') + " "

accuracy = "%.2f" % round(score.accuracy * 100, 2)
if accuracy == "100.00":
    post += "SS "
else:
    post += "%.2f" % round(score.accuracy * 100, 2) + "% "
if score.perfect:
    if accuracy != "100.00":
        post += "FC "
else:
    post += str(score.max_combo) + "/" + str(beatmap.max_combo) + " "
if score.statistics.count_miss > 0: post += str(score.statistics.count_miss) + "xMiss "
if not score.passed:
    post += "FAIL "

leaderboard = api.beatmap_scores(beatmap_id=score.beatmap.id, legacy_only=legacy_only).scores
for index, item in enumerate(leaderboard):
    if item.id == score.best_id:
        post += "#" + str(index + 1) + " "
        break

if beatmap.status == RankStatus.LOVED: post += "💖 "

post += "| "

if score.pp is None:
    pp = calculatePP("curr", score, maxcombo)
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
    post += "(" + str(int(calculatePP("fc", score, maxcombo))) + "pp if FC) "

if score.replay:
    try:
        replay = ReplayOssapi(api.download_score(score.id))
    except:
        replay = ReplayOssapi(api.download_score_mode(score.mode, score.id))
    try:
        post += "| " + str("%.2f" % round(cg.ur(replay), 2))
    except InvalidKeyException:
        print("Invalid API key. Please make sure you have added your API key in the \"CIRCLEGUARD_API_KEY\" section "
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
except:
    print("An error occurred when coping to clipboard. If you're using Linux, make sure you have either xsel or xclip "
          "installed.")

if input("Open browser? (y/N) ") == ("y" or "yes"):
    webbrowser.open_new_tab("https://www.reddit.com/r/osugame/submit/?type=IMAGE")
