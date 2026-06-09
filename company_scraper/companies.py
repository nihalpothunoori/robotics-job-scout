# Top robotics companies — (display_name, ats_type, slug)
#
# ats_type options:
#   greenhouse       — REST API, no auth
#   lever            — REST API, no auth
#   ashby            — REST API (returns 401 for most; use playwright_ashby instead)
#   playwright_ashby — headless Chromium renders jobs.ashbyhq.com/{slug}
#   workday          — REST API, slug format: '{subdomain}:{wd_num}:{tenant}'
#   playwright_tesla — headless Chromium renders tesla.com/careers/search
#
# Companies not listed (no programmatic access):
#   Workday (auth required): Mobileye, Stryker, Torc Robotics, ABB, Yaskawa
#   Custom (bot-protected):  OpenAI, Intuitive Surgical, Wing (Alphabet),
#                            SpaceX, Blue Origin, Microsoft, iRobot, Dyson
#   No US internships: Unitree, Xiaomi, Fourier, UBTECH, Geek+, Hai Robotics
#   Industrial (no US intern programs): FANUC, KUKA, Kawasaki, Stäubli, Denso
#   Defunct/acquired: Fetch Robotics (→ Zebra), Covariant (→ Amazon), Argo AI

COMPANIES = [
    # ── Greenhouse ────────────────────────────────────────────────────────────────
    ("Figure AI",              "greenhouse",        "figureai"),
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
    ("Nuro",                   "greenhouse",        "nuro"),
    ("May Mobility",           "greenhouse",        "maymobility"),
    ("Carbon Robotics",        "greenhouse",        "carbonrobotics"),
    ("Path Robotics",          "greenhouse",        "pathrobotics"),
    ("Stack AV",               "greenhouse",        "stackav"),
    ("Zipline",                "greenhouse",        "flyzipline"),
    ("Kodiak Robotics",        "greenhouse",        "kodiak"),
    ("Diligent Robotics",      "greenhouse",        "diligentrobotics"),
    ("Nimble Robotics",        "greenhouse",        "nimblerobotics"),

    # ── Lever ─────────────────────────────────────────────────────────────────────
    ("Shield AI",              "lever",             "shieldai"),
    ("Sanctuary AI",           "lever",             "sanctuary"),
    ("Saronic Technologies",   "lever",             "saronic"),
    ("Merlin Labs",            "lever",             "merlinlabs"),
    ("Cyngn",                  "lever",             "cyngn"),
    ("Forterra",               "lever",             "forterra"),
    ("Zoox",                   "lever",             "zoox"),
    ("Dexterity",              "lever",             "dexterity"),

    # ── Ashby via Playwright (API locked, page is public) ─────────────────────────
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
    ("Applied Intuition",      "playwright_ashby",  "appliedintuition"),
    ("Viam",                   "playwright_ashby",  "viam"),
    ("Joby Aviation",          "playwright_ashby",  "joby"),
    ("Machina Labs",           "playwright_ashby",  "machinalabs"),

    # ── Workday (public REST API) ──────────────────────────────────────────────────
    ("NVIDIA",                 "workday",           "nvidia:5:NVIDIAExternalCareerSite"),
    ("Boston Dynamics",        "workday",           "bostondynamics:1:Boston_Dynamics"),

    # ── Tesla (custom career page, Playwright) ─────────────────────────────────────
    ("Tesla",                  "playwright_tesla",  "tesla"),
]
