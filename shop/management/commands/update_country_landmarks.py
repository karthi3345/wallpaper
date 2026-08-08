"""
Update all Country image fields to use real famous-place / landmark photos
from Wikimedia Commons (via the Wikipedia REST API).

Each country is mapped to its most iconic landmark. The command fetches
the landmark's Wikipedia thumbnail and stores that URL on the Country.

Run:  python3 manage.py update_country_landmarks
"""
import json
import time
import urllib.parse
import urllib.request
import urllib.error

from django.core.management.base import BaseCommand
from shop.models import Country

# ---------------------------------------------------------------------------
# Slug → famous landmark (Wikipedia article title).
# One iconic, world-recognised place per country.
# NOTE: apostrophes are written as \\x27 to avoid Python's adjacent-string
# literal concatenation silently eating them.
# ---------------------------------------------------------------------------
APOS = "\x27"  # apostrophe

SLUG_TO_LANDMARK = {
    # A
    "afghanistan":         "Minaret of Jam",
    "albania":             "Kruje Castle",
    "algeria":             "Kasbah of Algiers",
    "andorra":             "Andorra la Vella",
    "angola":              "Fortaleza de Sao Miguel",
    "antigua-and-barbuda": "Nelson" + APOS + "s Dockyard",
    "argentina":           "Iguazu Falls",
    "armenia":             "Khor Virap",
    "australia":           "Sydney Opera House",
    "austria":             "Schonbrunn Palace",
    "azerbaijan":          "Flame Towers",
    # B
    "bahamas":             "Atlantis Paradise Island",
    "bahrain":             "Bahrain World Trade Center",
    "bangladesh":          "Sixty Dome Mosque",
    "barbados":            "Bridgetown",
    "belarus":             "Mir Castle Complex",
    "belgium":             "Grand-Place",
    "belize":              "Great Blue Hole",
    "benin":               "Royal Palaces of Abomey",
    "bhutan":              "Paro Taktsang",
    "bolivia":             "Salar de Uyuni",
    "bosnia-and-herzegovina": "Stari Most",
    "botswana":            "Okavango Delta",
    "brazil":              "Christ the Redeemer (statue)",
    "brunei":              "Sultan Omar Ali Saifuddien Mosque",
    "bulgaria":            "Alexander Nevsky Cathedral, Sofia",
    "burkina-faso":        "Banfora",
    "burundi":             "Lake Tanganyika",
    # C
    "cabo-verde":          "Cidade Velha",
    "cambodia":            "Angkor Wat",
    "cameroon":            "Mount Cameroon",
    "canada":              "CN Tower",
    "central-african-republic": "Dzanga-Sangha Forest Reserve",
    "chad":                "Zakouma National Park",
    "chile":               "Torres del Paine",
    "china":               "Great Wall of China",
    "colombia":            "Salt Cathedral of Zipaquira",
    "comoros":             "Mount Karthala",
    "congo-brazzaville":   "Brazzaville",
    "costa-rica":          "Arenal Volcano",
    "croatia":             "Dubrovnik",
    "cuba":                "Old Havana",
    "cyprus":              "Nicosia",
    "czechia":             "Prague Castle",
    # D
    "denmark":             "Nyhavn",
    "djibouti":            "Tadjoura",
    "dominica":            "Morne Trois Pitons National Park",
    "dominican-republic":  "Santo Domingo",
    # E
    "ecuador":             "Galapagos Islands",
    "egypt":               "Giza pyramid complex",
    "el-salvador":         "Lake Coatepeque",
    "england":             "Big Ben",
    "equatorial-guinea":   "Malabo",
    "eritrea":             "Asmara",
    "estonia":             "Tallinn Old Town",
    "eswatini":            "Mlilwane Wildlife Sanctuary",
    "ethiopia":            "Lalibela",
    # F
    "fiji":                "Mamanuca Islands",
    "finland":             "Suomenlinna",
    "france":              "Eiffel Tower",
    # G
    "gabon":               "Pongara National Park",
    "gambia":              "Kunta Kinteh Island",
    "georgia-country":     "Gergeti Trinity Church",
    "germany":             "Neuschwanstein Castle",
    "ghana":               "Cape Coast Castle",
    "greece":              "Acropolis of Athens",
    "grenada":             "Grenada",
    "guatemala":           "Tikal",
    "guinea":              "Mount Nimba Strict Nature Reserve",
    "guinea-bissau":       "Bissagos Islands",
    "guyana":              "Kaieteur Falls",
    # H
    "haiti":               "Citadelle Laferriere",
    "honduras":            "Copan",
    "hungary":             "Buda Castle",
    # I
    "iceland":             "Hallgrimskirkja",
    "india":               "Taj Mahal",
    "indonesia":           "Borobudur",
    "iran":                "Naqsh-e Jahan Square",
    "iraq":                "Samarra",
    "ireland":             "Cliffs of Moher",
    "israel":              "Old City (Jerusalem)",
    "italy":               "Colosseum",
    "ivory-coast":         "Basilica of Our Lady of Peace",
    # J
    "jamaica":             "Dunn" + APOS + "s River Falls",
    "japan":               "Mount Fuji",
    "jordan":              "Petra",
    # K
    "kazakhstan":          "Baiterek Tower",
    "kenya":               "Maasai Mara",
    "kiribati":            "South Tarawa",
    "kosovo":              "Visoki Decani",
    "kuwait":              "Kuwait Towers",
    "kyrgyzstan":          "Issyk-Kul",
    # L
    "laos":                "Luang Prabang",
    "latvia":              "Riga",
    "lebanon":             "Baalbek",
    "lesotho":             "Maloti Mountains",
    "liberia":             "Liberia",
    "libya":               "Leptis Magna",
    "liechtenstein":       "Vaduz Castle",
    "lithuania":           "Trakai Island Castle",
    "luxembourg":          "Bock (Luxembourg)",
    # M
    "madagascar":          "Avenue of the Baobabs",
    "malawi":              "Lake Malawi",
    "malaysia":            "Petronas Towers",
    "maldives":            "Male (Maldives)",
    "mali":                "Great Mosque of Djenne",
    "malta":               "Valletta",
    "marshall-islands":    "Majuro Atoll",
    "mauritania":          "Chinguetti",
    "mauritius":           "Le Morne Brabant",
    "mexico":              "Chichen Itza",
    "micronesia":          "Nan Madol",
    "moldova":             "Old Orhei",
    "monaco":              "Monte Carlo Casino",
    "mongolia":            "Gobi Desert",
    "montenegro":          "Kotor",
    "morocco":             "Marrakesh",
    "mozambique":          "Island of Mozambique",
    "myanmar":             "Bagan",
    # N
    "namibia":             "Sossusvlei",
    "nauru":               "Anibare Bay",
    "nepal":               "Mount Everest",
    "netherlands":         "Keukenhof",
    "new-zealand":         "Milford Sound",
    "nicaragua":           "San Juan del Sur",
    "niger":               "Agadez",
    "nigeria":             "Zuma Rock",
    "north-korea":         "Paektu Mountain",
    "north-macedonia":     "Lake Ohrid",
    "norway":              "Geirangerfjord",
    # O
    "oman":                "Sultan Qaboos Grand Mosque",
    # P
    "pakistan":            "Badshahi Mosque",
    "palau":               "Rock Islands (Palau)",
    "palestine":           "Church of the Nativity",
    "panama":              "Panama Canal",
    "papua-new-guinea":    "Kokoda Track",
    "paraguay":            "Itaipu Dam",
    "peru":                "Machu Picchu",
    "philippines":         "Banaue Rice Terraces",
    "poland":              "Wieliczka Salt Mine",
    "portugal":            "Belem Tower",
    # R
    "romania":             "Bran Castle",
    "russia":              "Saint Basil" + APOS + "s Cathedral",
    "rwanda":              "Volcanoes National Park",
    # S
    "saint-kitts-and-nevis": "Brimstone Hill Fortress",
    "saint-lucia":         "The Pitons",
    "saint-vincent":       "La Soufriere (volcano)",
    "samoa":               "Samoa",
    "san-marino":          "Guaita",
    "sao-tome-and-principe": "Pico Cao Grande",
    "saudi-arabia":        "Kingdom Centre",
    "senegal":             "Goree",
    "serbia":              "Belgrade Fortress",
    "seychelles":          "Anse Source d" + APOS + "Argent",
    "sierra-leone":        "Bunce Island",
    "singapore":           "Gardens by the Bay",
    "slovakia":            "Bojnice Castle",
    "slovenia":            "Lake Bled",
    "solomon-islands":     "Mataniko Falls",
    "somalia":             "Mogadishu",
    "south-africa":        "Table Mountain",
    "south-korea":         "Gyeongbokgung Palace",
    "south-sudan":         "Juba",
    "spain":               "Sagrada Familia",
    "sri-lanka":           "Sigiriya",
    "sudan":               "Meroe",
    "suriname":            "Paramaribo",
    "sweden":              "Gamla stan",
    "switzerland":         "Matterhorn",
    "syria":               "Krak des Chevaliers",
    # T
    "taiwan":              "Taipei 101",
    "tajikistan":          "Pamir Mountains",
    "tanzania":            "Mount Kilimanjaro",
    "thailand":            "Wat Pho",
    "timor-leste":         "Atauro Island",
    "togo":                "Koutammakou",
    "tonga":               "Trilithon",
    "trinidad-and-tobago": "Pitch Lake",
    "tunisia":             "Carthage",
    "turkey":              "Hagia Sophia",
    "turkmenistan":        "Darvaza gas crater",
    "tuvalu":              "Funafuti",
    # U
    "uganda":              "Bwindi Impenetrable National Park",
    "ukraine":             "Saint Sophia" + APOS + "s Cathedral, Kyiv",
    "uae":                 "Burj Khalifa",
    "united-states":       "Statue of Liberty",
    "uruguay":             "Colonia del Sacramento",
    "uzbekistan":          "Registan",
    # V
    "vanuatu":             "Mount Yasur",
    "vatican-city":        "St. Peter" + APOS + "s Basilica",
    "venezuela":           "Angel Falls",
    "vietnam":             "Ha Long Bay",
    # Y, Z
    "yemen":               "Shibam",
    "zambia":              "Victoria Falls",
    "zimbabwe":            "Great Zimbabwe",
}

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
SEARCH_API = (
    "https://en.wikipedia.org/w/api.php"
    "?action=query&format=json&prop=pageimages|redirects"
    "&piprop=thumbnail&pithumbsize=640"
    "&redirects=1&titles={}"
)
HEADERS = {
    "User-Agent": "MahashankhBot/1.0 (contact: dev@mahashank.com)",
    "Accept": "application/json",
}


