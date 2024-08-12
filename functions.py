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
        case ossapi.GameMode.CATCH:
            count_fruit = score.statistics.count_300
            count_drops = score.statistics.count_100
            count_droplets = score.statistics.count_50
            missed = score.statistics.count_miss
            acc = count_fruit + count_drops + count_droplets
            acc /= (acc + missed)
        case ossapi.GameMode.MANIA:
            count_max = score.statistics.count_geki
            count300 = score.statistics.count_300
            count200 = score.statistics.count_katu
            count100 = score.statistics.count_100
            count50 = score.statistics.count_50
            acc = 300 * (count_max + count300) + 200 * count200 + 100 * count100 + 50 * count50
            acc /= 300 * (count_max + count300 + count200 + count100 + count50)
    return acc * 100


def download_map(score):
    print("Downloading beatmap...")
    url = "https://osu.ppy.sh/osu/" + str(score.beatmap.id)
    r = requests.get(url)
    open('osu.osu', 'wb').write(r.content)


def calculate_pp(function, score, max_combo, mods, convert=None):
    if max_combo == 0: return 0
    download_map(score)
    map_file = Beatmap(path="osu.osu")
    calc = Performance(mods=mods)
    if convert:
        match convert:
            case "taiko":
                map_file.convert(GameMode.Taiko)
            case "fruits":
                map_file.convert(GameMode.Catch)
            case "mania":
                map_file.convert(GameMode.Mania)
    if function == "curr":
        print("Calculating score PP...")
        calc.set_accuracy(score.accuracy * 100)
        calc.set_misses(score.statistics.count_miss)
        calc.set_combo(score.max_combo)
    elif function == "fc":
        print("Calculating PP if FC...")
        calc.set_accuracy(acc_if_fc(score))
        calc.set_misses(0)
        calc.set_combo(max_combo)
    elif function == "ss":
        print("Calculating PP if SS...")
        calc.set_accuracy(100.00)
        calc.set_misses(0)
        calc.set_combo(max_combo)
    else:
        print("Invalid entry.")
        quit()
    perf = calc.calculate(map_file)
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
