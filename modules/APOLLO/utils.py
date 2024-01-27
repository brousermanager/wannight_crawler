import time
import re
import requests
from bs4 import BeautifulSoup

from hera.schema import GoogleOrganizer, Organizer
from hera import Session


def fix_results(results):
    pattern = r'^https://www\.facebook\.com/[^/]+/$'
    for result in results:
        # if the url ends with ?locale=it_IT, remove it
        if result.endswith('?locale=it_IT'):
            result = result[:-13]
        # find th first url that matches this pattern https://www.facebook.com/ilpineto/ and nothing after
        if (bool(re.match(pattern, result)) and len(result) == result.rfind('/') + 1):
            print('Url trovato: ' + result)
            return result
    return 'PorcoDio'


def get_organizer_without_fb_page() -> list:
    with Session() as session:
        return session.query(GoogleOrganizer).join(
            Organizer, GoogleOrganizer.id == Organizer.google_organizer_id
        ).filter(
            Organizer.facebook_organizer_id == None
        ).all()


def make_google_request(query) -> str:
    time.sleep(2)
   # SCADE OGNI SEI MESI

    cookies = {

        'NID': '511=uMg5pcN7bXVR7eHzcvnkVQpH7WQf8PeWuEGBk97kLMT7LjUiflYJSRNiRIlCd13omS_kczvi092ra81tS_beNrclJc2tgRYSlSG76xl-JGwdZ7mfWFJGzY1GDOwmub-UQ-8_BXGc_SfyvdkTIG_wGXjbeeJtGFApcwYfcII4mErz6TO7nMAF5_O6RPEDQA',

    }

    headers = {
        'Host': 'www.google.com',
        'Sec-Ch-Ua': '"Not:A-Brand";v="99", "Chromium";v="112"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Full-Version': '"112.0.5615.49"',
        'Sec-Ch-Ua-Arch': '"x86"',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Ch-Ua-Platform-Version': '"12.6.3"',
        'Sec-Ch-Ua-Model': '""',
        'Sec-Ch-Ua-Bitness': '"64"',
        'Sec-Ch-Ua-Wow64': '?0',
        'Sec-Ch-Ua-Full-Version-List': '"Not:A-Brand";v="99.0.0.0", "Chromium";v="112.0.5615.49"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'X-Client-Data': 'CKbjygE=',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        # 'Cookie': 'CONSENT=PENDING+777; SOCS=CAISHAgCEhJnd3NfMjAyMjEwMTAtMF9SQzIaAmVuIAEaBgiAq9eaBg; AEC=AUEFqZfYp43HfQIAqMG7Amz-8ncHMbOtEnCr0ed9WzDjA6filjehaUS12Es; NID=511=uMg5pcN7bXVR7eHzcvnkVQpH7WQf8PeWuEGBk97kLMT7LjUiflYJSRNiRIlCd13omS_kczvi092ra81tS_beNrclJc2tgRYSlSG76xl-JGwdZ7mfWFJGzY1GDOwmub-UQ-8_BXGc_SfyvdkTIG_wGXjbeeJtGFApcwYfcII4mErz6TO7nMAF5_O6RPEDQA; 1P_JAR=2023-5-14-9',
    }

    params = {
        'q': query,
        'oq': query,
        'sourceid': 'chrome',
        'ie': 'UTF-8',
    }
    tries = 0
    while tries < 5:
        try:
            response = requests.get('https://www.google.com/search',
                                    params=params, cookies=cookies, headers=headers, verify=False)

            return response.text

        except Exception as e:
            print('Errore nella richiesta per : ' +
                  str(e)+'\nTentativo: '+str(tries))
            tries += 1
            time.sleep(1)
    return None


def parse_google_response(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.find_all('div', class_='yuRUbf')
    urls = []
    for result in results:
        url = result.find('a')['href']
        urls.append(url)
    return urls
