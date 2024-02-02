import os
import sys
import traceback
import sched, time
from enum import Enum
from dotenv import load_dotenv

from hera import set_database

from modules.ATHENA.ATHENA import start_athena
from modules.APOLLO.APOLLO import start_apollo
from modules.DIONISO.DIONISO import start_dioniso
from modules.SIRIO.SIRIO import startSirio
from modules.ARCHIMEDE.ARCHIMEDE import start_archimede

#TODO: Sistema i log su db

class Process(Enum):
    ARCHIMEDE = 0  # Pulisci database da eventi passati
    ATHENA = 1
    APOLLO = 2
    DIONISO = 3
    SIRIO = 4
    
def runArchimede() -> None :
    print('ARCHIMEDE sta analizzando wannight...')
    code = start_archimede()
    print('ARCHIMEDE ha finito di analizzare... è stanco, lasciamolo riposare.')
def runAthena() -> None :
    print('ATHENA avviata')
    code = start_athena()
    if code == 1 :
        print('Errori nell\'esecuzione della ATHENA...')
    else :
        print('ATHENA avvenuta con successo!')

def runApollo() -> None :
    print('APOLLO avviato')
    code = start_apollo()
    if code == 1 :
        print('Errori nell\'esecuzione di APOLLO...')
    else :
        print('APOLLO avvenuto con successo!')

def runDioniso() -> None :
    print('DIONISO avviato!')
    code = start_dioniso(sys.argv[1] == 'OneNightCrawling')
    if code == 1 :
        print('Errori nell\'esecuzione di DIONISO...')
    else :
        print('DIONISO avvenuto con successo!')

def runSirio() -> None :
    print('SIRIO avviato')
    code = startSirio()
    if code == 1 :
        print('Errori nell\'esecuzione di SIRIO...')
    else :
        print('SIRIO avvenuto con successo!')

Process.ARCHIMEDE.function = runArchimede
Process.ATHENA.function = runAthena
Process.APOLLO.function = runApollo
Process.DIONISO.function = runDioniso
Process.SIRIO.function = runSirio
scheduler = sched.scheduler(time.time, time.sleep)

def schedulerFunction(delay: int, priority: int, process: str) -> None :
    getattr(Process, process).function()
    scheduler.enter(
        delay = delay,
        priority = priority,
        action = schedulerFunction,
        argument = (delay, priority, process)
    )

#args: 0-Atlas.py 1-Process 2-Category 3-City 4-Setting
def setupOneNightCrawling() -> None :
    # rules = executeSpecificQuery('GetAllCrawlerSettings')
    rules = []
    assert rules != 1, 'Errore nell\'estrazione dei settings!'
    for rule in rules :
        priority = rule['priority']
        frequency = getFrequency(rule['unity'], rule['frequency'])
        scheduler.enter(
            delay = 0, 
            priority = priority, 
            action = schedulerFunction,
            argument = (frequency, priority, rule['process'])
        )
    print('OneNightCrawling avviato!')
    scheduler.run()

def getFrequency(unity: str, frequency: str) -> int :
    time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'M': 2592000, 'y': 31536000}
    assert unity in time_units, 'Unità di misura non riconosciuta!'
    return int(frequency) * time_units[unity]

def setupSingleProcess() -> None :
    getattr(Process, sys.argv[1]).function()

if __name__ == '__main__' :
    load_dotenv()
  
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        print(database_url)
        set_database(database_url)
       
    else:
        # Handle the case where the database URL is not found
        print(f"Database URL not found for key: {database_url_key}")
    if len(sys.argv) > 1 :
        try:
            if sys.argv[1] == 'OneNightCrawling' :
                setupOneNightCrawling()
            else :
                setupSingleProcess()
        except Exception as e :
            traceback.print_exception(e)
    else:
        print('Argomento mancante!')
    