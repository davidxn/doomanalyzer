from omg import *
import sys
import json


if (len(sys.argv) < 3):
    print("    Omgifol script: measure healing items and monsters")
    print("    Usage:")
    print("    wadmeasure.py source.wad mapname")
    exit(0)

print("Loading %s..." % sys.argv[1])
inwad = WAD()
inwad.from_file(sys.argv[1])
edit = MapEditor(inwad.maps[sys.argv[2]])
f = open("./wadmeasure/thingdefs.json", "r")
thingdefs = json.load(f)

thingcounts = {}
thingpoints = {}
for t in edit.things:
    typ = str(t.type)
    skills = {"easy": t.get_easy(), "medium": t.get_medium(), "hard": t.get_hard()}
    thingdef = thingdefs.get(typ)
    if (thingdef):
        thingcategory = thingdef.get("type")
        for skill, iteminskill in skills.items():
            if iteminskill == True:
                if not thingcounts.get(typ):
                    thingcounts[typ] = {};
                if not thingpoints.get(skill):
                    thingpoints[skill] = {};
                thingpoints[skill][thingcategory] = thingpoints[skill][thingcategory]+thingdef["points"] if thingpoints[skill].get(thingcategory) else thingdef["points"]
                thingcounts[typ][skill] = thingcounts[typ][skill]+1 if thingcounts[typ].get(skill) else 1

print("{:<6s} {:>7s} {:>7s}".format("SKILL", "HEALTH", "MONSTER", "RATING"))
for skill, skilldata in sorted(thingpoints.items()):
    print("{:<6s} {:>7d} {:>7d} {:>7f}".format(skill, skilldata['health'], skilldata['monster'], 10/(skilldata['health']*1.0/skilldata['monster'])))

print("{:>4s} {:<16s} {:>4s} {:>4s} {:>4s}".format("ID", "Thing Type", "EASY", "MEDI", "HARD"))
# Output individual counts
for thingtype, skillcounts in thingcounts.items():
    thingname = thingdefs.get(thingtype)["name"]
    print("{:>4s} {:<16s} {:>4d} {:>4d} {:>4d}".format(thingtype, thingname, skillcounts.get("easy", 0), skillcounts.get("medium", 0), skillcounts.get("hard", 0)))

