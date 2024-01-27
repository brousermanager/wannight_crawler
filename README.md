# Bro-Users Crawler

## Indice dei moduli

AFRODITE (dea della bellezza) - Gestione dello storage delle immagini con AWS

APOLLO (dio delle scienze) - Ricerca delle pagine Facebook degli organizzatori trovati su Google

ATHENA (dea della conoscenza) - Ricerca degli organizzatori su Google

ATLAS (titano) - Controlla ed esegue tutti i processi

DIONISO (dio del divertimento) - Ricerca gli eventi su Facebook con esecuzioni ricorsive

ERMES (messaggero degli dei) - Gestisce il bot Telegram

HERA (dea delle relazioni) - Gestisce le connessioni con il db

#TODO: trovare un nome decennte a SIRIO che non è la divinità Egizia Iside ne la divinità greca Demetra
SIRIO (dio Iside per i greci) - Classifica gli eventi

## Setup 
### Windows

Install venv.

```bash
pip install virtualenv
```

Creare un ambiente virtuale chiamato venv.

```bash
python -m venv venv
```

Attivare venv su Windows.

```bash
.\venv\Scripts\activate 
```

Eseguire in caso di problemi con le policy di Windows.

```bash
Set-ExecutionPolicy Unrestricted -Scope Process 
```

Installare tutte le dipendenze elencate nel file requirements.txt con il seguente comando.

```bash
pip install -r requirements.txt
```

### Linux
Install python virtual environment
```bash
sudo apt install python3-venv
```

Create virtual environment
```bash
python -m venv venv
```

Activate virtual environment
```bash
source venv/bin/activate
```

Install requirements dependencies
```bash
pip install -r requirements.txt
```
## Setup Database

Installare la dipenza

```bash
pip install .\wannight_database-*.tar.gz
```

Creare immagine docker locale

```bash
docker run --name wannight -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
```

Accedere al terminale dell'immagine e creare il db

```bash
psql -U postgres
```
```sql
create database wannight;
```

Inserire nel file .env l'url del db

```bash
DATABASE_URL='postgresql://postgres:password@localhost:5432/wannight'
```

## Utilizzo

Posizionarsi nella directory del progetto ed eseguire il file ATLAS.py per avviare il processo, usare come argomenti il nome del processo desiderato e i files da usare come input. I files di input vanno inseriti rispettivamente nei percorsi relativi.

```bash
python ATLAS.py OneNightCrawling
```

È possibile eseguire i singoli processi.

```bash
python ATLAS.py ATHENA
python ATLAS.py APOLLO
python ATLAS.py DIONISO
```

## Esecuzione di specifiche query

```bash
# Gestione delle crawler settings
python ATLAS.py HERA CrawlerSettings name priority frequency process unity active
# Inserimento di citta
python ATLAS.py HERA AddCity city
# Inserimento di una categoria di ricerca
python ATLAS.py HERA AddCategory category
# Inserimento di una categoria da usare per la classificazione degli eventi
python ATLAS.py HERA AddCategorySirio category
```

Note: usare più volte CrawlerSettings su una impostazione già esistente per modificarla; usare più volte AddCity o AddCategory per eliminare il record.

## Obiettivo

Entrare gratis nelle discoteche e fare bordello!