def _fetch_thumbnail(landmark):
    """Return a thumbnail URL from Wikipedia for *landmark*, or None."""
    encoded = urllib.parse.quote(landmark)

    # 1. REST summary endpoint
    try:
        req = urllib.request.Request(WIKI_API + encoded, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        thumb = data.get("thumbnail", {}).get("source")
        if thumb:
            return thumb
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        pass

    # 2. MediaWiki pageimages API
    try:
        req = urllib.request.Request(
            SEARCH_API.format(encoded), headers=HEADERS
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            thumb = page.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        pass

    return None


class Command(BaseCommand):
    help = "Update all country images to use famous-place / landmark photos from Wikipedia."

    def add_arguments(self, parser):
        parser.add_argument(
            "--retry", action="store_true",
            help="Only update countries that still have a flagcdn URL.",
        )

    def handle(self, *args, **options):
        retry_only = options.get("retry", False)
        updated = 0
        skipped = 0
        failed = []

        qs = Country.objects.all().order_by("name")
        for country in qs:
            landmark = SLUG_TO_LANDMARK.get(country.slug)

            if retry_only and "flagcdn" not in (country.image or ""):
                skipped += 1
                continue

            if not landmark:
                failed.append((country.slug, "no landmark mapping"))
                continue

            thumb = _fetch_thumbnail(landmark)
            if thumb:
                if len(thumb) > 1000:
                    failed.append((country.slug, "URL too long"))
                    self.stdout.write(self.style.WARNING(
                        f"  --  {country.name:35s} -> {landmark}  (URL too long)"
                    ))
                    time.sleep(0.2)
                    continue
                country.image = thumb
                country.save(update_fields=["image"])
                updated += 1
                self.stdout.write(f"  OK  {country.name:35s} -> {landmark}")
            else:
                failed.append((country.slug, landmark))
                self.stdout.write(self.style.WARNING(
                    f"  --  {country.name:35s} -> {landmark}  (no image)"
                ))

            time.sleep(0.2)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done. Updated {updated} country images with famous places."
        ))
        if failed:
            self.stdout.write(self.style.WARNING(
                f"{len(failed)} countries missing images: "
                f"{[s for s, _ in failed]}"
            ))
        if skipped:
            self.stdout.write(f"Skipped {skipped} (already had non-flag images).")
