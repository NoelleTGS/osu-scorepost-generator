import ossapi
import requests
import os
from rosu_pp_py import Beatmap, Performance, GameMode


def acc_if_fc(score):
    match score.mode:
        case ossapi.GameMode.OSU:
            count300 = score.statistics.count_300
            count100 = score.statistics.count_100
            count50 = score.statistics.count_50
            acc = (300 * count300 + 100 * count100 + 50 * count50) / (300 * (count300 + count100 + count50))
        case ossapi.GameMode.TAIKO:
            count300 = score.statistics.count_300
            count100 = score.statistics.count_100
            acc = (count300 + 0.5 * count100) / (count300 + count100)
    return acc * 100


def downloadmap(score):
    print("Downloading beatmap...")
    url = "https://osu.ppy.sh/osu/" + str(score.beatmap.id)
    r = requests.get(url)
    open('osu.osu', 'wb').write(r.content)


def calculate_pp(function, score, maxcombo, mods, convert=None):
    if maxcombo == 0: return 0
    downloadmap(score)
    mapfile = Beatmap(path="osu.osu")
    calc = Performance(mods=mods)
    if convert:
        match convert:
            case "taiko":
                mapfile.convert(GameMode.Taiko)
            case "fruits":
                mapfile.convert(GameMode.Catch)
            case "mania":
                mapfile.convert(GameMode.Mania)
    if function == "curr":
        print("Calculating score PP...")
        calc.set_accuracy(score.accuracy * 100)
        calc.set_misses(score.statistics.count_miss)
        calc.set_combo(score.max_combo)
    elif function == "fc":
        print("Calculating PP if FC...")
        calc.set_accuracy(acc_if_fc(score))
        calc.set_misses(0)
        calc.set_combo(maxcombo)
    elif function == "ss":
        print("Calculating PP if SS...")
        calc.set_accuracy(100.00)
        calc.set_misses(0)
        calc.set_combo(maxcombo)
    else:
        print("Invalid entry.")
        quit()
    perf = calc.calculate(mapfile)
    try:
        os.remove("osu.osu")
    except OSError as x:
        print("Error occurred: %s : %s" % ("osu", x.strerror))
    return perf.pp


def mod_sort(mod):
    mod_order = ['EZ', 'HD', 'DT', 'NC', 'HT', 'DC', 'HR', 'SD', 'PF', 'FL', 'RX', 'AP']
    if mod in mod_order:
        return mod_order.index(mod)
    else:
        return len(mod_order)
