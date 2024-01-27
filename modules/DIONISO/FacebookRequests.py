import time
import requests
from bs4 import BeautifulSoup


def __makeFirstRequest__(cookies: dict, headers: dict, url: str) -> str:
    cookies = {
        'datr': cookies['datr'],
        'dpr': cookies['dpr'],
        'sb': cookies['sb'],
        # questo può cambiare da richiesta a richiesta  wd=1680x946 prova a ometterlo
        'wd': cookies['wd']
    }
    headers = {
        'Host': headers['host'],
        'Viewport-Width': headers['viewport'],
        'Sec-Ch-Ua': headers['secchua'],
        'Sec-Ch-Ua-Mobile': headers['seccamobile'],
        'Sec-Ch-Ua-Platform': headers['secuaplatform'],
        'Sec-Ch-Prefers-Color-Scheme': headers['colorscheme'],
        'Upgrade-Insecure-Requests': headers['upgradeinsecurerequests'],
        'User-Agent': headers['useragent'],
        'Accept': headers['accept'],
        'Sec-Fetch-Site': headers['secfetchsite'],
        'Sec-Fetch-Mode': headers['secfetchmode'],
        'Sec-Fetch-User': headers['secfetchuser'],
        'Sec-Fetch-Dest': headers['secfetchdest'],
        'Accept-Language': headers['acceptlanguage'],
        'Connection': headers['connectio']
    }
    tries = 0
    while tries < 5:
        try:
            # if url ends with / just remove it
            if url[-1] == '/':
                url = url[:-1]
            response = requests.get(url+'/events', cookies=cookies, headers=headers, timeout=3, verify=False)
            return response.text
        except Exception as e:
            print('Errore nella richiesta: ' +
                  str(e)+'\nTentativo: '+str(tries))
            tries += 1
            time.sleep(1)
    return None


def __makeFollowersRequest__(cookies, headers, url):
    cookies = {
        'datr': '4dRWY85ekoWoUSRvzBlt441L',
        'sb': 'NtVWYyXlr7LM1vsjdm0rcYnL',
        'dpr': '2',
        'wd': '1680x946'
    }

    headers = {
        'Host': 'www.facebook.com',
        'Viewport-Width': '1440',
        'Sec-Ch-Ua': '"Not A(Brand";v="24", "Chromium";v="110"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Ch-Prefers-Color-Scheme': 'light',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        # 'Cookie': 'datr=4dRWY85ekoWoUSRvzBlt441L; sb=NtVWYyXlr7LM1vsjdm0rcYnL',
    }
    tries = 0
    while tries < 5:
        try:
            response = requests.get(
                url,
                cookies=cookies,
                headers=headers,
                verify=False,
            )

            return response.text

        except Exception as e:
            print('Errore nella richiesta per i: ' + str(e)+'\nTentativo: '+str(tries))
            tries += 1
            time.sleep(1)
    return None


def __makeEventRequest__(cookies: dict, headers: dict, eventID: str) -> dict:  # TODO: DICT??
    # try this request 5 times delaying 1 second between each try and then return None if it fails all 5 times

    tries = 0
    cookies = {
        'datr': cookies['datr'],
        'sb': cookies['sb'],
        'wd': '1680x946',
        'dpr': cookies['dpr'],
        'locale': 'it_IT',
    }
    headers = {
        'Host': headers['host'],
        'Cache-Control': 'max-age=0',
        'Viewport-Width': '840',
        'Sec-Ch-Ua': headers['secchua'],
        'Sec-Ch-Ua-Mobile':  headers['seccamobile'],
        'Sec-Ch-Ua-Platform': headers['secuaplatform'],
        'Sec-Ch-Prefers-Color-Scheme': headers['colorscheme'],
        'Upgrade-Insecure-Requests': headers['upgradeinsecurerequests'],
        'User-Agent': headers['useragent'],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': headers['secfetchsite'],
        'Sec-Fetch-Mode': headers['secfetchmode'],
        'Sec-Fetch-User': headers['secfetchuser'],
        'Sec-Fetch-Dest': headers['secfetchdest'],
        'Accept-Language': headers['acceptlanguage'],
        'Accept-Encoding': 'gzip, deflate'
        # 'Accept-Encoding': 'gzip, deflate',
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'datr=4dRWY85ekoWoUSRvzBlt441L; sb=NtVWYyXlr7LM1vsjdm0rcYnL; wd=1680x946; dpr=2; locale=it_IT',
    }
    while tries < 5:
        try:
            response = requests.get('https://www.facebook.com/events/' + eventID, cookies=cookies, headers=headers, timeout=3, verify=False)

            return response.text

        except Exception as e:
            print('Errore nella richiesta: ' + str(e)+'\nTentativo: '+str(tries))
            tries += 1
            time.sleep(1)
    return None


