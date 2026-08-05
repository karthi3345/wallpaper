"""
Seed geographic catalog: Countries, Regions, Cities.
Associates existing products with relevant cities.
Run: python manage.py seed_geo
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from shop.models import Country, Region, City, Product


class Command(BaseCommand):
    help = 'Seed geographic catalog data (countries, regions, cities) and link products.'

    # ── Helpers ──────────────────────────────────────────────
    IMG = 'https://images.unsplash.com/'

    @staticmethod
    def _img(photo_id, w=900):
        return f'https://images.unsplash.com/photo-{photo_id}?w={w}&q=80'

    # ── Data ─────────────────────────────────────────────────
    COUNTRIES = [
        {
            'name': 'India',
            'slug': 'india',
            'image': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1200&q=80',
            'description': 'From the palaces of Rajasthan to the temples of Tamil Nadu — discover wallpapers inspired by India\u2019s rich heritage of art, architecture, and craftsmanship.',
            'regions': [
                {
                    'name': 'Maharashtra',
                    'slug': 'maharashtra',
                    'image': 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=900&q=80',
                    'description': 'Home to Mumbai and Pune — a vibrant blend of colonial architecture and modern design.',
                    'cities': [
                        {'name': 'Mumbai', 'slug': 'mumbai', 'image': 'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=900&q=80', 'description': 'The city of dreams — where Art Deco meets Bollywood glamour.', 'featured': True},
                        {'name': 'Pune', 'slug': 'pune', 'image': 'https://images.unsplash.com/photo-1620177247689-7382c9322a55?w=900&q=80', 'description': 'Cultural capital of Maharashtra with rich Maratha heritage.', 'featured': True},
                        {'name': 'Nagpur', 'slug': 'nagpur', 'image': '', 'description': 'The orange city of India.', 'featured': False},
                        {'name': 'Nashik', 'slug': 'nashik', 'image': '', 'description': 'Ancient holy city on the banks of the Godavari.', 'featured': False},
                        {'name': 'Aurangabad', 'slug': 'aurangabad', 'image': '', 'description': 'Gateway to the Ajanta and Ellora caves.', 'featured': False},
                    ],
                },
                {
                    'name': 'Delhi NCR',
                    'slug': 'delhi-ncr',
                    'image': 'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=900&q=80',
                    'description': 'The national capital region — Mughal monuments, Lutyens\u2019 boulevards, and modern luxury interiors.',
                    'cities': [
                        {'name': 'New Delhi', 'slug': 'new-delhi', 'image': 'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=900&q=80', 'description': 'India\u2019s capital — where Mughal heritage meets modern luxury.', 'featured': True},
                        {'name': 'Gurgaon', 'slug': 'gurgaon', 'image': '', 'description': 'Millennium city with soaring skyscrapers.', 'featured': True},
                        {'name': 'Noida', 'slug': 'noida', 'image': '', 'description': 'A planned city with modern infrastructure.', 'featured': False},
                    ],
                },
                {
                    'name': 'Karnataka',
                    'slug': 'karnataka',
                    'image': 'https://images.unsplash.com/photo-1591777334917-83d70d10ec5b?w=900&q=80',
                    'description': 'Bangalore\u2019s tech corridors and Mysore\u2019s royal palaces — South India\u2019s design hub.',
                    'cities': [
                        {'name': 'Bangalore', 'slug': 'bangalore', 'image': 'https://images.unsplash.com/photo-1596176530529-78163a4f7af2?w=900&q=80', 'description': 'The garden city and India\u2019s tech capital.', 'featured': True},
                        {'name': 'Mysore', 'slug': 'mysore', 'image': '', 'description': 'Royal city of palaces and silk.', 'featured': True},
                        {'name': 'Mangalore', 'slug': 'mangalore', 'image': '', 'description': 'Coastal city with Portuguese-influenced architecture.', 'featured': False},
                        {'name': 'Hubli', 'slug': 'hubli', 'image': '', 'description': 'A major commercial hub of North Karnataka.', 'featured': False},
                    ],
                },
                {
                    'name': 'Tamil Nadu',
                    'slug': 'tamil-nadu',
                    'image': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=900&q=80',
                    'description': 'Temple architecture, Chola bronzes, and the colonial charm of Chennai.',
                    'cities': [
                        {'name': 'Chennai', 'slug': 'chennai', 'image': 'https://images.unsplash.com/photo-1574316071302-54604c5a7e90?w=900&q=80', 'description': 'Gateway to the South, rich in Dravidian temple art.', 'featured': True},
                        {'name': 'Madurai', 'slug': 'madurai', 'image': '', 'description': 'Ancient temple city of the Meenakshi.', 'featured': True},
                        {'name': 'Coimbatore', 'slug': 'coimbatore', 'image': '', 'description': 'Manchester of South India.', 'featured': False},
                        {'name': 'Ooty', 'slug': 'ooty', 'image': '', 'description': 'Queen of hill stations.', 'featured': False},
                    ],
                },
                {
                    'name': 'Rajasthan',
                    'slug': 'rajasthan',
                    'image': 'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=900&q=80',
                    'description': 'The land of kings — forts, palaces, frescoes, and vibrant Pichwai and miniature art traditions.',
                    'cities': [
                        {'name': 'Jaipur', 'slug': 'jaipur', 'image': 'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=900&q=80', 'description': 'The Pink City — famous for frescoed havelis and block prints.', 'featured': True},
                        {'name': 'Udaipur', 'slug': 'udaipur', 'image': 'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=900&q=80', 'description': 'City of lakes and royal palaces.', 'featured': True},
                        {'name': 'Jodhpur', 'slug': 'jodhpur', 'image': '', 'description': 'The Blue City beneath the Mehrangarh Fort.', 'featured': False},
                        {'name': 'Jaisalmer', 'slug': 'jaisalmer', 'image': '', 'description': 'The Golden City in the Thar Desert.', 'featured': False},
                        {'name': 'Pushkar', 'slug': 'pushkar', 'image': '', 'description': 'Sacred lake town and pilgrimage site.', 'featured': False},
                    ],
                },
                {
                    'name': 'West Bengal',
                    'slug': 'west-bengal',
                    'image': 'https://images.unsplash.com/photo-1558431382-27e303142243?w=900&q=80',
                    'description': 'Kolkata\u2019s colonial-era mansions, terracotta temples, and the art of Shantiniketan.',
                    'cities': [
                        {'name': 'Kolkata', 'slug': 'kolkata', 'image': 'https://images.unsplash.com/photo-1558431382-27e303142243?w=900&q=80', 'description': 'City of joy — colonial heritage and Bengali artistry.', 'featured': True},
                        {'name': 'Darjeeling', 'slug': 'darjeeling', 'image': '', 'description': 'Queen of the Himalayas.', 'featured': False},
                        {'name': 'Siliguri', 'slug': 'siliguri', 'image': '', 'description': 'Gateway to Northeast India.', 'featured': False},
                    ],
                },
                {
                    'name': 'Gujarat',
                    'slug': 'gujarat',
                    'image': 'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=900&q=80',
                    'description': 'From the White Desert of Kutch to the step-wells of Patan — Gujarat\u2019s textile and embroidery heritage.',
                    'cities': [
                        {'name': 'Ahmedabad', 'slug': 'ahmedabad', 'image': 'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=900&q=80', 'description': 'UNESCO World Heritage city with pol architecture.', 'featured': True},
                        {'name': 'Surat', 'slug': 'surat', 'image': '', 'description': 'Textile and diamond hub of India.', 'featured': True},
                        {'name': 'Vadodara', 'slug': 'vadodara', 'image': '', 'description': 'Cultural capital with the Laxmi Vilas Palace.', 'featured': False},
                        {'name': 'Rajkot', 'slug': 'rajkot', 'image': '', 'description': 'City of Bandhani and Patola weaves.', 'featured': False},
                    ],
                },
                {
                    'name': 'Telangana',
                    'slug': 'telangana',
                    'image': 'https://images.unsplash.com/photo-1644238873987-3eb75863d7c6?w=900&q=80',
                    'description': 'Hyderabad\u2019s Nizam heritage, Bidri metalwork, and Deccani miniature paintings.',
                    'cities': [
                        {'name': 'Hyderabad', 'slug': 'hyderabad', 'image': 'https://images.unsplash.com/photo-1644238873987-3eb75863d7c6?w=900&q=80', 'description': 'City of Nizams, pearls, and biryani.', 'featured': True},
                        {'name': 'Warangal', 'slug': 'warangal', 'image': '', 'description': 'Kakatiya dynasty\u2019s architectural marvels.', 'featured': False},
                    ],
                },
                {
                    'name': 'Kerala',
                    'slug': 'kerala',
                    'image': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=900&q=80',
                    'description': 'God\u2019s Own Country — backwaters, mural paintings, and colonial port cities.',
                    'cities': [
                        {'name': 'Kochi', 'slug': 'kochi', 'image': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=900&q=80', 'description': 'Port city with Chinese fishing nets and colonial forts.', 'featured': True},
                        {'name': 'Thiruvananthapuram', 'slug': 'thiruvananthapuram', 'image': '', 'description': 'Capital city with Padmanabhaswamy Temple.', 'featured': True},
                        {'name': 'Kozhikode', 'slug': 'kozhikode', 'image': '', 'description': 'City of spices and Malabar trade.', 'featured': False},
                    ],
                },
            ],
        },
        {
            'name': 'Italy',
            'slug': 'italy',
            'image': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=1200&q=80',
            'description': 'From the canals of Venice to the frescoes of Florence — Italy\u2019s Renaissance heritage and Mediterranean elegance.',
            'regions': [
                {
                    'name': 'Tuscany',
                    'slug': 'tuscany',
                    'image': 'https://images.unsplash.com/photo-1543429776-2782fc8e1acd?w=900&q=80',
                    'description': 'Birthplace of the Renaissance — Florence, Siena, and the rolling hills of Chianti.',
                    'cities': [
                        {'name': 'Florence', 'slug': 'florence', 'image': 'https://images.unsplash.com/photo-1543429776-2782fc8e1acd?w=900&q=80', 'description': 'Cradle of the Renaissance and home of Botticelli and Michelangelo.', 'featured': True},
                        {'name': 'Siena', 'slug': 'siena', 'image': '', 'description': 'Medieval Gothic masterpiece.', 'featured': True},
                        {'name': 'Pisa', 'slug': 'pisa', 'image': '', 'description': 'Home of the famous Leaning Tower.', 'featured': False},
                    ],
                },
                {
                    'name': 'Lazio',
                    'slug': 'lazio',
                    'image': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=900&q=80',
                    'description': 'Rome and the Eternal City\u2019s layers of art from antiquity to Baroque.',
                    'cities': [
                        {'name': 'Rome', 'slug': 'rome', 'image': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=900&q=80', 'description': 'The Eternal City — ancient ruins, Vatican frescoes, and Baroque fountains.', 'featured': True},
                    ],
                },
                {
                    'name': 'Veneto',
                    'slug': 'veneto',
                    'image': 'https://images.unsplash.com/photo-1514890547357-a9ee288728e0?w=900&q=80',
                    'description': 'Venice and the Venetian tradition of palazzo d\u00e9cor and Murano glass.',
                    'cities': [
                        {'name': 'Venice', 'slug': 'venice', 'image': 'https://images.unsplash.com/photo-1514890547357-a9ee288728e0?w=900&q=80', 'description': 'La Serenissima — canals, palazzi, and Murano glass art.', 'featured': True},
                        {'name': 'Verona', 'slug': 'verona', 'image': '', 'description': 'City of Romeo and Juliet.', 'featured': False},
                    ],
                },
                {
                    'name': 'Lombardy',
                    'slug': 'lombardy',
                    'image': 'https://images.unsplash.com/photo-1515897178289-7e48e6c9439b?w=900&q=80',
                    'description': 'Milan — global capital of fashion and contemporary design.',
                    'cities': [
                        {'name': 'Milan', 'slug': 'milan', 'image': 'https://images.unsplash.com/photo-1515897178289-7e48e6c9439b?w=900&q=80', 'description': 'Fashion capital and home of the Duomo and La Scala.', 'featured': True},
                    ],
                },
            ],
        },
        {
            'name': 'France',
            'slug': 'france',
            'image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1200&q=80',
            'description': 'From the salons of Paris to the lavender fields of Provence — French wallpaper traditions from Toile de Jouy to Art Deco.',
            'regions': [
                {
                    'name': '\u00cele-de-France',
                    'slug': 'ile-de-france',
                    'image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=900&q=80',
                    'description': 'Paris — the city of light, art, and timeless interior design.',
                    'cities': [
                        {'name': 'Paris', 'slug': 'paris', 'image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=900&q=80', 'description': 'The City of Light — Haussmann boulevards and Mus\u00e9e d\u2019Orsay.', 'featured': True},
                        {'name': 'Versailles', 'slug': 'versailles', 'image': '', 'description': 'Royal palace and gardens of Louis XIV.', 'featured': True},
                    ],
                },
                {
                    'name': 'Provence-Alpes-C\u00f4te d\u2019Azur',
                    'slug': 'provence',
                    'image': 'https://images.unsplash.com/photo-1531608139434-188356b3df77?w=900&q=80',
                    'description': 'Lavender fields, Mediterranean coast, and Proven\u00e7al charm.',
                    'cities': [
                        {'name': 'Nice', 'slug': 'nice', 'image': 'https://images.unsplash.com/photo-1531608139434-188356b3df77?w=900&q=80', 'description': 'Pearl of the French Riviera.', 'featured': True},
                        {'name': 'Marseille', 'slug': 'marseille', 'image': '', 'description': 'Oldest port city in France.', 'featured': False},
                        {'name': 'Aix-en-Provence', 'slug': 'aix-en-provence', 'image': '', 'description': 'City of a thousand fountains.', 'featured': False},
                    ],
                },
                {
                    'name': 'Occitanie',
                    'slug': 'occitanie',
                    'image': 'https://images.unsplash.com/photo-1601123344178-6f52a87befed?w=900&q=80',
                    'description': 'Carcassonne, Toulouse, and the Canal du Midi.',
                    'cities': [
                        {'name': 'Toulouse', 'slug': 'toulouse', 'image': 'https://images.unsplash.com/photo-1601123344178-6f52a87befed?w=900&q=80', 'description': 'The Pink City and aerospace capital.', 'featured': True},
                    ],
                },
            ],
        },
        {
            'name': 'England',
            'slug': 'england',
            'image': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=1200&q=80',
            'description': 'From William Morris florals to Victorian damasks — England\u2019s wallpaper heritage is the backbone of classic interior design.',
            'regions': [
                {
                    'name': 'Greater London',
                    'slug': 'greater-london',
                    'image': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=900&q=80',
                    'description': 'London — from Georgian townhouses to Shoreditch lofts.',
                    'cities': [
                        {'name': 'London', 'slug': 'london', 'image': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=900&q=80', 'description': 'A global capital of art, design, and architecture.', 'featured': True},
                    ],
                },
                {
                    'name': 'Cotswolds',
                    'slug': 'cotswolds',
                    'image': 'https://images.unsplash.com/photo-1515488764276-beab7607c1e6?w=900&q=80',
                    'description': 'Honey-stone villages and quintessential English countryside.',
                    'cities': [
                        {'name': 'Bath', 'slug': 'bath', 'image': 'https://images.unsplash.com/photo-1515488764276-beab7607c1e6?w=900&q=80', 'description': 'Roman baths and Georgian crescents.', 'featured': True},
                        {'name': 'Oxford', 'slug': 'oxford', 'image': '', 'description': 'The dreaming spires of the oldest university.', 'featured': True},
                    ],
                },
                {
                    'name': 'Greater Manchester',
                    'slug': 'greater-manchester',
                    'image': 'https://images.unsplash.com/photo-1515597291474-5f91708b2ec3?w=900&q=80',
                    'description': 'Industrial heritage reborn as a modern cultural hub.',
                    'cities': [
                        {'name': 'Manchester', 'slug': 'manchester', 'image': 'https://images.unsplash.com/photo-1515597291474-5f91708b2ec3?w=900&q=80', 'description': 'Industrial revolution birthplace turned creative city.', 'featured': True},
                        {'name': 'Liverpool', 'slug': 'liverpool', 'image': '', 'description': 'Maritime city and birthplace of The Beatles.', 'featured': False},
                    ],
                },
            ],
        },
        {
            'name': 'United States',
            'slug': 'united-states',
            'image': 'https://images.unsplash.com/photo-1485871981521-5b1fd3805eee?w=1200&q=80',
            'description': 'From New York lofts to California modernism — America\u2019s diverse design landscape.',
            'regions': [
                {
                    'name': 'New York',
                    'slug': 'new-york-state',
                    'image': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=900&q=80',
                    'description': 'The Empire State — Art Deco icons, SoHo galleries, and Brooklyn brownstones.',
                    'cities': [
                        {'name': 'New York City', 'slug': 'new-york-city', 'image': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=900&q=80', 'description': 'The city that never sleeps — skyline and loft living.', 'featured': True},
                        {'name': 'Buffalo', 'slug': 'buffalo', 'image': '', 'description': 'Prairie School architecture and Frank Lloyd Wright.', 'featured': False},
                    ],
                },
                {
                    'name': 'California',
                    'slug': 'california',
                    'image': 'https://images.unsplash.com/photo-1444985906900-31a034ce40b0?w=900&q=80',
                    'description': 'Mid-century modern, Hollywood Regency, and the Pacific coast aesthetic.',
                    'cities': [
                        {'name': 'Los Angeles', 'slug': 'los-angeles', 'image': 'https://images.unsplash.com/photo-1444985906900-31a034ce40b0?w=900&q=80', 'description': 'Hollywood glamour and mid-century modern.', 'featured': True},
                        {'name': 'San Francisco', 'slug': 'san-francisco', 'image': '', 'description': 'Victorian painted ladies and bay views.', 'featured': True},
                        {'name': 'San Diego', 'slug': 'san-diego', 'image': '', 'description': 'Sun-kissed coastal living.', 'featured': False},
                    ],
                },
                {
                    'name': 'Illinois',
                    'slug': 'illinois',
                    'image': 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=900&q=80',
                    'description': 'Chicago — birthplace of the skyscraper and Prairie School.',
                    'cities': [
                        {'name': 'Chicago', 'slug': 'chicago', 'image': 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=900&q=80', 'description': 'Architecture capital with stunning skyline.', 'featured': True},
                    ],
                },
            ],
        },
        {
            'name': 'Japan',
            'slug': 'japan',
            'image': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1200&q=80',
            'description': 'From Tokyo\u2019s neon minimalism to Kyoto\u2019s ancient temples — Japan\u2019s aesthetic of wabi-sabi and refined simplicity.',
            'regions': [
                {
                    'name': 'Kanto',
                    'slug': 'kanto',
                    'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=900&q=80',
                    'description': 'Tokyo and the Greater Metropolitan Area — ultra-modern metropolis.',
                    'cities': [
                        {'name': 'Tokyo', 'slug': 'tokyo', 'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=900&q=80', 'description': 'World\u2019s largest metropolis — minimalism meets neon.', 'featured': True},
                    ],
                },
                {
                    'name': 'Kansai',
                    'slug': 'kansai',
                    'image': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=900&q=80',
                    'description': 'Kyoto, Osaka — the cultural and historical heart of Japan.',
                    'cities': [
                        {'name': 'Kyoto', 'slug': 'kyoto', 'image': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=900&q=80', 'description': 'Ancient capital of temples, gardens, and geisha.', 'featured': True},
                        {'name': 'Osaka', 'slug': 'osaka', 'image': '', 'description': 'Kitchen of Japan and vibrant street culture.', 'featured': True},
                    ],
                },
            ],
        },
        # ── 7. Spain ──────────────────────────────────────────
        {
            'name': 'Spain',
            'slug': 'spain',
            'image': 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=1200&q=80',
            'description': 'From Gaud\u00ed\u2019s Barcelona to the Moorish palaces of Andalusia — Spain\u2019s vibrant blend of Islamic geometry, Gothic grandeur, and Mediterranean color.',
            'regions': [
                {
                    'name': 'Catalonia',
                    'slug': 'catalonia',
                    'image': 'https://images.unsplash.com/photo-1583422409518-1444a352609c?w=900&q=80',
                    'description': 'Barcelona and the Modernisme movement of Antoni Gaud\u00ed.',
                    'cities': [
                        {'name': 'Barcelona', 'slug': 'barcelona', 'image': 'https://images.unsplash.com/photo-1583422409518-1444a352609c?w=900&q=80', 'description': 'Gaud\u00ed\u2019s playground of color, tile, and organic form.', 'featured': True},
                        {'name': 'Girona', 'slug': 'girona', 'image': '', 'description': 'Medieval walled city with rainbow riverside houses.', 'featured': False},
                    ],
                },
                {
                    'name': 'Andalusia',
                    'slug': 'andalusia',
                    'image': 'https://images.unsplash.com/photo-1597212720158-e21cc6e7cb98?w=900&q=80',
                    'description': 'Seville, Granada, C\u00f3rdoba \u2014 the heart of Moorish Spain.',
                    'cities': [
                        {'name': 'Seville', 'slug': 'seville', 'image': 'https://images.unsplash.com/photo-1597212720158-e21cc6e7cb98?w=900&q=80', 'description': 'Flamenco, azulejo tiles, and Alc\u00e1zar palaces.', 'featured': True},
                        {'name': 'Granada', 'slug': 'granada', 'image': '', 'description': 'Home of the breathtaking Alhambra.', 'featured': True},
                        {'name': 'C\u00f3rdoba', 'slug': 'cordoba', 'image': '', 'description': 'Mezquita and flowering patios.', 'featured': False},
                    ],
                },
                {
                    'name': 'Community of Madrid',
                    'slug': 'madrid-region',
                    'image': 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=900&q=80',
                    'description': 'Spain\u2019s elegant capital of art museums and royal palaces.',
                    'cities': [
                        {'name': 'Madrid', 'slug': 'madrid', 'image': 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=900&q=80', 'description': 'Royal palaces, Prado masterpieces, and vibrant street life.', 'featured': True},
                        {'name': 'Toledo', 'slug': 'toledo', 'image': '', 'description': 'City of three cultures perched on a hill.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 8. Germany ─────────────────────────────────────────
        {
            'name': 'Germany',
            'slug': 'germany',
            'image': 'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=1200&q=80',
            'description': 'From Bavarian castles to Bauhaus minimalism — Germany\u2019s design heritage spans medieval half-timbering to the most influential modernist movement in history.',
            'regions': [
                {
                    'name': 'Bavaria',
                    'slug': 'bavaria',
                    'image': 'https://images.unsplash.com/photo-1601022453588-29f4e2d4b96f?w=900&q=80',
                    'description': 'Fairytale castles, alpine meadows, and Baroque churches.',
                    'cities': [
                        {'name': 'Munich', 'slug': 'munich', 'image': 'https://images.unsplash.com/photo-1601022453588-29f4e2d4b96f?w=900&q=80', 'description': 'Bavaria\u2019s capital of beer, art, and royal squares.', 'featured': True},
                        {'name': 'Nuremberg', 'slug': 'nuremberg', 'image': '', 'description': 'Medieval imperial city with castle views.', 'featured': False},
                    ],
                },
                {
                    'name': 'Berlin',
                    'slug': 'berlin-region',
                    'image': 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=900&q=80',
                    'description': 'Germany\u2019s edgy capital where history meets avant-garde.',
                    'cities': [
                        {'name': 'Berlin', 'slug': 'berlin', 'image': 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=900&q=80', 'description': 'Bauhaus heritage, street art, and industrial-chic lofts.', 'featured': True},
                        {'name': 'Potsdam', 'slug': 'potsdam', 'image': '', 'description': 'Sanssouci Palace and Prussian gardens.', 'featured': False},
                    ],
                },
                {
                    'name': 'Saxony',
                    'slug': 'saxony',
                    'image': 'https://images.unsplash.com/photo-1574691250077-03a929faece4?w=900&q=80',
                    'description': 'Dresden\u2019s Baroque splendor and the Elbe Sandstone Mountains.',
                    'cities': [
                        {'name': 'Dresden', 'slug': 'dresden', 'image': 'https://images.unsplash.com/photo-1574691250077-03a929faece4?w=900&q=80', 'description': 'Florence on the Elbe \u2014 rebuilt Baroque jewel.', 'featured': True},
                        {'name': 'Leipzig', 'slug': 'leipzig', 'image': '', 'description': 'New Berlin \u2014 a rising art and music city.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 9. Morocco ─────────────────────────────────────────
        {
            'name': 'Morocco',
            'slug': 'morocco',
            'image': 'https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=1200&q=80',
            'description': 'From the zellige tilework of Marrakech to the blue-washed streets of Chefchaouen \u2014 Morocco\u2019s craftsmanship in geometric patterns, carved plaster, and rich textiles.',
            'regions': [
                {
                    'name': 'Marrakech-Safi',
                    'slug': 'marrakech-safi',
                    'image': 'https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=900&q=80',
                    'description': 'The Red City and its surrounding Atlas Mountains.',
                    'cities': [
                        {'name': 'Marrakech', 'slug': 'marrakech', 'image': 'https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=900&q=80', 'description': 'Medina labyrinth of souks, riads, and Bahia Palace.', 'featured': True},
                        {'name': 'Essaouira', 'slug': 'essaouira', 'image': '', 'description': 'Windy port town with blue shutters and ramparts.', 'featured': True},
                    ],
                },
                {
                    'name': 'F\u00e8s-Mekn\u00e8s',
                    'slug': 'fes-meknes',
                    'image': 'https://images.unsplash.com/photo-1539020140153-e479b8c5a9b8?w=900&q=80',
                    'description': 'The imperial cities of Morocco\u2019s interior.',
                    'cities': [
                        {'name': 'F\u00e8s', 'slug': 'fes', 'image': 'https://images.unsplash.com/photo-1539020140153-e479b8c5a9b8?w=900&q=80', 'description': 'World\u2019s oldest medina \u2014 a UNESCO living museum.', 'featured': True},
                        {'name': 'Mekn\u00e8s', 'slug': 'meknes', 'image': '', 'description': 'Isma\u2019il\u2019s royal city with monumental gates.', 'featured': False},
                    ],
                },
                {
                    'name': 'Tangier-Tetouan',
                    'slug': 'tangier-tetouan',
                    'image': 'https://images.unsplash.com/photo-1568393690040-28f7e8fc7e7f?w=900&q=80',
                    'description': 'The gateway between Africa and Europe.',
                    'cities': [
                        {'name': 'Chefchaouen', 'slug': 'chefchaouen', 'image': 'https://images.unsplash.com/photo-1568393690040-28f7e8fc7e7f?w=900&q=80', 'description': 'The Blue Pearl \u2014 an indigo dream in the Rif Mountains.', 'featured': True},
                        {'name': 'Tangier', 'slug': 'tangier', 'image': '', 'description': 'International zone that inspired Bowles and Matisse.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 10. Turkey ─────────────────────────────────────────
        {
            'name': 'Turkey',
            'slug': 'turkey',
            'image': 'https://images.unsplash.com/photo-1524234257241-9e3e1f4e4e6b?w=1200&q=80',
            'description': 'From the domes and minarets of Istanbul to the fairy chimneys of Cappadocia \u2014 Turkey\u2019s crossroads of Byzantine mosaics, Ottoman tilework, and Anatolian kilim patterns.',
            'regions': [
                {
                    'name': 'Istanbul',
                    'slug': 'istanbul-region',
                    'image': 'https://images.unsplash.com/photo-1524234257241-9e3e1f4e4e6b?w=900&q=80',
                    'description': 'The city on two continents \u2014 where East meets West.',
                    'cities': [
                        {'name': 'Istanbul', 'slug': 'istanbul', 'image': 'https://images.unsplash.com/photo-1524234257241-9e3e1f4e4e6b?w=900&q=80', 'description': 'Hagia Sophia, Blue Mosque, and Grand Bazaar splendor.', 'featured': True},
                    ],
                },
                {
                    'name': 'Central Anatolia',
                    'slug': 'central-anatolia',
                    'image': 'https://images.unsplash.com/photo-1641128324972-af3212f0f6bd?w=900&q=80',
                    'description': 'Cappadocia\u2019s surreal landscapes and underground cities.',
                    'cities': [
                        {'name': 'Cappadocia', 'slug': 'cappadocia', 'image': 'https://images.unsplash.com/photo-1641128324972-af3212f0f6bd?w=900&q=80', 'description': 'Fairy chimneys, cave hotels, and sunrise balloons.', 'featured': True},
                        {'name': 'Konya', 'slug': 'konya', 'image': '', 'description': 'City of Rumi, whirling dervishes, and Seljuk tilework.', 'featured': False},
                    ],
                },
                {
                    'name': 'Aegean Region',
                    'slug': 'aegean-region',
                    'image': 'https://images.unsplash.com/photo-1604941909484-7fa3d4e7c1b3?w=900&q=80',
                    'description': 'Ancient Roman ruins and turquoise coastlines.',
                    'cities': [
                        {'name': 'Izmir', 'slug': 'izmir', 'image': 'https://images.unsplash.com/photo-1604941909484-7fa3d4e7c1b3?w=900&q=80', 'description': 'Pearl of the Aegean with Ottoman-era bazaar.', 'featured': True},
                        {'name': 'Ephesus', 'slug': 'ephesus', 'image': '', 'description': 'Library of Celsus and ancient Roman city.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 11. China ──────────────────────────────────────────
        {
            'name': 'China',
            'slug': 'china',
            'image': 'https://images.unsplash.com/photo-1548489687-08f2326fc8c0?w=1200&q=80',
            'description': 'From the Forbidden City\u2019s vermilion walls to Suzhou\u2019s ink-wash gardens \u2014 China\u2019s five-thousand-year tradition of lacquer, silk, and auspicious patterns.',
            'regions': [
                {
                    'name': 'Beijing',
                    'slug': 'beijing-region',
                    'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=900&q=80',
                    'description': 'The imperial capital with the Forbidden City and Great Wall.',
                    'cities': [
                        {'name': 'Beijing', 'slug': 'beijing', 'image': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=900&q=80', 'description': 'Forbidden City, hutong courtyards, and imperial red.', 'featured': True},
                    ],
                },
                {
                    'name': 'Shanghai',
                    'slug': 'shanghai-region',
                    'image': 'https://images.unsplash.com/photo-1545893835-abaa50cbe628?w=900&q=80',
                    'description': 'Art Deco Bund and futuristic Pudong skyline.',
                    'cities': [
                        {'name': 'Shanghai', 'slug': 'shanghai', 'image': 'https://images.unsplash.com/photo-1545893835-abaa50cbe628?w=900&q=80', 'description': 'Bund-era Deco meets 21st-century verticality.', 'featured': True},
                        {'name': 'Suzhou', 'slug': 'suzhou', 'image': '', 'description': 'Venice of the East \u2014 classical gardens and silk.', 'featured': True},
                    ],
                },
                {
                    'name': 'Sichuan',
                    'slug': 'sichuan',
                    'image': 'https://images.unsplash.com/photo-1597157639073-2985dd9e6e25?w=900&q=80',
                    'description': 'Chengdu\u2019s teahouses, Tibetan borderlands, and spicy heritage.',
                    'cities': [
                        {'name': 'Chengdu', 'slug': 'chengdu', 'image': 'https://images.unsplash.com/photo-1597157639073-2985dd9e6e25?w=900&q=80', 'description': 'Panda capital and city of ancient Shu culture.', 'featured': False},
                        {'name': 'Leshan', 'slug': 'leshan', 'image': '', 'description': 'Giant Buddha carved into a riverside cliff.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 12. United Arab Emirates ───────────────────────────
        {
            'name': 'United Arab Emirates',
            'slug': 'uae',
            'image': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1200&q=80',
            'description': 'From Dubai\u2019s golden skylines to Abu Dhabi\u2019s pearl-white mosques \u2014 the UAE\u2019s fusion of Bedouin heritage, Islamic geometry, and ultra-modern luxury.',
            'regions': [
                {
                    'name': 'Dubai',
                    'slug': 'dubai-emirate',
                    'image': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=900&q=80',
                    'description': 'The city of superlatives \u2014 gold, glass, and desert.',
                    'cities': [
                        {'name': 'Dubai', 'slug': 'dubai', 'image': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=900&q=80', 'description': 'Burj Khalifa, gold souk, and opulent interiors.', 'featured': True},
                    ],
                },
                {
                    'name': 'Abu Dhabi',
                    'slug': 'abu-dhabi-emirate',
                    'image': 'https://images.unsplash.com/photo-1597052634311-a09a1a4bbb9b?w=900&q=80',
                    'description': 'The capital emirate \u2014 culture, mosques, and islands.',
                    'cities': [
                        {'name': 'Abu Dhabi', 'slug': 'abu-dhabi', 'image': 'https://images.unsplash.com/photo-1597052634311-a09a1a4bbb9b?w=900&q=80', 'description': 'Sheikh Zayed Grand Mosque \u2014 white marble and gold.', 'featured': True},
                        {'name': 'Al Ain', 'slug': 'al-ain', 'image': '', 'description': 'Garden city and UNESCO desert oasis.', 'featured': False},
                    ],
                },
                {
                    'name': 'Sharjah',
                    'slug': 'sharjah-emirate',
                    'image': 'https://images.unsplash.com/photo-1595297601642-3b8c3a4e5f96?w=900&q=80',
                    'description': 'Cultural capital of the Arab world.',
                    'cities': [
                        {'name': 'Sharjah', 'slug': 'sharjah', 'image': 'https://images.unsplash.com/photo-1595297601642-3b8c3a4e5f96?w=900&q=80', 'description': 'Islamic art, heritage area, and Heart of Sharjah.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 13. Brazil ─────────────────────────────────────────
        {
            'name': 'Brazil',
            'slug': 'brazil',
            'image': 'Indonesia https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=1200&q=80',
            'description': 'From the cobblestone streets of colonial Paraty to Niemeyer\u2019s curving modernism in Bras\u00edlia \u2014 Brazil\u2019s explosion of tropical color, Portuguese azulejos, and Amazonian patterns.',
            'regions': [
                {
                    'name': 'Rio de Janeiro',
                    'slug': 'rio-de-janeiro-state',
                    'image': 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=900&q=80',
                    'description': 'Mountains, beaches, and Carnival spectacle.',
                    'cities': [
                        {'name': 'Rio de Janeiro', 'slug': 'rio-de-janeiro', 'image': 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=900&q=80', 'description': 'Christ the Redeemer, Copacabana, and samba color.', 'featured': True},
                        {'name': 'Paraty', 'slug': 'paraty', 'image': '', 'description': 'Colonial port with whitewashed doors and blue trim.', 'featured': False},
                    ],
                },
                {
                    'name': 'S\u00e3o Paulo',
                    'slug': 'sao-paulo-state',
                    'image': 'https://images.unsplash.com/photo-1576716402245-9b2e1c0a0b2d?w=900&q=80',
                    'description': 'South America\u2019s largest city and art capital.',
                    'cities': [
                        {'name': 'S\u00e3o Paulo', 'slug': 'sao-paulo', 'image': 'https://images.unsplash.com/photo-1576716402245-9b2e1c0a0b2d?w=900&q=80', 'description': 'Concrete brutalism, street murals, andMASP.', 'featured': True},
                        {'name': 'Campos do Jord\u00e3o', 'slug': 'campos-do-jordao', 'image': '', 'description': 'Alpine-style mountain resort town.', 'featured': False},
                    ],
                },
                {
                    'name': 'Bahia',
                    'slug': 'bahia',
                    'image': 'https://images.unsplash.com/photo-1597223559814-1af3b2efa7a7?w=900&q=80',
                    'description': 'Afro-Brazilian culture, Pelourinho, and tropical coast.',
                    'cities': [
                        {'name': 'Salvador', 'slug': 'salvador', 'image': 'https://images.unsplash.com/photo-1597223559814-1af3b2efa7a7?w=900&q=80', 'description': 'Pastel colonial facades and African heritage.', 'featured': True},
                    ],
                },
            ],
        },
        # ── 14. Australia ──────────────────────────────────────
        {
            'name': 'Australia',
            'slug': 'australia',
            'image': 'https://images.unsplash.com/photo-1524121758962-ddde1ab4e085?w=1200&q=80',
            'description': 'From Sydney\u2019s harbourside modernism to the ochre deserts of the Outback \u2014 Australia\u2019s blend of Aboriginal dot art, coastal living, and bold contemporary design.',
            'regions': [
                {
                    'name': 'New South Wales',
                    'slug': 'new-south-wales',
                    'image': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=900&q=80',
                    'description': 'Sydney and its stunning coastline and harbour.',
                    'cities': [
                        {'name': 'Sydney', 'slug': 'sydney', 'image': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=900&q=80', 'description': 'Opera House, Harbour Bridge, and beachside living.', 'featured': True},
                        {'name': 'Byron Bay', 'slug': 'byron-bay', 'image': '', 'description': 'Bohemian surf town at Australia\u2019s easternmost point.', 'featured': True},
                    ],
                },
                {
                    'name': 'Victoria',
                    'slug': 'victoria',
                    'image': 'https://images.unsplash.com/photo-1548549019-474a4c6225f6?w=900&q=80',
                    'description': 'Melbourne \u2014 Australia\u2019s coffee and laneway art capital.',
                    'cities': [
                        {'name': 'Melbourne', 'slug': 'melbourne', 'image': 'https://images.unsplash.com/photo-1548549019-474a4c6225f6?w=900&q=80', 'description': 'Street art, Victorian architecture, and hidden bars.', 'featured': True},
                    ],
                },
                {
                    'name': 'Queensland',
                    'slug': 'queensland',
                    'image': 'https://images.unsplash.com/photo-1524121758962-ddde1ab4e085?w=900&q=80',
                    'description': 'Tropical north, Great Barrier Reef, and rainforest.',
                    'cities': [
                        {'name': 'Brisbane', 'slug': 'brisbane', 'image': '', 'description': 'River city with subtropical outdoor lifestyle.', 'featured': False},
                        {'name': 'Cairns', 'slug': 'cairns', 'image': '', 'description': 'Gateway to the Great Barrier Reef and Daintree.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 15. Netherlands ────────────────────────────────────
        {
            'name': 'Netherlands',
            'slug': 'netherlands',
            'image': 'https://images.unsplash.com/photo-1534351590666-13e3e96c5017?w=1200&q=80',
            'description': 'From the canal houses of Amsterdam to the geometric precision of De Stijl \u2014 Dutch design mastery in Delftware blue, golden-age interiors, and minimalist contemporary aesthetics.',
            'regions': [
                {
                    'name': 'North Holland',
                    'slug': 'north-holland',
                    'image': 'https://images.unsplash.com/photo-1534351590666-13e3e96c5017?w=900&q=80',
                    'description': 'Amsterdam\u2019s canals, gabled facades, and world-class museums.',
                    'cities': [
                        {'name': 'Amsterdam', 'slug': 'amsterdam', 'image': 'https://images.unsplash.com/photo-1534351590666-13e3e96c5017?w=900&q=80', 'description': 'Canal ring, gabled brick houses, and Rijksmuseum.', 'featured': True},
                        {'name': 'Haarlem', 'slug': 'haarlem', 'image': '', 'description': 'Medieval city with Frans Hals and Teylers Museum.', 'featured': False},
                    ],
                },
                {
                    'name': 'South Holland',
                    'slug': 'south-holland',
                    'image': 'https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=900&q=80',
                    'description': 'The Hague, Rotterdam, and Delft \u2014 modern and classic.',
                    'cities': [
                        {'name': 'Rotterdam', 'slug': 'rotterdam', 'image': 'https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=900&q=80', 'description': 'Bold modern architecture rebuilt after WWII.', 'featured': True},
                        {'name': 'The Hague', 'slug': 'the-hague', 'image': '', 'description': 'Royal city and home of Vermeer\u2019s Girl with a Pearl Earring.', 'featured': True},
                        {'name': 'Delft', 'slug': 'delft', 'image': '', 'description': 'Birthplace of Delftware blue-and-white ceramics.', 'featured': False},
                    ],
                },
                {
                    'name': 'Utrecht',
                    'slug': 'utrecht-region',
                    'image': 'https://images.unsplash.com/photo-1561258363-1d1b6c5e2e2f?w=900&q=80',
                    'description': 'Central province of canals, DOM tower, and design universities.',
                    'cities': [
                        {'name': 'Utrecht', 'slug': 'utrecht', 'image': 'https://images.unsplash.com/photo-1561258363-1d1b6c5e2e2f?w=900&q=80', 'description': 'Dom Tower, sunken canals, and Rietveld design heritage.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 16. Thailand ───────────────────────────────────────
        {
            'name': 'Thailand',
            'slug': 'thailand',
            'image': 'https://images.unsplash.com/photo-1563492065-1a3ddb2dab52?w=1200&q=80',
            'description': 'From the gilded temples of Bangkok to the teak houses of Chiang Mai \u2014 Thailand\u2019s rich tradition of gold-leaf Buddhist art, silk weaving, and tropical botanical motifs.',
            'regions': [
                {
                    'name': 'Bangkok',
                    'slug': 'bangkok-region',
                    'image': 'https://images.unsplash.com/photo-1563492065-1a3ddb2dab52?w=900&q=80',
                    'description': 'The capital of temples, markets, and gilded palaces.',
                    'cities': [
                        {'name': 'Bangkok', 'slug': 'bangkok', 'image': 'https://images.unsplash.com/photo-1563492065-1a3ddb2dab52?w=900&q=80', 'description': 'Grand Palace, Wat Arun, and floating markets.', 'featured': True},
                    ],
                },
                {
                    'name': 'Northern Thailand',
                    'slug': 'northern-thailand',
                    'image': 'https://images.unsplash.com/photo-1598935858628-8f7be85e4e89?w=900&q=80',
                    'description': 'Lanna kingdom heritage, hill tribes, and misty mountains.',
                    'cities': [
                        {'name': 'Chiang Mai', 'slug': 'chiang-mai', 'image': 'https://images.unsplash.com/photo-1598935858628-8f7be85e4e89?w=900&q=80', 'description': 'Lanna capital of teak temples and night bazaars.', 'featured': True},
                        {'name': 'Pai', 'slug': 'pai', 'image': '', 'description': 'Bohemian mountain town in Mae Hong Son loop.', 'featured': False},
                    ],
                },
                {
                    'name': 'Southern Thailand',
                    'slug': 'southern-thailand',
                    'image': 'https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=900&q=80',
                    'description': 'Limestone cliffs, tropical islands, and Andaman coast.',
                    'cities': [
                        {'name': 'Phuket', 'slug': 'phuket', 'image': 'https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=900&q=80', 'description': 'Pearl of the Andaman \u2014 Sino-Portuguese architecture.', 'featured': True},
                        {'name': 'Krabi', 'slug': 'krabi', 'image': '', 'description': 'Limestone karsts and Railay Beach.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 17. Greece ─────────────────────────────────────────
        {
            'name': 'Greece',
            'slug': 'greece',
            'image': 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=1200&q=80',
            'description': 'From the whitewashed domes of Santorini to the marble columns of the Acropolis \u2014 Greece\u2019s timeless aesthetic of Aegean blue, classical proportion, and Mediterranean simplicity.',
            'regions': [
                {
                    'name': 'Attica',
                    'slug': 'attica',
                    'image': 'https://images.unsplash.com/photo-1555993539-1732b0258235?w=900&q=80',
                    'description': 'Athens \u2014 the cradle of Western civilization.',
                    'cities': [
                        {'name': 'Athens', 'slug': 'athens', 'image': 'https://images.unsplash.com/photo-1555993539-1732b0258235?w=900&q=80', 'description': 'Acropolis, Plaka, and neoclassical facades.', 'featured': True},
                    ],
                },
                {
                    'name': 'Cyclades',
                    'slug': 'cyclades',
                    'image': 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=900&q=80',
                    'description': 'White-and-blue island archipelago in the Aegean Sea.',
                    'cities': [
                        {'name': 'Santorini', 'slug': 'santorini', 'image': 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=900&q=80', 'description': 'Caldera cliffs, blue domes, and Aegean sunsets.', 'featured': True},
                        {'name': 'Mykonos', 'slug': 'mykonos', 'image': '', 'description': 'Windmills, narrow lanes, and cosmopolitan charm.', 'featured': True},
                        {'name': 'Naxos', 'slug': 'naxos', 'image': '', 'description': 'Largest Cycladic island with Venetian castles.', 'featured': False},
                    ],
                },
                {
                    'name': 'Crete',
                    'slug': 'crete',
                    'image': 'https://images.unsplash.com/photo-1604561447191-2c3a3e5a1e1c?w=900&q=80',
                    'description': 'Minoan palaces, Venetian harbors, and rugged mountains.',
                    'cities': [
                        {'name': 'Chania', 'slug': 'chania', 'image': 'https://images.unsplash.com/photo-1604561447191-2c3a3e5a1e1c?w=900&q=80', 'description': 'Venetian lighthouse and old harbor town.', 'featured': True},
                        {'name': 'Heraklion', 'slug': 'heraklion', 'image': '', 'description': 'Gateway to Knossos Minoan palace.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 18. Mexico ─────────────────────────────────────────
        {
            'name': 'Mexico',
            'slug': 'mexico',
            'image': 'https://images.unsplash.com/photo-1518105779142-d975f22f1b5a?w=1200&q=80',
            'description': 'From the pyramids of Teotihuacan to the pink facades of San Miguel de Allende \u2014 Mexico\u2019s vivid palette of Talavera tile, Mayan motifs, and Baroque churches.',
            'regions': [
                {
                    'name': 'Mexico City',
                    'slug': 'mexico-city-region',
                    'image': 'https://images.unsplash.com/photo-1518105779142-d975f22f1b5a?w=900&q=80',
                    'description': 'Tenochtitl\u00e1n to megacity \u2014 Aztec ruins and Baroque cathedrals.',
                    'cities': [
                        {'name': 'Mexico City', 'slug': 'mexico-city', 'image': 'https://images.unsplash.com/photo-1518105779142-d975f22f1b5a?w=900&q=80', 'description': 'Z\u00f3calo, Frida Kahlo\u2019s Casa Azul, and Museo Soumaya.', 'featured': True},
                    ],
                },
                {
                    'name': 'Guanajuato',
                    'slug': 'guanajuato-region',
                    'image': 'https://images.unsplash.com/photo-1473773508845-188df298d2d1?w=900&q=80',
                    'description': 'Colonial silver-mining towns with kaleidoscopic facades.',
                    'cities': [
                        {'name': 'San Miguel de Allende', 'slug': 'san-miguel-de-allende', 'image': 'https://images.unsplash.com/photo-1473773508845-188df298d2d1?w=900&q=80', 'description': 'UNESCO colonial gem with pink and ochre streets.', 'featured': True},
                        {'name': 'Guanajuato City', 'slug': 'guanajuato-city', 'image': '', 'description': 'Underground tunnels and rainbow-colored alleys.', 'featured': True},
                    ],
                },
                {
                    'name': 'Yucat\u00e1n',
                    'slug': 'yucatan',
                    'image': 'https://images.unsplash.com/photo-1568917977021-ad88f22a8c7d?w=900&q=80',
                    'description': 'Mayan ruins, colonial cities, and cenote landscapes.',
                    'cities': [
                        {'name': 'M\u00e9rida', 'slug': 'merida', 'image': 'https://images.unsplash.com/photo-1568917977021-ad88f22a8c7d?w=900&q=80', 'description': 'White City with Paseo de Montejo mansions.', 'featured': True},
                        {'name': 'Valladolid', 'slug': 'valladolid-mx', 'image': '', 'description': 'Yellow-walled colonial town near Chich\u00e9n Itz\u00e1.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 19. Russia ─────────────────────────────────────────
        {
            'name': 'Russia',
            'slug': 'russia',
            'image': 'https://images.unsplash.com/photo-1547448415-e9f5b28e570d?w=1200&q=80',
            'description': 'From the onion domes of St. Petersburg to the constructivist avant-garde of Moscow \u2014 Russia\u2019s opulent imperial palaces, iconography, and bold geometric design.',
            'regions': [
                {
                    'name': 'Moscow',
                    'slug': 'moscow-region',
                    'image': 'https://images.unsplash.com/photo-1513326738677-b964603b136d?w=900&q=80',
                    'description': 'Red Square, the Kremlin, and Stalinist skyscrapers.',
                    'cities': [
                        {'name': 'Moscow', 'slug': 'moscow', 'image': 'https://images.unsplash.com/photo-1513326738677-b964603b136d?w=900&q=80', 'description': 'St. Basil\u2019s, Metro palaces, and Bolshoi Theatre.', 'featured': True},
                    ],
                },
                {
                    'name': 'St. Petersburg',
                    'slug': 'st-petersburg-region',
                    'image': 'https://images.unsplash.com/photo-1556610961-2fecc5927175?w=900&q=80',
                    'description': 'Peter the Great\u2019s window to the West \u2014 canals and palaces.',
                    'cities': [
                        {'name': 'St. Petersburg', 'slug': 'st-petersburg', 'image': 'https://images.unsplash.com/photo-1556610961-2fecc5927175?w=900&q=80', 'description': 'Hermitage, Peterhof fountains, and amber rooms.', 'featured': True},
                        {'name': 'Pushkin', 'slug': 'pushkin', 'image': '', 'description': 'Tsarskoye Selo \u2014 Catherine Palace and golden amber.', 'featured': False},
                    ],
                },
                {
                    'name': 'Golden Ring',
                    'slug': 'golden-ring',
                    'image': 'https://images.unsplash.com/photo-1547448415-e9f5b28e570d?w=900&q=80',
                    'description': 'Ancient medieval towns northeast of Moscow.',
                    'cities': [
                        {'name': 'Suzdal', 'slug': 'suzdal', 'image': 'https://images.unsplash.com/photo-1547448415-e9f5b28e570d?w=900&q=80', 'description': 'Open-air museum of wooden churches and kremlins.', 'featured': False},
                        {'name': 'Yaroslavl', 'slug': 'yaroslavl', 'image': '', 'description': 'UNESCO city with 17th-century frescoes.', 'featured': False},
                    ],
                },
            ],
        },
        # ── 20. Egypt ──────────────────────────────────────────
        {
            'name': 'Egypt',
            'slug': 'egypt',
            'image': 'https://images.unsplash.com/photo-1572252009286-268acec5ca0a?w=1200&q=80',
            'description': 'From the temples of Luxor to the bazaars of Cairo \u2014 Egypt\u2019s five-thousand-year heritage of hieroglyphs, Islamic geometry, and desert-colored palettes.',
            'regions': [
                {
                    'name': 'Greater Cairo',
                    'slug': 'greater-cairo',
                    'image': 'https://images.unsplash.com/photo-1572252009286-268acec5ca0a?w=900&q=80',
                    'description': 'Pyramids, medieval Islamic Cairo, and the Nile.',
                    'cities': [
                        {'name': 'Cairo', 'slug': 'cairo', 'image': 'https://images.unsplash.com/photo-1572252009286-268acec5ca0a?w=900&q=80', 'description': 'Pyramids of Giza, Khan el-Khalili, and mosque minarets.', 'featured': True},
                    ],
                },
                {
                    'name': 'Upper Egypt',
                    'slug': 'upper-egypt',
                    'image': 'https://images.unsplash.com/photo-1601922153326-1ef0c4a4b1a0?w=900&q=80',
                    'description': 'Valley of the Kings, Karnak, and Nile temples.',
                    'cities': [
                        {'name': 'Luxor', 'slug': 'luxor', 'image': 'https://images.unsplash.com/photo-1601922153326-1ef0c4a4b1a0?w=900&q=80', 'description': 'World\u2019s greatest open-air museum \u2014 temples and tombs.', 'featured': True},
                        {'name': 'Aswan', 'slug': 'aswan', 'image': '', 'description': 'Nubian culture and Philae Temple on the Nile.', 'featured': False},
                    ],
                },
                {
                    'name': 'Alexandria',
                    'slug': 'alexandria-region',
                    'image': 'https://images.unsplash.com/photo-1599751449628-9d4a93f1e3c7?w=900&q=80',
                    'description': 'Mediterranean port founded by Alexander the Great.',
                    'cities': [
                        {'name': 'Alexandria', 'slug': 'alexandria', 'image': 'https://images.unsplash.com/photo-1599751449628-9d4a93f1e3c7?w=900&q=80', 'description': 'Bibliotheca, Corniche, and Greco-Roman heritage.', 'featured': True},
                    ],
                },
            ],
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):
        created_counts = {'countries': 0, 'regions': 0, 'cities': 0}

        for i, cdata in enumerate(self.COUNTRIES):
            country, created = Country.objects.get_or_create(
                slug=cdata['slug'],
                defaults={
                    'name': cdata['name'],
                    'image': cdata['image'],
                    'description': cdata['description'],
                    'sort_order': i,
                    'is_active': True,
                }
            )
            if created:
                created_counts['countries'] += 1

            for j, rdata in enumerate(cdata['regions']):
                region, created = Region.objects.get_or_create(
                    slug=rdata['slug'],
                    defaults={
                        'country': country,
                        'name': rdata['name'],
                        'image': rdata.get('image', ''),
                        'description': rdata.get('description', ''),
                        'sort_order': j,
                        'is_active': True,
                    }
                )
                if created:
                    created_counts['regions'] += 1

                for k, city_data in enumerate(rdata['cities']):
                    city, created = City.objects.get_or_create(
                        slug=city_data['slug'],
                        defaults={
                            'region': region,
                            'name': city_data['name'],
                            'image': city_data.get('image', ''),
                            'description': city_data.get('description', ''),
                            'sort_order': k,
                            'is_active': True,
                            'featured': city_data.get('featured', False),
                        }
                    )
                    if created:
                        created_counts['cities'] += 1

        # ── Associate existing products with cities ──────────
        all_products = list(Product.objects.all())
        all_cities = list(City.objects.all())

        if all_products and all_cities:
            # Distribute products across cities — each product gets 1-3 cities
            import random
            random.seed(42)
            for product in all_products:
                num_cities = random.randint(1, min(3, len(all_cities)))
                chosen = random.sample(all_cities, num_cities)
                product.cities.set(chosen)

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded {created_counts["countries"]} countries, '
                f'{created_counts["regions"]} regions, '
                f'{created_counts["cities"]} cities. '
                f'Associated {len(all_products)} products with cities.'
            )
        )
