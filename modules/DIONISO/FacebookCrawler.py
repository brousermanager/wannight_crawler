import re
import os
import math
import json
import datetime
import warnings
import traceback
import time
from bs4 import BeautifulSoup

from modules.AFRODITE.AFRODITE import image_uploader
from modules.DIONISO.EventsDionisoExtraction import EventExtractor
from utils.json import extractEventsFromJson, extractJsonFromHtml, extract_object
from .FacebookRequests import __makeFirstRequest__, __analyzeFirstRequest__, __makeEventRequest__, __makeFollowersRequest__


from .fetch_path import find_values
from progress import progress_decorator

from sqlalchemy import and_
from hera import Session, create, update
from hera.enum import CategoryType
from hera.schema import Organizer, FacebookOrganizer, Event, EventArrangement, EventCategorization, Category


MAXIMUM_RECURSION_LEVEL = 5
MAXIMUM_DISTANCE = 200


# TODO: A che serve questo? # toglie i warning
warnings.filterwarnings("ignore")


class FacebookCrawler:

    def __init__(self, organizers: list[FacebookOrganizer], flagPast: bool = False, lat: int = None, lon: int = None, recursion_number: int = 0):
        self.organizers = organizers
        self.flagPast = flagPast
        self.lat = lat
        self.lon = lon
        self.recursion_number = recursion_number
        self.cookies = {
            'datr': '4dRWY85ekoWoUSRvzBlt441L',
            'dpr': '2',
            'sb': 'NtVWYyXlr7LM1vsjdm0rcYnL',
            'wd': '1200x902'
        }
        self.headers = {
            'host': 'www.facebook.com',
            'viewport': '1680',
            'secchua': '"Not;A=Brand";v="99", "Chromium";v="106"',
            'seccamobile': '?0',
            'secuaplatform': '"macOS"',
            'colorscheme': 'light',
            'upgradeinsecurerequests': '1',
            'useragent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.62 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'secfetchsite': 'none',
            'secfetchmode': 'navigate',
            'secfetchuser': '"?1"',
            'secfetchdest': 'document',
            'acceptlanguage': 'en-GB,en-US;q=0.9,en;q=0.8',
            'connectio': 'close'
        }


    # TODO: Ci sono altri modi per calcolare la distanza geografica in athena
    # Credo che questa funzione sia stata ripetuta altrove, non ricordo dove
    def coordinate_dopo_n_km(latitudine, longitudine, n):
        raggio_terrestre = 6371  # Raggio della Terra in km
        delta_lat = (n / raggio_terrestre) * (180 / math.pi)
        delta_lon = (n / raggio_terrestre) * (180 / math.pi) / math.cos(latitudine * math.pi / 180)
        return latitudine + delta_lat, latitudine - delta_lat, longitudine + delta_lon, longitudine - delta_lon

    def start(self):
        fetch_fb_page(self.organizers, f"DIONISO_{self.recursion_number}", self)

    def process(self, organizer: FacebookOrganizer) -> None:
        time.sleep(1)
        try:
            content = __makeFirstRequest__(self.cookies, self.headers, organizer.url)
        except:
            print('Errore con la prima richiesta per ' + organizer.url)
            return None


        # make sure in content is present the string "Puglia"
        parameters = __analyzeFirstRequest__(content, organizer.url)
        if parameters != None:
            print('PARAMETRI: ' + str(parameters))
            upcomigEvents = EventExtractor(True)

            if self.flagPast == True:
                pastEvents = EventExtractor(False)
            else:
                pastEvents = None

            if parameters['name'] == None:
                print('Non trovato il parametro name per ' + organizer.name)
                return None

            if parameters['loginNeed'] == False:
                upcomigEvents.loginIsNotNedeed(self.cookies, self.headers, parameters)
                
                if pastEvents != None:
                    pastEvents.loginIsNotNedeed(self.cookies, self.headers, parameters)
                self.loginNotNeeded(parameters, upcomigEvents, pastEvents)
            else:
                self.loginNeeded(parameters, upcomigEvents, pastEvents)

            if upcomigEvents.stringa != None:
                print('Estrazione degli eventi futuri...')
                self.eventExtraction(parameters, True, upcomigEvents)

                if len(upcomigEvents.listEvents) > 0:
                    self.httpRequestEvent(organizer, upcomigEvents)

            if pastEvents != None and pastEvents.stringa != None:
                print('Estrazione degli eventi passati...')
                self.eventExtraction(parameters, False, pastEvents)

                if pastEvents != None and len(pastEvents.listEvents) > 0:
                    self.httpRequestEvent(organizer, pastEvents)

    def loginNotNeeded(self, parameters: dict, upcomigEvents: EventExtractor, pastEvents: EventExtractor) -> None:
        print('Login non necessario...')
        if parameters['lsd'] == None or parameters['jazoest'] == None:
            print('Parametri mancanti! =(')
            return # TODO e qui che cazzo torna? 
        # TODO Ma qui?? Queste stringhe statiche?

        parameters['docIdPresentEvents'] = str(5343523095766906)
        parameters['docIdPastEvents'] = str(5552939301434068)

        try:
            upcomigEvents.__makeEventsRequest__(parameters)
            time.sleep(1)
            upcomigEvents.listEvents = extractEventsFromJson(upcomigEvents.stringa, True)
        except Exception as e:
            print(e)
            time.sleep(2)
            upcomigEvents.stringa = None

        if pastEvents != None:
            try:
                pastEvents.__makeEventsRequest__(parameters)
                time.sleep(1)
                pastEvents.listEvents = extractEventsFromJson(pastEvents.stringa, False)
            except Exception as e:
                print(e)
                time.sleep(2)
                pastEvents.stringa = None

    def loginNeeded(self, parameters: dict, upcomigEvents: EventExtractor, pastEvents: EventExtractor) -> None:
        print('Login necessario...')
        upcomigEvents.listEvents = []
        try:
            upcomigEvents.__logInNeededApiRequest__(parameters)
        except:
            print('Nessun evento futuro')
            upcomigEvents.stringa = None
        if pastEvents != None:
            pastEvents.listEvents = []
            try:
                pastEvents.__logInNeededApiRequest__(parameters)
            except:
                print('Nessun evento passato')
                pastEvents.stringa = None

    def eventExtraction(self, parameters: dict, flag: bool, eventsObj) -> None:
        stringaProva = extractJsonFromHtml(str(BeautifulSoup(eventsObj.stringa)))
        for each in stringaProva:
            each = json.dumps(each)
            listaEventiPast = extractEventsFromJson(each, flag)
            eventsObj.listEvents.extend(listaEventiPast)

        if eventsObj.stringa != None:
            eventsObj.listEvents.extend(self.__extractEvents__(eventsObj.stringa, parameters))

            if len(eventsObj.listEvents) > 0:
                print('Eventi estratti: ' + str(eventsObj.listEvents))

    def __extractEvents__(self, stringa: str, parameters: dict) -> list:
        eventIDList = []
        if parameters['loginNeed'] == True:
            eventIDList.extend(re.findall(r'"node":\{"__typename":"Event","id":"(.*?)",', stringa))
            
        return eventIDList

    def httpRequestEvent(self, organizer: FacebookOrganizer, eventsObj) -> None:
        for i in eventsObj.listEvents:
            try:
                print('In corso la richiesta per l\'evento ' + i)
                request_content = __makeEventRequest__(self.cookies, self.headers, i)

                if request_content == None:
                    print('Errore nella richiesta dell\'evento ' + i)
                    continue
                else:
                    try:
                        soup = BeautifulSoup(request_content, 'html.parser')
                        event_jsonInformation = extractJsonFromHtml(str(soup), i)
                        self.saveEvent(event_jsonInformation, i, organizer)
                    except Exception as e:
                        traceback.print_exception(e)
                        print('Errore nella richiesta dell\'evento ' + i)
            except Exception as e:
                print('Errore nella funzione httpRequestEvent')

    def saveEvent(self, event: list, id: str, organizer: FacebookOrganizer) -> None:
        try:
            data = find_values(event, id)
            self.insert_evento(data, organizer)
            if self.recursion_number < MAXIMUM_RECURSION_LEVEL:
                exit_nodes = []
                for node in data['exit_nodes']:
                    if data['exit_nodes'].index(node) > 0 and node['url'] and self.check_organizer_existence(node['url']):
                        new_org = create(FacebookOrganizer, {'url': node['url']})
                        exit_nodes.append(new_org)
                        create(Organizer, {'facebook_organizer_id': new_org.id})
                crawler = FacebookCrawler(exit_nodes, self.flagPast)
                crawler.start()
                del crawler
        except Exception as e:
            traceback.print_exception(e)
            print('Errore del salvataggio dei dati per l\'evento ' + id + ' - ' + str(e))

    def insert_evento(self, evento: dict, organizer: FacebookOrganizer):
        flag = False
        if "photo" in evento and evento['photo'] and evento['photo'] != '' and evento['photo'] != []:
            bucket = os.environ.get('BUCKET_EVENTI')
            hash_code = str(hash(f"{evento['photo']}{bucket}"))
            flag = image_uploader(evento['photo'], hash_code, bucket)
        if flag:
            evento['photo'] = hash_code
        else:
            evento['photo'] = False
        e = create(Event, {
            'name': evento['name'],
            'fb_id': evento['fb_id'],
            'latitude': evento['latitude'],
            'longitude': evento['longitude'],
            'date_start': datetime.datetime.fromtimestamp(evento['date_start']),
            'image': evento['photo'] if 'photo' in evento else None,
            'address': evento['address'] if 'address' in evento else None,
            'date_end': datetime.datetime.fromtimestamp(evento['date_end'])
                if 'date_end' in evento else None,
            'location': evento['location'] if 'location' in evento else None,
            'is_online': evento['is_online'] if 'is_online' in evento else None,
            'ticket_url': evento['ticket_url'] if 'ticket_url' in evento else None,
            'description': evento['description'] if 'description' in evento else None,
        })
        with Session() as session:
            if 'categories' in evento:
                for category in evento['categories']:
                    c = session.query(Category).filter(and_(
                        Category.name == category['label'],
                        Category.type == CategoryType.FACEBOOK
                    )).first()
                    if not c:
                        create(Category, {
                            'name': category['label'],
                            'type': CategoryType.FACEBOOK
                        })
                    create(EventCategorization, {'event_id': e.id, 'category_id': c.id})
            if organizer.name is None:
                update(organizer, { 'name': evento['organizer_name'] })
            o = session.query(Organizer).filter(
                Organizer.facebook_organizer_id == organizer.id
            ).first()
            create(EventArrangement, {'event_id': e.id, 'organizer_id': o.id})

    def check_organizer_existence(self, url):
        with Session() as session:
            return session.query(FacebookOrganizer).filter(
                FacebookOrganizer.url == url
            ).first() is None

    def insert_facebook_organizer(self, url):
        fb = create(FacebookOrganizer, {'url': url,})
        create(Organizer, {'facebook_organizer_id': fb.id})
        return fb

    def addCorrelatedPages(self, url):
        # if endswith / -> remove

        profile_followers = []
        if url.endswith('/'):
            url = url[:-1]

        prefix = '/following'
        content = __makeFollowersRequest__(self.cookies, self.headers, url+prefix)
        '''
        stringaContent=str(BeautifulSoup(content, 'html.parser'))
        #se non è presente la stringa "Puglia" allora ritornerà None
        if 'Puglia' not in stringaContent:
            print('LA PAGINA NON è CORRELATA A PUGLIA')
            return 'NOT IN PUGLIA'
        '''
        stringaProva = extractJsonFromHtml(str(BeautifulSoup(content, 'html.parser')), None)
        for each in stringaProva:
            text = str(each)
            if 'pageItems' in text:
                j = 0
                require_object = extract_object(each, 'require')
                bbox_object = require_object[9][3][1]

                for j in range(0, 5):
                    try:
                        value_im_interested = bbox_object['__bbox']['result']['data']['node']['all_collections'][
                            'nodes'][0]['style_renderer']['collection']['pageItems']['edges'][j]['node']['url']
                        # if starts with https://www.facebook.com/ add it
                        if value_im_interested != None:
                            if value_im_interested.startswith('https'):
                                profile_followers.append(value_im_interested)
                                j = j+1

                        stringOrganizers = str(value_im_interested)

                    except Exception as e:
                        # if the exception is because the page has less than 10 followers, just ignore it
                        if str(e) == 'list index out of range':
                            break
                        else:
                            print(str(e))
                            return None
                print('la pagina facebook ha questi seguiti:  ' + stringOrganizers)
                return profile_followers


@progress_decorator
def fetch_fb_page(item: FacebookOrganizer, crawler: FacebookCrawler):
    if crawler.lat == None or crawler.lon == None:
        crawler.process(item)
    else:
        lat_nord, lat_sud, lon_est, lon_ovest = crawler.coordinate_dopo_n_km(crawler.lat, crawler.lon, MAXIMUM_DISTANCE)
        if lat_nord > item.lat and item.lat > lat_sud and lon_ovest < item.lng and item.lng < lon_est:
            crawler.process(item)
