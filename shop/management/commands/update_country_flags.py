"""
Update all Country image fields to use real country flag images from flagcdn.
Each country gets its own unique flag image — no more random/shared images.

Run: python3 manage.py update_country_flags
"""
from django.core.management.base import BaseCommand
from shop.models import Country

# ISO 3166-1 alpha-2 codes mapped by country slug
# flagcdn.com/w640/<code>.png gives a 640px wide PNG flag
SLUG_TO_ISO = {
    'afghanistan': 'af', 'albania': 'al', 'algeria': 'dz', 'andorra': 'ad',
    'angola': 'ao', 'antigua-and-barbuda': 'ag', 'argentina': 'ar', 'armenia': 'am',
    'australia': 'au', 'austria': 'at', 'azerbaijan': 'az', 'bahamas': 'bs',
    'bahrain': 'bh', 'bangladesh': 'bd', 'barbados': 'bb', 'belarus': 'by',
    'belgium': 'be', 'belize': 'bz', 'benin': 'bj', 'bhutan': 'bt',
    'bolivia': 'bo', 'bosnia-and-herzegovina': 'ba', 'botswana': 'bw', 'brazil': 'br',
    'brunei': 'bn', 'bulgaria': 'bg', 'burkina-faso': 'bf', 'burundi': 'bi',
    'cabo-verde': 'cv', 'cambodia': 'kh', 'cameroon': 'cm', 'canada': 'ca',
    'central-african-republic': 'cf', 'chad': 'td', 'chile': 'cl', 'china': 'cn',
    'colombia': 'co', 'comoros': 'km', 'congo-brazzaville': 'cg', 'costa-rica': 'cr',
    'croatia': 'hr', 'cuba': 'cu', 'cyprus': 'cy', 'czechia': 'cz',
    'denmark': 'dk', 'djibouti': 'dj', 'dominica': 'dm', 'dominican-republic': 'do',
    'ecuador': 'ec', 'egypt': 'eg', 'el-salvador': 'sv', 'england': 'gb-eng',
    'equatorial-guinea': 'gq', 'eritrea': 'er', 'estonia': 'ee', 'eswatini': 'sz',
    'ethiopia': 'et', 'fiji': 'fj', 'finland': 'fi', 'france': 'fr',
    'gabon': 'ga', 'gambia': 'gm', 'georgia-country': 'ge', 'germany': 'de',
    'ghana': 'gh', 'greece': 'gr', 'grenada': 'gd', 'guatemala': 'gt',
    'guinea': 'gn', 'guinea-bissau': 'gw', 'guyana': 'gy', 'haiti': 'ht',
    'honduras': 'hn', 'hungary': 'hu', 'iceland': 'is', 'india': 'in',
    'indonesia': 'id', 'iran': 'ir', 'iraq': 'iq', 'ireland': 'ie',
    'israel': 'il', 'italy': 'it', 'ivory-coast': 'ci', 'jamaica': 'jm',
    'japan': 'jp', 'jordan': 'jo', 'kazakhstan': 'kz', 'kenya': 'ke',
    'kiribati': 'ki', 'kosovo': 'xk', 'kuwait': 'kw', 'kyrgyzstan': 'kg',
    'laos': 'la', 'latvia': 'lv', 'lebanon': 'lb', 'lesotho': 'ls',
    'liberia': 'lr', 'libya': 'ly', 'liechtenstein': 'li', 'lithuania': 'lt',
    'luxembourg': 'lu', 'madagascar': 'mg', 'malawi': 'mw', 'malaysia': 'my',
    'maldives': 'mv', 'mali': 'ml', 'malta': 'mt', 'marshall-islands': 'mh',
    'mauritania': 'mr', 'mauritius': 'mu', 'mexico': 'mx', 'micronesia': 'fm',
    'moldova': 'md', 'monaco': 'mc', 'mongolia': 'mn', 'montenegro': 'me',
    'morocco': 'ma', 'mozambique': 'mz', 'myanmar': 'mm', 'namibia': 'na',
    'nauru': 'nr', 'nepal': 'np', 'netherlands': 'nl', 'new-zealand': 'nz',
    'nicaragua': 'ni', 'niger': 'ne', 'nigeria': 'ng', 'north-korea': 'kp',
    'north-macedonia': 'mk', 'norway': 'no', 'oman': 'om', 'pakistan': 'pk',
    'palau': 'pw', 'palestine': 'ps', 'panama': 'pa', 'papua-new-guinea': 'pg',
    'paraguay': 'py', 'peru': 'pe', 'philippines': 'ph', 'poland': 'pl',
    'portugal': 'pt', 'romania': 'ro', 'russia': 'ru', 'rwanda': 'rw',
    'saint-kitts-and-nevis': 'kn', 'saint-lucia': 'lc', 'saint-vincent': 'vc',
    'samoa': 'ws', 'san-marino': 'sm', 'sao-tome-and-principe': 'st',
    'saudi-arabia': 'sa', 'senegal': 'sn', 'serbia': 'rs', 'seychelles': 'sc',
    'sierra-leone': 'sl', 'singapore': 'sg', 'slovakia': 'sk', 'slovenia': 'si',
    'solomon-islands': 'sb', 'somalia': 'so', 'south-africa': 'za', 'south-korea': 'kr',
    'south-sudan': 'ss', 'spain': 'es', 'sri-lanka': 'lk', 'sudan': 'sd',
    'suriname': 'sr', 'sweden': 'se', 'switzerland': 'ch', 'syria': 'sy',
    'taiwan': 'tw', 'tajikistan': 'tj', 'tanzania': 'tz', 'thailand': 'th',
    'timor-leste': 'tl', 'togo': 'tg', 'tonga': 'to', 'trinidad-and-tobago': 'tt',
    'tunisia': 'tn', 'turkey': 'tr', 'turkmenistan': 'tm', 'tuvalu': 'tv',
    'uganda': 'ug', 'ukraine': 'ua', 'uae': 'ae', 'united-states': 'us',
    'uruguay': 'uy', 'uzbekistan': 'uz', 'vanuatu': 'vu', 'vatican-city': 'va',
    'venezuela': 've', 'vietnam': 'vn', 'yemen': 'ye', 'zambia': 'zm',
    'zimbabwe': 'zw',
}

FLAG_BASE = 'https://flagcdn.com/w640/'


class Command(BaseCommand):
    help = 'Update all country images to use real country flags from flagcdn.'

    def handle(self, *args, **options):
        updated = 0
        missing = []

        for country in Country.objects.all():
            iso = SLUG_TO_ISO.get(country.slug)
            if iso:
                country.image = f'{FLAG_BASE}{iso}.png'
                country.save(update_fields=['image'])
                updated += 1
            else:
                missing.append(country.slug)

        self.stdout.write(
            self.style.SUCCESS(
                f'Updated {updated} country images with flags. '
                f'Missing: {len(missing)}'
            )
        )
        if missing:
            self.stdout.write(self.style.WARNING(f'Slugs without ISO mapping: {missing}'))
