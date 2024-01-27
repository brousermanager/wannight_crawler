import random
import string
import requests

#i dati dissimili che devi determinari sono
#X-Fb-Lsd che sta sia in data sia negli headers ed è lo stesso
#hsi che è una stringa in data  la trovi nella prima richiesta cercando "hsi"
#variables=%7B%22pageID%22%3A%22 114598135236933 %22%7D solo il codice tra i 2 %22 è dissimile e lo trovi nella prima richiesta cercando "pageID"
# "__spin_t" è un parametroche trovi nell'html iniziale cercando appunto   _spin_t":

#doc_id che è un numero(5343523095766906) in data alla fine
#lo trovi facendo una chiamata api al link che sta  "w741Nwb": e poi cercare all'interno della risposta del server
#doc_id=secondorichiesta(url)

class EventExtractor :
    
    def __init__(self, upcomingFlag: bool) :
        self.upcomingFlag = upcomingFlag
        self.stringa = None
        self.cookies = {
            'datr' : '4dRWY85ekoWoUSRvzBlt441L',
            'sb' : 'NtVWYyXlr7LM1vsjdm0rcYnL',
            'wd' : '1440x796',
            'dpr' : '2',
        }
        self.headers = {
            'Host' : 'www.facebook.com',
            'Viewport-Width' : '720',
            'Sec-Ch-Ua' : '"Not?A_Brand";v="8", "Chromium";v="108"',
            'Sec-Ch-Ua-Mobile' : '?0',
            'Sec-Ch-Ua-Platform' : '"macOS"',
            'Sec-Ch-Prefers-Color-Scheme' : 'light',
            'Upgrade-Insecure-Requests' : '1',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.72 Safari/537.36',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site' : 'none',
            'Sec-Fetch-Mode' : 'navigate',
            'Sec-Fetch-User' : '?1',
            'Sec-Fetch-Dest' : 'document',
            'Accept-Language' : 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection' : 'close'
            # 'Accept-Encoding': 'gzip, deflate',
            # 'Cookie': 'datr=4dRWY85ekoWoUSRvzBlt441L; sb=NtVWYyXlr7LM1vsjdm0rcYnL; wd=1440x796; dpr=2',
        }

    def loginIsNotNedeed(self, cookies: dict, headers: dict, parameters: dict) :
        self.cookies = {
            'datr' : cookies['datr'],
            'dpr' : cookies['dpr'],
            'sb' : cookies['sb'],
            'wd' : '1680x946',
        }
        self.headers = {
            'Host': headers['host'],
            'Sec-Ch-Ua': headers['secchua'],
            'Sec-Ch-Ua-Mobile': headers['seccamobile'],
            'User-Agent': headers['useragent'],
            'Viewport-Width': headers['viewport'],
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Fb-Lsd': parameters['lsd'],
            'X-Fb-Friendly-Name': 'PageEventsTabUpcomingEventsCardRendererQuery' if self.upcomingFlag 
                else 'PageEventsTabPastEventsCardRendererQuery',
            'Sec-Ch-Prefers-Color-Scheme': headers['colorscheme'],
            'Sec-Ch-Ua-Platform': headers['secuaplatform'],
            'Accept': '*/*',
            'Origin': 'https://www.facebook.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.facebook.com/pg/' + parameters['name'] + '/events/',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8', 
        }
     

    def __makeEventsRequest__(self, parameters: dict) -> str :
        s = ''.join(random.choices(string.ascii_letters + string.digits, k = 11)).lower()
        sNumber = ''.join(random.choices(string.digits, k = 4))
        parameters['s'] = sNumber[0] + s[0] + s[1] + s[2] + s[2] + s[4] + '%3A' + s[5] + s[6] + sNumber[1] + sNumber[2] + \
            '%3A' + s[7]+sNumber[3] + s[8] + s[9] + sNumber[3] + s[10]
        data = 'av=0&__user=0&__a=1&__dyn=7AgNe5Gg4WS5k1ryaxG4QjFwn8S2Sq2i5U4e1qzEjyQUC3eF8vyUuKewhEmwKzorx62bwCwSz820xi3y4o4O0C8dU21CwDwLwxw-KEdEnwho4a3mbzU2px278-0BE662y22225o-cyo7y8wc-5bgO2G3i0UEbU9kbxS4UN0hUb82kwnGwWwlo5qfK6EaE4y58jwVw9O1iwKxm9yUe888d8nwhE2Lx-0iS2S3qazo11E2ZwhF8-4U6C2-2B0oo&__csr=&__req=2&__hs=' + \
            parameters['haste_session'] + '.BP%3ADEFAULT.2.0.0.0.0&dpr=2&__ccg=EXCELLENT&__rev=' + parameters['spinR'] + '&__s=' + parameters['s'] + '&__hsi=' + parameters['hsi'] + '&__comet_req=0&lsd=+' + parameters['lsd'] + '&jazoest=' + parameters['jazoest'] + '&__spin_r='+parameters['spinR'] + '&__spin_b=trunk&__spin_t=' + \
                parameters['spinT'] + '&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=PageEventsTab' + ('Upcoming' if self.upcomingFlag else 'Past') + 'EventsCardRendererQuery&variables=%7B%22pageID%22%3A%22' + parameters['pageId'] + '%22%7D&server_timestamps=true&doc_id=' + parameters['docIdPresentEvents' if self.upcomingFlag else 'docIdPastEvents']
        self.stringa =  requests.post(
            'https://www.facebook.com/api/graphql/',
            cookies = self.cookies,
            headers = self.headers,
            data = data,
            verify = False,
            timeout = 3).text

    def __logInNeededApiRequest__(self, parameters: dict) -> None :
        url = 'https://www.facebook.com/' + parameters['name'] + (
            '/upcoming_hosted_events' if self.upcomingFlag else '/past_hosted_events'
        )
        self.stringa = requests.get(
            url,
            cookies = self.cookies,
            headers = self.headers,
            verify = False,
        ).text