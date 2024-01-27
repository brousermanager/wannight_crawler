from hera import Session
from datetime import datetime
from datetime import timedelta
import csv
import os
import boto3
import os
from dotenv import load_dotenv

from hera.schema import Event, Suggestion

load_dotenv()

# Definisci il nome del file CSV in cui verranno salvati gli eventi scaduti
csv_filename = 'outdated_events.csv'

def start_archimede(save=True, delete_outdated_events=True) -> int:
    save_outdated_events()
    remove_outdated_events()
    save_suggestions()

def save_outdated_events():
    outdated_events = get_outdated_events()

    # Se il file CSV non esiste, crea un nuovo file CSV con l'header
    if not os.path.isfile(csv_filename):
        with open(csv_filename, 'w', newline='', encoding='utf-8', errors='ignore') as csv_file:  # Specifica l'encoding come 'utf-8'
            writer = csv.writer(csv_file)
            header = ['ID', 'name', 'description', 'city', 'price', 'date_start', 'date_end', 'timestamp']
            writer.writerow(header)

    # Apri il file CSV in modalità append e leggi tutte le righe esistenti
    with open(csv_filename, 'r', newline='', encoding='utf-8', errors='ignore') as csv_file:  # Specifica l'encoding come 'utf-8'
        existing_events = set()
        reader = csv.reader(csv_file)
        next(reader)  # Salta l'header
        for row in reader:
            if len(row) > 0:
                existing_events.add(tuple(row))

    with open(csv_filename, 'a', newline='', encoding='utf-8') as csv_file:  # Specifica l'encoding come 'utf-8'
        writer = csv.writer(csv_file)
        for event in outdated_events:
            event_data = (
                event.name,
                event.description,
                event.city,
                event.price,
                event.date_start,
                event.date_end,
                event.date_added
            )
            if event_data not in existing_events:
                writer.writerow([event.id] + list(event_data))

    if len(outdated_events) > 0:
        print(f'Archimede: - "Ho salvato {len(outdated_events)} eventi, potrebbero servirci per alcuni esperimenti!"')



# Questa funzione rimuove tutti gli eventi che hanno 'date_end' minore della data odierna.
# Se l'evento ha solo 'date_start' allora viene eliminato 2 settimane dopo.
def remove_outdated_events():
    n = 0
    # Crea una sessione Hera utilizzando un blocco 'with' per garantire una corretta gestione delle risorse
    with Session() as session:
        # Query per ottenere tutti gli eventi con date_end inferiore alla data odierna
        # oppure con solo 'date_start' e la data odierna è maggiore di 2 settimane rispetto a 'date_start'
        outdated_events = get_outdated_events()

        # Rimuovi gli eventi obsoleti
        for event in outdated_events:
            # Elimina l'immagine associata all'evento
            if event.image:
                delete_image_from_s3(event.image)
            session.delete(event)

        # Esegui il commit per effettuare le modifiche nel database
        session.commit()
    if len(outdated_events)>0:
        print(f'Archimede:-"Ho rimosso {len(outdated_events)} eventi dal database. Finalmente un po di pulizie!"')

def delete_image_from_s3(key_name):
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )
        bucket_name = os.environ.get("BUCKET_EVENTI")

        s3.delete_object(Bucket=bucket_name, Key=f"{key_name}.jpg")
        return True
    except Exception as e:
        return False

def get_outdated_events():
    # Crea una lista vuota per gli eventi scaduti
    outdated_events = []

    # Crea una sessione Hera utilizzando un blocco 'with' per garantire una corretta gestione delle risorse
    with Session() as session:
        # Ottieni la data odierna
        current_date = datetime.now()
        two_weeks_ago = current_date - timedelta(weeks=2)

        # Query per ottenere tutti gli eventi con date_end inferiore alla data odierna
        # oppure con solo 'date_start' e la data odierna è maggiore di 2 settimane rispetto a 'date_start'
        outdated_events = session.query(Event).filter(
            (Event.date_end < current_date) | ((Event.date_end == None) & (Event.date_start < two_weeks_ago))
        ).all()

    return outdated_events

def get_suggestions():
    with Session() as session:
        return session.query(Suggestion).all()

def save_suggestions():
    filename = 'new_suggestions.csv'
    suggestions = get_suggestions()
    if suggestions and len(suggestions) > 0:
        headers = suggestions[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8', errors='ignore') as file_csv:
            writer = csv.DictWriter(file_csv, fieldnames=headers)
            writer.writeheader()
            writer.writerows(suggestions)
