# lession-kiosk-display

![Python](https://img.shields.io/badge/python-3.11-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![UI](https://img.shields.io/badge/interface-responsive-lightgrey)
![Docker](https://img.shields.io/badge/container-Docker--ready-blue)


> EN: A digital signage system to display university classroom and floor schedules in real time.  
> IT: Un sistema di digital signage per visualizzare in tempo reale gli orari delle lezioni per aula e per piano.

---

## 🧩 Description / Descrizione

**EN:**  
lession-kiosk-display is a Flask-based web application that dynamically shows current and upcoming lessons in classrooms and across entire floors of a university building.  
It uses official API data (e.g., from Cineca/Unime) and supports bilingual display (IT/EN) with automatic language switching, responsive UI, and Docker-based deployment.

**IT:**  
lession-kiosk-display è un'applicazione web basata su Flask che mostra in tempo reale le lezioni in corso o imminenti per singole aule o per interi piani.  
Utilizza dati ufficiali (es. API Cineca/Unime) e supporta visualizzazione bilingue (IT/EN), interfaccia responsive e distribuzione via Docker.

---

## 🏗️ Project Structure / Struttura del progetto

```
lession-kiosk-display/
├── app/                              # Backend Flask API
│   ├── __init__.py                   # Inizializzazione app Flask
│   ├── config.py                     # Configurazione API base
│   ├── constants.py                  # Mappatura ID aula/piani
│   ├── models.py                     # Schemi Pydantic, cache
│   ├── routes.py                     # Rotte Flask (API /lessons, /floor)
│   └── services.py                   # Logica di fetch/split lezioni
│
├── web/                              # Frontend statico
│   ├── assets/                       # Asset statici (immagini, icone)
│   │   ├── monitor_background.png
│   │   └── favicon.ico
│   ├── static/
│   │   ├── css/
│   │   │   ├── classroom_style.css   # Stile per visualizzazione aula
│   │   │   └── floor_style.css       # Stile per visualizzazione piano
│   │   └── js/
│   │       ├── classroom_script.js   # Script visualizzazione aula
│   │       └── floor_script.js       # Script visualizzazione piano
│   ├── classroom/
│   │   └── index.html                # Visualizzazione per singola aula
│   └── floor/                        # Visualizzazioni per piano
│       ├── floor0.html               # Piano 0
│       ├── floor1.html               # Piano 1
│       └── floorM1.html              # Piano -1
│
├── requirements.txt                  # Dipendenze Python
└── Dockerfile                        # Dockerfile produzione
```

---

## 🚀 Quick Start / Avvio rapido

### ▶️ With Docker / Con Docker

```bash
# Build the image
docker build -t info-kiosk .

# Run the container on port 8080
docker run -p 8080:8080 info-kiosk
```

### ▶️ Without Docker / Senza Docker

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app (development mode)
python run.py
```

---

## 📦 API Endpoints

| Endpoint              | Method | Description (EN)                     | Descrizione (IT)                            |
|----------------------|--------|--------------------------------------|---------------------------------------------|
| `/`                  | GET    | Homepage                             | Pagina principale                           |
| `/lessons`           | POST   | Get lessons for a classroom          | Ottiene lezioni per aula                    |
| `/floor/<floor>`     | GET    | Get lessons for a floor              | Ottiene lezioni per piano                   |
| `/assets/<filename>` | GET    | Serve static asset (image/icon)      | Restituisce asset statici                   |

---

## 🌍 Parameters / Parametri supportati

### Classroom view (`classroom/index.html?classroom=...&building=...`)

- `classroom` – ID aula
- `building` – ID edificio
- `period` – `morning`, `afternoon` o `all`
- `date` – Data nel formato `YYYY-MM-DD` (opzionale)

### Floor view (`floor/floorNUMBER.html?date=YYYY-MM-DD`)

- `date` – Data nel formato `YYYY-MM-DD` (opzionale)

- 🔗 **Classroom view example**: [http://localhost:8080/static/classroom/index.html?classroom=CODE&building=CODE&date=DATE&period=PERIOD](http://localhost:8080/static/classroom/index.html?classroom=CODE&building=CODE&date=DATE&period=PERIOD)
- 🔗 **Floor**: [http://172.16.32.13:5000/static/floor/floorNUMBER.html?date=2DATE](http://172.16.32.13:5000/static/floor/floorNUMBER.html?date=2DATE)
---

## 📚 Technologies / Tecnologie utilizzate

- **Backend**: Python 3.11, Flask, Gunicorn, Pydantic, Requests
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Docker

---

## 👥 Authors / Autori

- **Massimo Mantineo**  
  @ Università di Messina  
  Corso di Laurea in Informatica (L-31)
  - **Adeebullah Hamidy**  
  @ Università di Messina  
  Corso di Laurea in Informatica (L-31)

---

## 📄 License / Licenza

> This project is released under the [MIT License](LICENSE).  
> Questo progetto è distribuito sotto licenza [Licenza MIT](LICENSE).
