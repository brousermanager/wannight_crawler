import os
import csv
import random
import traceback

from hera import Session, create
from hera.schema import FacebookOrganizer

from .FacebookCrawler import FacebookCrawler


def start_dioniso(flagPast: bool) -> int :
    try :
        suggestions = get_suggestions_from_csv()
        if suggestions:
            for suggestion in suggestions:
                if not exists_facebook_organizer(suggestion['url']):
                    create(FacebookOrganizer, {'url': suggestion['url']})

        initial_list = get_organizer_with_fb_page()
    
        sub_list_without_names = [g for g in initial_list if g.name is None or g.name == '']
        sub_list_with_names = [g for g in initial_list if g not in sub_list_without_names]
        random.shuffle(sub_list_without_names)
        random.shuffle(sub_list_with_names)
        initial_list = sub_list_with_names + sub_list_without_names

        crawler = FacebookCrawler(initial_list, flagPast)
        crawler.start()
        del crawler
    except Exception as e :
        traceback.print_exception(e)
        return 1
    return 0


def get_organizer_with_fb_page() -> list:
    with Session() as session:
        return session.query(FacebookOrganizer).all()


def get_suggestions_from_csv():
    filename = 'new_suggestions.csv'
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as file_csv:
        reader = csv.DictReader(file_csv)
        return [riga for riga in reader]


def exists_facebook_organizer(url):
    with Session() as session:
        return not session.query(FacebookOrganizer).filter(
            FacebookOrganizer.url == url
        ).scalar() is None
