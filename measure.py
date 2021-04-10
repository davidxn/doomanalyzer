from omg import *
import sys
import json

thing_defs = {}


def output_header():
    headers = ["Map", "Size"]
    for skill_name in ["easy", "medium", "hard"]:
        headers.append(skill_name + "HealthPoints")
        headers.append(skill_name + "MonsterPoints")
        headers.append(skill_name + "AmmoPoints")
        headers.append(skill_name + "MonsterCount")
        headers.append(skill_name + "AmmoSurplus")
        headers.append(skill_name + "HealthRatio")
    for header in headers:
        print("{:<20s}".format(header), end="")
    print()

class Measure:

    thing_defs = {}

    def __init__(self, map_lump_name):
        if not self.thing_defs:
            f = open("./wadmeasure/thingdefs.json", "r")
            self.thing_defs = json.load(f)
        self.thing_points = {}
        self.thing_counts = {}
        self.size_data = {}
        self.map_lump_name = map_lump_name

    def reset(self):
        self.thing_points = {}
        self.thing_counts = {}
        self.size_data = {}
        self.map_lump_name = ""

    def open_wad(self, filename):
        in_wad = WAD()
        in_wad.from_file(filename)
        return in_wad

    def measure_everything(self, edit):
        self.measure_size(edit)
        self.count_things(edit)

    def measure_size(self, edit):
        x_min = y_min = 32767
        x_max = y_max = -32768
        for v in edit.vertexes:
            x_min = min(x_min, v.x)
            x_max = max(x_max, v.x)
            y_min = min(y_min, -v.y)
            y_max = max(y_max, -v.y)
        self.size_data = {"x_min":x_min, "x_max":x_max, "y_min":y_min, "y_max":y_max, "x_size":x_max-x_min, "y_size":y_max-y_min, "size":(x_max-x_min)*(y_max-y_min)}

    def count_things(self, edit):
        for t in edit.things:
            typ = str(t.type)
            skills = {"easy": t.get_easy(), "medium": t.get_medium(), "hard": t.get_hard()}
            thing_def = self.thing_defs.get(typ)
            if thing_def:
                thing_category = thing_def.get("type")
                for skill, item_in_skill in skills.items():
                    if item_in_skill:
                        if not self.thing_counts.get(typ):
                            self.thing_counts[typ] = {}
                        if not self.thing_points.get(skill):
                            self.thing_points[skill] = {}
                        self.thing_points[skill][thing_category] = self.thing_points[skill][thing_category] + thing_def["points"] if \
                        self.thing_points[skill].get(thing_category) else thing_def["points"]
                        self.thing_counts[typ][skill] = self.thing_counts[typ][skill] + 1 if self.thing_counts[typ].get(skill) else 1

    def output_scorecard(self):
        # Work out our ratings by comparing
        for skill_name in ["easy", "medium", "hard"]:
            skill_data = self.thing_points.get(skill_name)
            print("-" * 40)
            print(skill_name.capitalize())
            print("-" * 40)
            print("{:>7s} {:>7s} {:>7s}".format("HEALTH", "MONSTER", "AMMO"))
            print("{:>7d} {:>7d} {:>7d}".format(skill_data['health'], skill_data['monster'], skill_data['ammo']))
            print()
            health_ratio, ammo_surplus, monster_count = self.calculate_data(skill_name, skill_data)
            print("Monster count: " + str(monster_count))
            print("Bounding box: " + str(self.size_data.get("x_size", 0)) + " x " + str(self.size_data.get("y_size", 0)) + " = " + str(self.size_data.get("size", 0)/10000))
            print("Health difficulty: " + str(round(health_ratio, 2)))
            print("Ammo surplus: " + str(ammo_surplus))
            print("-" * 40)
            print()

        print("{:>4s} {:<16s} {:>4s} {:>4s} {:>4s}".format("ID", "Thing Type", "EASY", "MEDI", "HARD"))
        # Output individual counts
        for thing_type, skill_counts in self.thing_counts.items():
            thing_name = self.thing_defs.get(thing_type)["name"]
            print("{:>4s} {:<16s} {:>4d} {:>4d} {:>4d}".format(thing_type, thing_name, skill_counts.get("easy", 0),
                                                               skill_counts.get("medium", 0),
                                                               skill_counts.get("hard", 0)))

    def output_row(self):
        outputs = [self.map_lump_name, self.size_data.get("size", 0)/10000]
        for skill_name in ["easy", "medium", "hard"]:
            skill_data = self.thing_points.get(skill_name)
            health_ratio, ammo_surplus, monster_count = self.calculate_data(skill_name, skill_data)
            outputs += [skill_data.get('health', 0), skill_data.get('monster', 0), skill_data.get('ammo', 0), monster_count, ammo_surplus, round(health_ratio, 2)]
        for output in outputs:
            print("{:<20s}".format(str(output)), end="")
        print()

    def get_ratio(self, numerator, denominator):
        return int(100 / (numerator * 1.0 / denominator))

    def calculate_data(self, skill_name, skill_data):
        monster_count = 0
        item_counts = self.thing_counts
        health_ratio = skill_data.get('monster', 0) / skill_data.get('health', 1)
        ammo_surplus = skill_data.get('ammo', 0) - skill_data.get('monster', 0)
        for thing_type, thing_count in item_counts.items():
            if self.thing_defs.get(thing_type).get("type") == "monster":
                monster_count += thing_count.get(skill_name, 0)
        return health_ratio, ammo_surplus, monster_count

if (sys.argv[1] == 'single' and len(sys.argv) < 4) or (sys.argv[1] == 'file' and len(sys.argv) < 3):
    print("    Omgifol script: measure healing items and monsters")
    print("    Usage:")
    print("    wadmeasure.py single source.wad mapname")
    print("    wadmeasure.py file descriptorname")
    exit(0)


if sys.argv[1] == 'single':
    print("Loading %s..." % sys.argv[2])
    filename = sys.argv[2]
    map_lump_name = sys.argv[3]
    measure = Measure(map_lump_name)
    edit = MapEditor(measure.open_wad(filename).maps[map_lump_name])
    measure.measure_everything(edit)
    measure.output_scorecard()

elif sys.argv[1] == 'file':
    print("Loading definition file %s" % sys.argv[2])
    with open(sys.argv[2], "r") as f:
        measure_def = json.load(f)

    output_header()

    for wad_measure_def in measure_def['wads']:
        for map_lump_name in wad_measure_def['maps']:
            measure = Measure(map_lump_name)
            wad = measure.open_wad(wad_measure_def['filename'])
            doom_map = wad.maps[map_lump_name]
            edit = MapEditor(doom_map)
            measure.measure_everything(edit)
            measure.output_row()
            measure.reset()