def __analyzeFirstRequest__(content: str, url: str) -> dict:
    if content == None:
        return None
    else:
        object = {}
        object['lsd'] = None
        object['jazoest'] = None
        object['hsi'] = None
        object['spinT'] = None
        object['spinR'] = None
        object['haste_session'] = None
        object['pageId'] = None
        try:
            object['name'] = url.split('facebook.com/')[1].split('/')[0]
        except:
            object['name'] = None
        
        try:
            object['loginNeed'] = False
            soup = BeautifulSoup(content, 'html.parser')
            for link in soup.find_all():
                if link.find("input", {"name": "lsd"}):
                    object["lsd"] = str(findLsd(link))
                else:
                    object["lsd"] = None
                    print("lsd not found")

                if link.find("input", {"name": "jazoest"}):
                    object["jazoest"] = str(
                        link.find("input", {"name": "jazoest"})["value"])
                else:
                    object["jazoest"] = None
                    print("jazoest not found")

                # TODO fare una regex per sto cazzo di str(link) che non può avere 5 if innestati =/
                if "\"hsi\":" in str(link):
                    object["hsi"] = findHsi(link)
                else:
                    object["hsi"] = None
                    print("hsi not found")

                if "\"__spin_t\"" in str(link):
                    object["spinT"] = findSpinT(link)
                else:
                    object["spinT"] = None
                    print("spinT not found")
                
                if "spin_r" in str(link):
                    object["spinR"] = str(link)[str(link).find(
                        "spin_r") + 8: str(link).find("spin_r") + 99].split(",")[0]
                else:
                    object["spinR"] = None
                    print("spinR not found")
                
                if "haste_session" in str(link):
                    object["haste_session"] = str(link)[str(link).find(
                        "haste_session") + 16: str(link).find("haste_session") + 99].split(".")[0]
                else:
                    object["haste_session"] = None
                    print("haste_session not found")
                
                if "fb://page/?id=" in str(link):
                    object["pageId"] = findPageId(link)
                    break
                else:
                    object["pageId"] = None
                    print("pageId not found")
                    break

        except:
            object['loginNeed'] = True
            print("login needed")
            # if pageid or lsd or jazoest or hsi or spinT or spinR or haste_session is None, the page is private
            # so login is needed
        if object['pageId'] == None or object['lsd'] == None or object['jazoest'] == None or object['hsi'] == None or object['spinT'] == None or object['spinR'] == None or object['haste_session'] == None:
            object['loginNeed'] = True

        return object


def findLsd(link):
    # if you find it in this place okay
    lsd = link.find("input", {"name": "lsd"})["value"]
    if lsd == None:
        # if you find it in this place okay
        lsd = link.find("input", {"name": "lsd"})["value"]
    return link.find("input", {"name": "lsd"})["value"]


# TODO: Ma qui è necessario che cambi il valore di link?
def findHsi(link):
    link = (str(link)[str(link).find("\"hsi\"") + 7: str(link).find("\"hsi\"") + 200]).split("\"")[0]
    return str(link)


def findSpinT(link):
    link = (str(link)[str(link).find("\"__spin_t\"") + 11: str(link).find("\"__spin_t\"") + 200]).split(",")[0]
    return str(link)


def findPageId(link):
    return str(link)[str(link).find("fb://page/?id=") + 14: str(link).find("fb://page/?id=") + 30].split("\"")[0]
