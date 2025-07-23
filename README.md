# Schedule Service

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-black?logo=flask)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![Status](https://img.shields.io/badge/Status-Production-brightgreen)

Un microservizio per visualizzare in tempo reale gli orari delle lezioni universitarie, sia per singole aule che per interi piani di un edificio.

![Showcase del Servizio Classroom](./docs/schedule-classroom-showcase.png)
![Showcase del Servizio Floor](./docs/schedule-floor-showcase.png)

---

## Descrizione

Lo **Schedule Service** si collega alle API ufficiali dell'ateneo (es. CINECA) per recuperare e mostrare gli orari delle lezioni. Fornisce due visualizzazioni ottimizzate per display di digital signage:

1.  **Vista Aula (`classroom_view.html`)**: Mostra il palinsesto giornaliero di una singola aula, evidenziando lo stato di ogni lezione (in corso, terminata, futura).
2.  **Vista Piano (`floor_view.html`)**: Aggrega gli orari di tutte le aule di un determinato piano, fornendo una panoramica completa.

Il servizio include un sistema di cache per minimizzare le chiamate all'API esterna e garantire una risposta rapida.

---

## Funzionalità

* **Vista Aula & Vista Piano**: Due modalità di visualizzazione per esigenze specifiche e generali.
* **Dati in Tempo Reale**: Si collega a API esterne per mostrare sempre gli orari più aggiornati.
* **Sistema di Cache**: Una cache in-memoria riduce il carico sull'API esterna e migliora le performance.
* **Supporto Bilingue**: Passa automaticamente da Italiano a Inglese per tutte le etichette.
* **Scorrimento Automatico**: Le tabelle con molte lezioni scorrono automaticamente per garantire la visibilità di tutti i contenuti.
* **Servizio Dockerizzato**: Pronto per il deployment come container indipendente e gestito tramite Docker Compose.

---

## Setup & Configurazione

La configurazione è minima.
1.  Nella cartella `schedule-service`, copia il file `.env.example` e rinominalo in `.env`.
2.  Il file contiene una variabile, `LESSON_API_BASE_URL`. Il valore di default è già impostato per l'Università di Messina, ma puoi cambiarlo se necessario.

---

## Avvio

Questo servizio è parte della `DigitalSignageSuite` e viene avviato tramite il file `docker-compose.yml` nella directory principale.

1.  Assicurati di essere nella cartella `DigitalSignageSuite`.
2.  Esegui il comando:
    ```bash
    docker compose up --build -d
    ```
3.  Il servizio sarà accessibile sulla porta **8081**.

---

## Utilizzo e URL di Esempio

Per utilizzare il servizio, costruisci un URL specificando la vista e i parametri desiderati.

### Vista Aula (`classroom_view.html`)

Mostra l'orario di una singola aula.

* **URL:** `http://localhost:8081/views/classroom_view.html?classroom=5f775da9bb0c1600171ae370&building=5f6cb2c183c80e0018f4d46&date=2025-07-23`

* **Parametri Disponibili:**

| Parametro     | Descrizione                                                               | Esempio                          |
| :------------ | :------------------------------------------------------------------------ | :------------------------------- |
| `classroom`   | **(Obbligatorio)** L'ID tecnico dell'aula.                                | `5f775da9bb0c1600171ae370`       |
| `building`    | **(Obbligatorio)** L'ID tecnico dell'edificio a cui appartiene l'aula.    | `5f6cb2c183c80e0018f4d46`       |
| `date`        | (Opzionale) La data per cui mostrare l'orario, in formato `YYYY-MM-DD`.   | `2025-07-23`                     |
| `period`      | (Opzionale) Filtra per `morning`, `afternoon` o `all` (default).          | `period=morning`                 |

### Vista Piano (`floor_view.html`)

Mostra l'orario aggregato di un intero piano.

* **URL:** `http://localhost:8081/views/floor_view.html?floor=1&building=A&date=2025-07-23`

* **Parametri Disponibili:**

| Parametro  | Descrizione                                                              | Esempio             |
| :--------- | :----------------------------------------------------------------------- | :------------------ |
| `floor`    | **(Obbligatorio)** Il numero del piano (es. `-1`, `0`, `1`, `2`).          | `1`                 |
| `building` | **(Obbligatorio)** La chiave breve dell'edificio (`A`, `B`, `SBA`).       | `A`                 |
| `date`     | (Opzionale) La data per cui mostrare l'orario, in formato `YYYY-MM-DD`.  | `2025-07-23`        |

---

## Tecnologie Utilizzate

* **Backend**: Python, Flask, Gunicorn, Pydantic
* **Frontend**: HTML5, CSS3, JavaScript
* **Deployment**: Docker