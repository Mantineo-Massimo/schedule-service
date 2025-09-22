/**
 * EN:
 * This script controls all the dynamic behavior of the `classroom_view.html` page.
 * Its main responsibilities include:
 * - Fetching lesson data from the backend API.
 * - Synchronizing time with a server endpoint to ensure accuracy.
 * - Updating the clock display every second.
 * - Periodically toggling between Italian and English languages.
 * - Rendering the lesson data into the HTML table.
 * - Handling a smooth auto-scroll animation if the content overflows.
 * - Refreshing data at a regular interval.
 *
 * IT:
 * Questo script controlla tutto il comportamento dinamico della pagina `classroom_view.html`.
 * Le sue responsabilità principali includono:
 * - Recuperare i dati delle lezioni dall'API del backend.
 * - Sincronizzare l'ora con un endpoint del server per garantirne l'accuratezza.
 * - Aggiornare l'orologio visualizzato ogni secondo.
 * - Alternare periodicamente tra le lingue italiano e inglese.
 * - Renderizzare i dati delle lezioni nella tabella HTML.
 * - Gestire un'animazione di scorrimento automatico se il contenuto è troppo lungo.
 * - Aggiornare i dati a intervalli regolari.
 */
document.addEventListener('DOMContentLoaded', function() {
    // EN: Centralized object for DOM element references for performance and clarity.
    // IT: Oggetto centralizzato per i riferimenti agli elementi del DOM per performance e chiarezza.
    var dom = {
        lessonBody: document.getElementById('lesson-body'),
        clock: document.getElementById('clock'),
        classroomName: document.getElementById('classroom-name'),
        currentDate: document.getElementById('current-date'),
        body: document.body
    };

    // EN: Centralized object for managing the application's dynamic state.
    // IT: Oggetto centralizzato per la gestione dello stato dinamico dell'applicazione.
    var state = {
        currentLanguage: 'it',
        lessons: [],
        fetchStatus: 'loading', // 'loading', 'success', or 'error'
        params: new URLSearchParams(window.location.search),
        timeDifference: 0, // EN: Difference in ms between server and client time. / IT: Differenza in ms tra ora del server e del client.
        get displayDate() {
            var dateStr = this.params.get('date') || new Date().toISOString().split('T')[0];
            return new Date(dateStr + 'T12:00:00');
        }
    };
    
    // EN: Centralized object for static configuration values.
    // IT: Oggetto centralizzato per i valori di configurazione statici.
    var config = {
        timeServiceUrl: '/api/time/', // EN: Using a relative path for proxy. / IT: Usa un percorso relativo per il proxy.
        languageToggleInterval: 15, // seconds
        dataRefreshInterval: 5 * 60, // seconds
    };
    
    // EN: Object containing all translation strings for easy language switching.
    // IT: Oggetto contenente tutte le stringhe di traduzione per un facile cambio di lingua.
    var translations = {
        it: {
            days: ["Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"],
            months: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
            status: { soon: 'Futura', live: 'In corso', ended: 'Terminata' },
            noLessons: 'Nessuna lezione disponibile al momento',
            missingParams: "Parametri 'classroom' o 'building' mancanti",
            loadingError: "Errore nel caricamento delle lezioni"
        },
        en: {
            days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            status: { soon: 'Upcoming', live: 'Ongoing', ended: 'Ended' },
            noLessons: 'No lessons available at the moment',
            missingParams: "Missing 'classroom' or 'building' parameters",
            loadingError: "Error loading lessons"
        }
    };

    /**
     * EN: Syncs the local time with the server's time to correct for client-side clock drift.
     * IT: Sincronizza l'ora locale con quella del server per correggere imprecisioni dell'orologio del client.
     */
    function syncTimeWithServer() {
        fetch(config.timeServiceUrl)
            .then(function(response) {
                if (!response.ok) throw new Error('Time API not responding');
                return response.json();
            })
            .then(function(data) {
                var serverNow = new Date(data.time);
                var clientNow = new Date();
                state.timeDifference = serverNow - clientNow;
                console.log('Time synchronized. Server/client difference:', state.timeDifference, 'ms');
            })
            .catch(function(error) {
                console.error('Could not sync time with server:', error);
                state.timeDifference = 0; // EN: Fallback to client time on error. / IT: Ripiega sull'ora del client in caso di errore.
                dom.clock.style.color = 'red';
            });
    }

    /**
     * EN: Updates the clock display every second using the server-synced time.
     * IT: Aggiorna l'orologio ogni secondo usando l'ora sincronizzata con il server.
     */
    function updateClock() {
        var serverTime = new Date(new Date().getTime() + state.timeDifference);
        var clockOptions = { timeZone: 'Europe/Rome', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        dom.clock.textContent = serverTime.toLocaleTimeString('it-IT', clockOptions);
    }
    
    /**
     * EN: Updates the static UI elements like date and classroom name.
     * IT: Aggiorna gli elementi statici dell'interfaccia come data e nome dell'aula.
     */
    function updateStaticUI() {
        var lang = translations[state.currentLanguage];
        var displayDate = state.displayDate;
        var dayName = lang.days[displayDate.getUTCDay()];
        var monthName = lang.months[displayDate.getUTCMonth()];
        dom.currentDate.textContent = dayName + ' ' + displayDate.getUTCDate() + ' ' + monthName + ' ' + displayDate.getUTCFullYear();
        if (state.lessons.length > 0) {
            dom.classroomName.textContent = state.lessons[0] ? state.lessons[0].classroom_name : 'Classroom';
        }
    }
    
    /**
     * EN: Toggles the display language and updates all text content.
     * IT: Cambia la lingua di visualizzazione e aggiorna tutto il contenuto testuale.
     */
    function toggleLanguage() {
        state.currentLanguage = (state.currentLanguage === 'en') ? 'it' : 'en';
        dom.body.className = 'lang-' + state.currentLanguage;
        // EN: Re-render to apply the new language strings. / IT: Esegue nuovamente il render per applicare le nuove stringhe di lingua.
        renderLessons();
    }
    
    /**
     * EN: Displays a message in the table (e.g., "No lessons").
     * IT: Mostra un messaggio nella tabella (es. "Nessuna lezione").
     */
    function showMessageInTable(messageKey) {
        var message = translations[state.currentLanguage][messageKey];
        dom.lessonBody.innerHTML = '<tr><td colspan="4">' + message + '</td></tr>';
    }
    
    /**
     * EN: Determines the current status of a lesson (soon, live, ended).
     * IT: Determina lo stato attuale di una lezione (futura, in corso, terminata).
     */
    function getStatus(startTimeStr, endTimeStr, now) {
        var start = new Date(startTimeStr);
        var end = new Date(endTimeStr);
        if (now < start) return { key: 'soon', class: 'status-soon' };
        if (now > end) return { key: 'ended', class: 'status-ended' };
        return { key: 'live', class: 'status-live' };
    }
    
    /**
     * EN: Updates the status indicators of all lessons in the table without a full re-render.
     * IT: Aggiorna gli indicatori di stato di tutte le lezioni nella tabella senza un re-render completo.
     */
    function updateLessonStatus() {
        var rows = dom.lessonBody.querySelectorAll('tr');
        if (!rows.length || (rows.length === 1 && rows[0].querySelector('td[colspan="4"]'))) {
            return;
        }
        var now = new Date(new Date().getTime() + state.timeDifference);
        rows.forEach(function(row, index) {
            var lesson = state.lessons[index];
            if (lesson && lesson.start_time) {
                var status = getStatus(lesson.start_time, lesson.end_time, now);
                var statusIndicator = row.querySelector('.status-dot');
                var statusText = row.querySelector('.status-text');
                if (statusIndicator) {
                    statusIndicator.className = 'status-dot ' + status.class;
                }
                if(statusText) {
                    statusText.textContent = translations[state.currentLanguage].status[status.key];
                }
            }
        });
    }

    /**
     * EN: Renders the lessons into the table or displays a message (e.g., no lessons, error).
     * IT: Renderizza le lezioni nella tabella o mostra un messaggio (es. nessuna lezione, errore).
     */
    function renderLessons() {
        dom.lessonBody.innerHTML = '';
        if (state.fetchStatus === 'error' || !state.lessons.length || state.lessons[0].message) {
            dom.classroomName.textContent = state.lessons[0] ? state.lessons[0].classroom_name : 'Classroom';
            var messageKey = (state.fetchStatus === 'error') ? 'loadingError' : 'noLessons';
            showMessageInTable(messageKey);
            return;
        }

        var fragment = document.createDocumentFragment();
        var now = new Date(new Date().getTime() + state.timeDifference);
        
        state.lessons.forEach(function(lesson) {
            var start = new Date(lesson.start_time);
            var end = new Date(lesson.end_time);

            var timeOptions = { timeZone: 'Europe/Rome', hour: '2-digit', minute: '2-digit', hour12: false };
            var startTime = start.toLocaleTimeString('it-IT', timeOptions);
            var endTime = end.toLocaleTimeString('it-IT', timeOptions);
            var timeRange = startTime + ' - ' + endTime;

            var status = getStatus(lesson.start_time, lesson.end_time, now);
            var statusText = translations[state.currentLanguage].status[status.key];
            var row = document.createElement('tr');
            row.innerHTML = '<td>' + timeRange + '</td><td style="text-align: left;">' + lesson.lesson_name + '</td><td><div class="status-indicator"><span class="status-dot ' + status.class + '"></span><span class="status-text">' + statusText + '</span></div></td><td style="text-align: left;">' + lesson.instructor + '</td>';
            fragment.appendChild(row);
        });
        dom.lessonBody.appendChild(fragment);
        updateStaticUI();
        // EN: Delay scroll setup to allow the DOM to update. / IT: Ritarda l'impostazione dello scroll per permettere al DOM di aggiornarsi.
        setTimeout(setupAutoScroll, 100);
    }
    
    /**
     * EN: Fetches lesson data from the backend.
     * IT: Recupera i dati delle lezioni dal backend.
     */
    function fetchLessons() {
        var classroomId = state.params.get('classroom');
        var buildingId = state.params.get('building');
        var date = state.displayDate.toISOString().split('T')[0];
        var period = state.params.get('period') || 'all';

        if (!classroomId || !buildingId) {
            state.fetchStatus = 'error';
            renderLessons();
            return;
        }

        fetch('/schedule/lessons', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ classroom: classroomId, building: buildingId, date: date, period: period })
        })
        .then(function(response) {
            if (!response.ok) throw new Error('HTTP error! status: ' + response.status);
            return response.json();
        })
        .then(function(data) {
            state.fetchStatus = 'success';
            state.lessons = data;
            renderLessons();
        })
        .catch(function(error) {
            console.error('Failed to fetch lessons:', error);
            state.fetchStatus = 'error';
            state.lessons = [];
            renderLessons();
        });
    }
    
    var scrollAnimationId;
    /**
     * EN: Sets up a smooth, continuous scrolling animation if the table content overflows.
     * IT: Imposta un'animazione di scorrimento continuo e fluido se il contenuto della tabella è troppo lungo.
     */
    function setupAutoScroll() {
        var wrapper = document.querySelector('.scroll-body');
        if (!wrapper) return;
        var table = wrapper.querySelector('table');
        cancelAnimationFrame(scrollAnimationId);

        var wrapperHeight = wrapper.clientHeight;
        var tableHeight = table.scrollHeight;
        
        // EN: If no scrolling is needed, stop. / IT: Se non serve lo scroll, si ferma.
        if (tableHeight <= wrapperHeight) {
            table.style.transform = 'translateY(0)';
            return;
        }
        
        var position = 0;
        var direction = -1; // -1 for up, 1 for down
        var speed = 0.5;
        var pauseDuration = 3000; // 3 seconds
        var isPaused = true;
        setTimeout(function() { isPaused = false; }, pauseDuration);

        function animateScroll() {
            if (!isPaused) {
                position += direction * speed;
                var maxScroll = wrapperHeight - tableHeight;

                // EN: Reached the bottom, pause and reverse. / IT: Raggiunto il fondo, mette in pausa e inverte.
                if (position <= maxScroll) {
                    position = maxScroll;
                    direction = 1;
                    isPaused = true;
                    setTimeout(function() { isPaused = false; }, pauseDuration);
                } 
                // EN: Reached the top, pause and reverse. / IT: Raggiunta la cima, mette in pausa e inverte.
                else if (position >= 0) {
                    position = 0;
                    direction = -1;
                    isPaused = true;
                    setTimeout(function() { isPaused = false; }, pauseDuration);
                }
            }
            table.style.transform = 'translateY(' + position + 'px)';
            scrollAnimationId = requestAnimationFrame(animateScroll);
        }
        scrollAnimationId = requestAnimationFrame(animateScroll);
    }
    
    /**
     * EN: Hides the loader when the window is fully loaded.
     * IT: Nasconde il loader quando la finestra è completamente caricata.
     */
    window.onload = function() {
        var loader = document.getElementById('loader');
        if (loader) {
            loader.classList.add('hidden'); 
        }
    };
    
    /**
     * EN: The main initialization function.
     * IT: La funzione di inizializzazione principale.
     */
    function init() {
        dom.body.className = 'lang-' + state.currentLanguage;
        
        syncTimeWithServer();
        fetchLessons();
        
        var secondsCounter = 0;
        
        // EN: Main application loop, runs every second.
        // IT: Loop principale dell'applicazione, eseguito ogni secondo.
        setInterval(function() {
            secondsCounter++;
            updateClock();
            updateLessonStatus();
            
            if (secondsCounter % config.languageToggleInterval === 0) {
                toggleLanguage();
            }
            if (secondsCounter % config.dataRefreshInterval === 0) {
                fetchLessons();
                syncTimeWithServer();
            }
        }, 1000);

        // EN: Full page reload every few hours to prevent long-term issues.
        // IT: Ricarica completa della pagina ogni qualche ora per prevenire problemi a lungo termine.
        setTimeout(function() { 
            window.location.reload(true); 
        }, 4 * 60 * 60 * 1000);
    }

    init();
});