import traceback
import time
from progress import progress_decorator
from .utils import get_organizer_without_fb_page, make_google_request, parse_google_response, fix_results

from hera.schema import FacebookOrganizer, GoogleOrganizer, Organizer
from hera import create, update, Session


# Legge i file di input, gestisce le query a Google e scrive i file di output
def start_apollo() -> int:
    try:
        names, count, dup, ok, notFB = [], 0, 0, 0, 0
        load_organizers(get_organizer_without_fb_page(),
                        'APOLLO', names, count, dup, ok, notFB)
        print(
            f'Total: {count} Duplicates: {dup} Singles: {ok} Not Facebook: {notFB}')
    except Exception as e:
        traceback.print_exception(e)
        return 1
    return 0


#   Si occupa di trovare la pagina fb, restituisce la lista dei gestori modificati
@progress_decorator
def load_organizers(gestore: FacebookOrganizer, names: list, count: int, dup: int, ok: int, notFB: int) -> None:
    count += 1
    if gestore.name not in names:
        names.append(gestore.name)
        try:
            fb = get_facebook_page(gestore)
            if fb != 'PorcoDio':
                ok += 1
                create_facebook_organizer(gestore.id, fb)
            else:
                notFB += 1
        except Exception as e:
            notFB += 1
            traceback.print_exception(e)
    else:
        dup += 1


def get_facebook_page(gestore: GoogleOrganizer) -> str:
    time.sleep(1)
    string = f'{gestore.name} {gestore.city} site:facebook.com'
    try:
        content = make_google_request(string)
        urls = parse_google_response(content)
        return fix_results(urls)
    except Exception as e:
        print('Errore nella richiesta: ' + str(e))
        return 'PorcoDio'


def create_facebook_organizer(id, url) -> str:
    fb = create(FacebookOrganizer, {'url': url})
    with Session() as session:
        o = session.query(Organizer).filter(
            Organizer.google_organizer_id == id
        ).first()
        update(o, {'facebook_organizer_id': fb.id})
