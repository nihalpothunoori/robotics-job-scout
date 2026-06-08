# Top robotics companies — (display_name, ats_type, slug)
#
# ats_type options:
#   greenhouse       — REST API, no auth
#   lever            — REST API, no auth
#   ashby            — REST API (returns 401 for most; use playwright_ashby instead)
#   playwright_ashby — headless Chromium renders jobs.ashbyhq.com/{slug}
#
# Companies not listed (no programmatic access):
#   Workday: Tesla, NVIDIA, Boston Dynamics, Stryker, Medtronic, ABB, Universal Robots
#   iCIMS: Joby Aviation
#   Custom: OpenAI, Intuitive Surgical, Ghost Robotics (Paylocity)
#   No US internships: Unitree, Xiaomi, Fourier, UBTECH, Astribot, Mentee
#   Industrial (no US intern programs): FANUC, Yaskawa, KUKA, Kawasaki, Stäubli, Epson, Comau, Denso
#   Defunct/acquired: Fetch Robotics (→ Zebra), Covariant (→ Amazon)
#
# These are caught by LinkedIn/Google job-scout searches instead.

COMPANIES = [
    # ── Greenhouse (confirmed working) ─────────────────────────────────────────
    ("Figure AI",              "greenhouse",        "figure"),
    ("Waymo",                  "greenhouse",        "waymo"),
    ("Agility Robotics",       "greenhouse",        "agilityrobotics"),
    ("Google DeepMind",        "greenhouse",        "deepmind"),
    ("Anduril Industries",     "greenhouse",        "andurilindustries"),
    ("Apptronik",              "greenhouse",        "apptronik"),
    ("Epirus",                 "greenhouse",        "epirus"),
    ("Metron",                 "greenhouse",        "metron"),
    ("Outrider",               "greenhouse",        "outrider"),
    ("Locus Robotics",         "greenhouse",        "locusrobotics"),
    ("Vicarious Surgical",     "greenhouse",        "vicarioussurgical"),
    ("Motional",               "greenhouse",        "motional"),
    ("Archer Aviation",        "greenhouse",        "archer"),

    # ── Lever (confirmed working) ──────────────────────────────────────────────
    ("Shield AI",              "lever",             "shieldai"),
    ("Sanctuary AI",           "lever",             "sanctuary"),
    ("Saronic Technologies",   "lever",             "saronic"),
    ("Merlin Labs",            "lever",             "merlinlabs"),
    ("Cyngn",                  "lever",             "cyngn"),
    ("Forterra",               "lever",             "forterra"),

    # ── Ashby via Playwright (API locked, page is public) ─────────────────────
    ("Physical Intelligence",  "playwright_ashby",  "physicalintelligence"),
    ("1X Technologies",        "playwright_ashby",  "1xtechnologies"),
    ("Skydio",                 "playwright_ashby",  "skydio"),
    ("Aurora",                 "playwright_ashby",  "aurora"),
    ("Skild AI",               "playwright_ashby",  "skild"),
    ("Collaborative Robotics", "playwright_ashby",  "collaborativerobotics"),
    ("Saildrone",              "playwright_ashby",  "saildrone"),
    ("AeroVironment",          "playwright_ashby",  "aerovironment"),
    ("Kratos Defense",         "playwright_ashby",  "kratos"),
    ("Monarch Tractor",        "playwright_ashby",  "monarch-tractor"),
    ("Procept BioRobotics",    "playwright_ashby",  "procept"),
    ("CMR Surgical",           "playwright_ashby",  "cmrsurgical"),
    ("Asensus Surgical",       "playwright_ashby",  "asensus"),
    ("Burro",                  "playwright_ashby",  "burro"),
    ("GreyOrange",             "playwright_ashby",  "greyorange"),
    ("Gideon Brothers",        "playwright_ashby",  "gideon"),
    ("Teal Drones",            "playwright_ashby",  "tealdrones"),
    ("Symbotic",               "playwright_ashby",  "symbotic"),
    ("Mytra",                  "playwright_ashby",  "mytra"),
    ("Exotec",                 "playwright_ashby",  "exotec"),
    ("AutoStore",              "playwright_ashby",  "autostore"),
    ("Clearpath Robotics",     "playwright_ashby",  "clearpath"),
    ("Amazon Robotics",        "playwright_ashby",  "amazonrobotics"),
]
