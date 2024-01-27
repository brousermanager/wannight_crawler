import difflib
import re
import math
import time
from functools import wraps

bar_length = 50


def print_process_bar(indice, elemento, total):
    """Function to print the process bar.

    Args:
        indice (int): _description_
        elemento (int): _description_
        total (int): _description_
    """
    progress = indice + 1
    percentuale = (progress / total) * 100
    filled_length = int(bar_length * progress / total)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    print('\r[{0}] {1}/{2} - {3:.1f}%'.format(bar, progress,
          total, percentuale), end=f' {elemento}\n')


def exponential_backoff(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sleep_time = 1
        while True:
            try:
                result = func(*args, **kwargs)
                # reset sleep_time to 1 if no exception was raised
                sleep_time = 1
                return result
            except Exception as e:
                print(
                    f"Encountered error: {e}. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
                sleep_time *= 2  # exponentially increase sleep_time for next retry
    return wrapper


#   SCRAPE EVENTS
def extract_page_name(url):
    # Match the last segment of the URL path using regex
    match = re.search(r'\/([^\/]*)$', url)

    # Return the matched segment (or None if no match found)
    return match.group(1) if match else None

# n is km distance from the center
# retrns the coordinates of the square that contains the circle of radius n
def coordinate_dopo_n_km(latitudine, longitudine, n):
    raggio_terrestre = 6371  # Raggio della Terra in chilometri
    delta_lat = (n / raggio_terrestre) * (180 / math.pi)
    delta_lon = (n / raggio_terrestre) * (180 / math.pi) / \
        math.cos(latitudine * math.pi / 180)
    return latitudine + delta_lat, latitudine - delta_lat, longitudine + delta_lon, longitudine - delta_lon


# function that check if lat, lon are in the square
def check_if_in_square(lat, lon, lat1, lat2, lon1, lon2):
    if lat1 <= lat <= lat2 and lon1 <= lon <= lon2:
        return True
    else:
        return False


# check if given two sets of coordinates are in square of radius n using the functions above
def check_if_are_close(lat_original, lon_original, lat_event, lon_event, n):
    # get the coordinates of the square which contains the circle of radius n
    # approximate radius of Earth in km
    R = 6371

    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(
        math.radians, [float(lat_original), float(lon_original), float(lat_event), float(lon_event)])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance <= n


def check_similarity(string, string_list, threshold=0.9):
    flag = False
    for item in string_list:
        similarity = difflib.SequenceMatcher(None, string, item).ratio()
        if similarity >= threshold:

            flag = True
        else:
            continue

    if flag == False:

        return False
    else:

        return True
