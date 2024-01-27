import os
import time
import geocoder
import traceback
import googlemaps
from geopy import distance
from dotenv import load_dotenv

from sqlalchemy import and_
from hera import Session, create
from hera.enum import CategoryType
from hera.schema import GoogleOrganizer, Category, GoogleOrganizerCategorization, Organizer

from progress import progress_decorator

load_dotenv()
RADIUS = 20000
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')


#   Legge i file di input, gestisce le query a Google
def start_athena() -> int:
    try:
        cities, categories = get_input_files()
        main_list = []
        for category in categories:
            for city in cities:
                main_list.append([category, city])
        query_google_maps(main_list, 'ATHENA')
    except Exception as e:
        traceback.print_exception(e)
        return 1
    return 0


def get_input_files() -> (list[str], list[str]):
    cities = []
    with open('./files/athena_inputs/cities.txt', 'r', encoding='utf-8') as file:
        for riga in file:
            cities.append(riga.strip())
    categories = []
    with open('./files/athena_inputs/categories.txt', 'r', encoding='utf-8') as file:
        for riga in file:
            categories.append(riga.strip())
    return cities, categories


def get_category(name: str) -> Category:
    with Session() as session:
        return session.query(Category).filter(and_(
            Category.name == name, Category.type == CategoryType.GOOGLE
        )).first()


def exists_organizer(google_id: str):
    with Session() as session:
        return not session.query(GoogleOrganizer).filter(
            GoogleOrganizer.google_id == google_id
        ).first() is None


def save_results(organizers: list[dict]) -> None:
    for o in organizers:
        lat = o['geometry']['location']['lat']
        lon = o['geometry']['location']['lng']
        organizer = create(GoogleOrganizer, {
            'name': o['name'],
            'rating': o['rating'] if 'rating' in o else None,
            'google_id': o['place_id'],
            'city': o['city'],
            'address': o['formatted_address'],
            'n_voters': o['user_ratings_total'] if 'user_ratings_total' in o else None,
            'latitude': lat,
            'longitude': lon
        })
        create(Organizer, {'google_organizer_id': organizer.id})
        for category in o['types']:
            c = get_category(category)
            if not c:
                c = create(Category, {'name': category,
                           'type': CategoryType.GOOGLE})
            create(GoogleOrganizerCategorization, {
                'google_organizer_id': organizer.id,
                'category_id': c.id
            })


# Resituisce la latitudine e la longitudine nel formato utile alla query di Google
def get_lat_long_by_city(city: str) -> str:
    location = geocoder.osm(city)
    if location.ok:
        return [location.latlng[0], location.latlng[1]]
    else:
        raise Exception(f'Not found latitude and longitude from city {city}')


# Elaborazione di una singola query di Google, verifica dei risultati e scrittura dei dati
@progress_decorator
def query_google_maps(
    item: tuple
) -> bool:
    category, city = item
    print(f"Ricerca avviata con le parole chiave {category} e la città {city}")

    trash, taken, newResults = 0, 0, []
    gmaps = googlemaps.Client(key=API_KEY)
    coordinates = get_lat_long_by_city(city)
    params = {
        'location': coordinates,
        'query': category,
        'radius': RADIUS
    }
    print('Query Google Maps -> ' + str(params))
    while True:
        results = gmaps.places(**params)
        for g in results['results']:
            if add_gestore(newResults, g, coordinates):
                taken += 1
            else:
                trash += 1
        time.sleep(2)
        if 'next_page_token' in results:
            params['page_token'] = results['next_page_token']
        else:
            break
    save_results(newResults)
    print('Elementi trovati: ' + str(taken) +
          ' Elementi scartati: ' + str(trash))


# Inserisce un gestore nella lista risultante se vengono superati tutti i controlli di coerenza
def add_gestore(
    newResults: list[dict], gestore: dict, coo: list
) -> bool:
    if not 'name' in gestore:
        print('\033[91mSCARTATO: Nome non presente\033[0m')
        return False
    lat = gestore['geometry']['location']['lat']
    lon = gestore['geometry']['location']['lng']
    if geo_check(coo, [lat, lon]):
        print('\033[91mSCARTATO: Troppo lontano dalla città ricercata\033[0m')
        return False
    if exists_organizer(gestore['place_id']):
        print('\033[91mSCARTATO: Già presente sul db\033[0m')
        return False
    place = geocoder.osm([lat, lon], method='reverse')
    if place.ok and (place.city or place.town or place.village):
        gestore['city'] = place.city if place.city else \
            place.town if place.town else place.village
    else:
        print('\033[91mSCARTATO: Città non presente\033[0m')
        return False
    newResults.append(gestore)
    return True


# Calcola la distanza in km tra due punti geografici usando latitudine e longitudine
def geo_check(city: str, gestore: list) -> bool:
    coord1 = (city[0], city[1])
    coord2 = (gestore[0], gestore[1])
    return distance.geodesic(coord1, coord2).meters > RADIUS
