import os
import json
import geocoder
import traceback
from modules.HERA.HERA import executeQuery
from utils import print_process_bar

def create_organizzer_by_overpass(lista_elementi) :
    num_elements = len(lista_elementi)
    for index, elemento in enumerate(lista_elementi) :
        try :
            name, amenity, coordinates, fb = extraction_info(elemento)
            print_process_bar(index, name, num_elements)
            if name != None and coordinates != None :
                city = get_city_name(coordinates[0], coordinates[1])
                query = 'CALL inserisci_organizzatore_from_overpass("%s", "%s", "%s", "%s", %s, %s);' % (
                    name.replace('"', '\'\''), amenity.replace('"', '\'\''), coordinates[0], coordinates[1],
                        f"\"{fb}\"" if fb != None else 'NULL',
                                f"\"{city}\"" if city != None else 'NULL')
                executeQuery(query)
        except Exception as e :
            traceback.print_exception(e)
            pass

def extraction_info(organizer) :
    name, amenity, coordinates, fb = None, None, None, None
    if 'properties' in organizer and 'geometry' in organizer :
        if 'name' in organizer['properties'] and 'coordinates' in organizer['geometry'] and 'amenity' in organizer['properties'] :
            name = organizer['properties']['name']
            amenity = organizer['properties']['amenity']
            coordinates = organizer['geometry']['coordinates']
            if 'contact:facebook' in organizer['properties'] :
                fb = organizer['properties']['contact:facebook']
            elif 'website' in organizer['properties'] and 'facebook' in organizer['properties']['website'] :
                fb = organizer['properties']['website']
    return name, amenity, coordinates, fb

def get_city_name(latitude, longitude) :
    location = geocoder.arcgis([latitude, longitude], method='reverse')
    if location.ok and location.city != '' :
        return location.city
    else :
        return None

def open_folder(cartella) :
    if not os.path.exists(cartella):
        print(f"La cartella '{cartella}' non esiste.")
        return
    for file in os.listdir(cartella) :
        with open(f"{cartella}{file}", 'rb') as f :
            create_organizzer_by_overpass(json.load(f)['features'])

open_folder('modules/ATHENA/over_pass_files/')
