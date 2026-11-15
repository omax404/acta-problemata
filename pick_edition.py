#!/usr/bin/env python3
"""Print today's edition.json on stdout.  usage: pick_edition.py [YYYY-MM-DD]
Rotates through bank/*.json by day of year. The answer_key is NOT included in the output."""
import json, sys, glob, datetime, pathlib
day = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
files = sorted(glob.glob(str(pathlib.Path(__file__).parent / "bank" / "*.json")))
doy = day.timetuple().tm_yday
b = json.load(open(files[(doy - 1) % len(files)], encoding="utf-8"))
b.pop("answer_key", None)
b.update(edition_no=doy, year=day.year, date=day.strftime("%d/%m/%Y"),
         code=f"AP-{day.year}-{doy:03d}-MA-{b['sector_code']}-{b['level']}",
         archive_url="https://omax404.github.io/acta-problemata/", unsubscribe_url="{{UNSUB_URL}}")
print(json.dumps(b, ensure_ascii=False, indent=1))
