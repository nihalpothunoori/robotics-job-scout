"""
Probe each company for their ATS type and slug.
Tries Lever, Greenhouse, and Ashby for every company.
Reports job count or failure for each.
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"
S.timeout = 10

LEVER      = "https://api.lever.co/v0/postings/{slug}?mode=json"
GREENHOUSE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
ASHBY      = "https://api.ashbyhq.com/posting-public/apikey/job-board/{slug}"

# (display_name, [(ats, slug), ...])  — ordered by most likely first
COMPANIES = [
    ("Tesla",                   [("workday", "tesla"), ("greenhouse", "tesla"), ("lever", "tesla")]),
    ("Figure AI",               [("lever", "figureai"), ("ashby", "figureai")]),
    ("1X Technologies",         [("lever", "1x"), ("ashby", "1x")]),
    ("Boston Dynamics",         [("greenhouse", "bostondynamics"), ("lever", "bostondynamics")]),
    ("Agility Robotics",        [("lever", "agilityrobotics"), ("greenhouse", "agilityrobotics")]),
    ("Unitree Robotics",        [("lever", "unitree"), ("greenhouse", "unitree"), ("ashby", "unitree")]),
    ("Apptronik",               [("ashby", "apptronik"), ("lever", "apptronik")]),
    ("Sanctuary AI",            [("ashby", "sanctuary"), ("lever", "sanctuary"), ("greenhouse", "sanctuary")]),
    ("Collaborative Robotics",  [("ashby", "collaborativerobotics"), ("lever", "collaborativerobotics"), ("greenhouse", "collaborativerobotics")]),
    ("UBTECH Robotics",         [("lever", "ubtech"), ("greenhouse", "ubtech"), ("ashby", "ubtech")]),
    ("Fourier Intelligence",    [("lever", "fourier"), ("greenhouse", "fourier"), ("ashby", "fourier"), ("ashby", "fourierintelligence")]),
    ("Mentee Robotics",         [("lever", "mentee"), ("greenhouse", "mentee"), ("ashby", "mentee"), ("ashby", "menteerobotics")]),
    ("Xiaomi",                  [("lever", "xiaomi"), ("greenhouse", "xiaomi"), ("ashby", "xiaomi")]),
    ("Astribot",                [("lever", "astribot"), ("greenhouse", "astribot"), ("ashby", "astribot")]),
    ("NVIDIA",                  [("greenhouse", "nvidia"), ("lever", "nvidia"), ("ashby", "nvidia")]),
    ("Microsoft",               [("greenhouse", "microsoft"), ("lever", "microsoft")]),
    ("Google DeepMind",         [("greenhouse", "deepmind"), ("lever", "deepmind"), ("greenhouse", "google")]),
    ("OpenAI",                  [("greenhouse", "openai"), ("lever", "openai"), ("ashby", "openai")]),
    ("Physical Intelligence",   [("ashby", "physicalintelligence"), ("lever", "physicalintelligence")]),
    ("Skild AI",                [("ashby", "skild"), ("lever", "skildai"), ("greenhouse", "skild")]),
    ("FANUC",                   [("lever", "fanuc"), ("greenhouse", "fanuc"), ("ashby", "fanuc")]),
    ("Yaskawa",                 [("lever", "yaskawa"), ("greenhouse", "yaskawa"), ("ashby", "yaskawa")]),
    ("ABB Robotics",            [("lever", "abb"), ("greenhouse", "abb"), ("ashby", "abb")]),
    ("KUKA",                    [("lever", "kuka"), ("greenhouse", "kuka"), ("ashby", "kuka")]),
    ("Universal Robots",        [("lever", "universal-robots"), ("greenhouse", "universalrobots"), ("ashby", "universalrobots")]),
    ("Kawasaki Robotics",       [("lever", "kawasaki"), ("greenhouse", "kawasaki"), ("ashby", "kawasaki")]),
    ("Stäubli",                 [("lever", "staubli"), ("greenhouse", "staubli"), ("ashby", "staubli")]),
    ("Epson Robots",            [("lever", "epson"), ("greenhouse", "epson"), ("ashby", "epson")]),
    ("Comau",                   [("lever", "comau"), ("greenhouse", "comau"), ("ashby", "comau")]),
    ("Denso Robotics",          [("lever", "denso"), ("greenhouse", "denso"), ("ashby", "denso")]),
    ("Amazon Robotics",         [("greenhouse", "amazon"), ("lever", "amazon"), ("ashby", "amazonrobotics")]),
    ("Symbotic",                [("greenhouse", "symbotic"), ("lever", "symbotic")]),
    ("Locus Robotics",          [("lever", "locusrobotics"), ("greenhouse", "locusrobotics")]),
    ("AutoStore",               [("lever", "autostore"), ("greenhouse", "autostore"), ("ashby", "autostore")]),
    ("Fetch Robotics",          [("lever", "fetchrobotics"), ("greenhouse", "fetchrobotics"), ("ashby", "fetch")]),
    ("Geek+",                   [("lever", "geekplus"), ("greenhouse", "geekplus"), ("ashby", "geekplus")]),
    ("Exotec",                  [("lever", "exotec"), ("greenhouse", "exotec"), ("ashby", "exotec")]),
    ("Mytra",                   [("ashby", "mytra"), ("lever", "mytra")]),
    ("Gideon Brothers",         [("lever", "gideonbrothers"), ("greenhouse", "gideonbrothers"), ("ashby", "gideon")]),
    ("GreyOrange",              [("lever", "greyorange"), ("greenhouse", "greyorange"), ("ashby", "greyorange")]),
    ("Waymo",                   [("greenhouse", "waymo"), ("lever", "waymo")]),
    ("Skydio",                  [("lever", "skydio"), ("greenhouse", "skydio")]),
    ("Clearpath Robotics",      [("ashby", "clearpath"), ("lever", "clearpath"), ("greenhouse", "clearpath")]),
    ("Outrider",                [("greenhouse", "outrider"), ("lever", "outrider")]),
    ("Saronic Technologies",    [("lever", "saronic"), ("greenhouse", "saronic"), ("ashby", "saronic")]),
    ("Metron",                  [("lever", "metron"), ("greenhouse", "metron"), ("ashby", "metron")]),
    ("Burro",                   [("lever", "burro"), ("greenhouse", "burro"), ("ashby", "burro")]),
    ("Cyngn",                   [("lever", "cyngn"), ("greenhouse", "cyngn"), ("ashby", "cyngn")]),
    ("Monarch Tractor",         [("lever", "monarchtractor"), ("greenhouse", "monarchtractor"), ("ashby", "monarch")]),
    ("Intuitive Surgical",      [("greenhouse", "intuitivesurgical"), ("lever", "intuitive")]),
    ("Stryker",                 [("greenhouse", "stryker"), ("lever", "stryker")]),
    ("Medtronic",               [("lever", "medtronic"), ("greenhouse", "medtronic"), ("ashby", "medtronic")]),
    ("Asensus Surgical",        [("lever", "asensus"), ("greenhouse", "asensus"), ("ashby", "asensus")]),
    ("Vicarious Surgical",      [("lever", "vicarioussurgical"), ("greenhouse", "vicarioussurgical"), ("ashby", "vicarious")]),
    ("CMR Surgical",            [("ashby", "cmrsurgical"), ("lever", "cmrsurgical"), ("greenhouse", "cmrsurgical")]),
    ("Procept BioRobotics",     [("greenhouse", "procept"), ("lever", "procept"), ("ashby", "procept")]),
    ("Anduril Industries",      [("lever", "anduril"), ("greenhouse", "anduril")]),
    ("AeroVironment",           [("lever", "aerovironment"), ("greenhouse", "aerovironment"), ("ashby", "aerovironment")]),
    ("Kratos Defense",          [("lever", "kratosdefense"), ("greenhouse", "kratos"), ("ashby", "kratos")]),
    ("Forterra",                [("lever", "forterra"), ("greenhouse", "forterra"), ("ashby", "forterra")]),
    ("Merlin Labs",             [("lever", "merlinlabs"), ("greenhouse", "merlinlabs"), ("ashby", "merlin")]),
    ("Epirus",                  [("lever", "epirus"), ("greenhouse", "epirus"), ("ashby", "epirus")]),
    ("Shield AI",               [("lever", "shieldai"), ("greenhouse", "shieldai")]),
    ("Saildrone",               [("lever", "saildrone"), ("greenhouse", "saildrone"), ("ashby", "saildrone")]),
    ("Teal Drones",             [("lever", "tealdrones"), ("greenhouse", "teal"), ("ashby", "teal")]),
    ("Ghost Robotics",          [("lever", "ghostrobotics"), ("greenhouse", "ghostrobotics"), ("ashby", "ghost")]),
]


def probe(ats: str, slug: str) -> int | None:
    """Return job count on success, None on failure."""
    try:
        if ats == "lever":
            r = S.get(LEVER.format(slug=slug))
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    return len(data)
        elif ats == "greenhouse":
            r = S.get(GREENHOUSE.format(slug=slug))
            if r.status_code == 200:
                return len(r.json().get("jobs", []))
        elif ats == "ashby":
            r = S.get(ASHBY.format(slug=slug))
            if r.status_code == 200:
                return len(r.json().get("jobPostings", []))
    except Exception:
        pass
    return None


def check_company(name, candidates):
    for ats, slug in candidates:
        if ats == "workday":
            continue  # skip workday in this probe
        count = probe(ats, slug)
        if count is not None:
            return name, ats, slug, count
    return name, None, None, None


results = []
with ThreadPoolExecutor(max_workers=20) as pool:
    futures = {pool.submit(check_company, name, cands): name for name, cands in COMPANIES}
    for future in as_completed(futures):
        results.append(future.result())

results.sort(key=lambda x: x[0])

print(f"\n{'Company':<30} {'ATS':<12} {'Slug':<30} {'Jobs'}")
print("-" * 85)
found, missing = [], []
for name, ats, slug, count in results:
    if ats:
        print(f"{'✅ ' + name:<30} {ats:<12} {slug:<30} {count}")
        found.append((name, ats, slug))
    else:
        print(f"{'❌ ' + name:<30} not found on Lever/Greenhouse/Ashby")
        missing.append(name)

print(f"\n✅ Found: {len(found)}  ❌ Need manual/Workday: {len(missing)}")
print("\nMissing:", ", ".join(missing))
