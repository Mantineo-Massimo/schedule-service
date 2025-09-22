/**
 * EN:
 * This script controls all the dynamic behavior of the `floor_view.html` page.
 * Its primary functions are similar to the classroom script but adapted for a floor-wide view:
 * - Fetching aggregated lesson data for all classrooms on a floor.
 * - Synchronizing time with a server endpoint.
 * - Updating the clock and date display.
 * - Periodically toggling the language between Italian and English.
 * - Rendering all lessons into a single, scrollable table.
 * - Managing the auto-scroll animation.
 *
 * IT:
 * Questo script controlla tutto il comportamento dinamico della pagina `floor_view.html`.
 * Le sue funzioni principali sono simili allo script dell'aula ma adattate per una vista a livello di piano:
 * - Recuperare i dati aggregati delle lezioni per tutte le aule di un piano.
 * - Sincronizzare l'ora con un endpoint del server.
 * - Aggiornare la visualizzazione dell'orologio e della data.
 * - Alternare periodicamente la lingua tra italiano e inglese.
 * - Renderizzare tutte le lezioni in un'unica tabella scorrevole.
 * - Gestire l'animazione di scorrimento automatico.
 */
document.addEventListener('DOMContentLoaded', function() {
    // EN: Centralized object for DOM element references.
    // IT: Oggetto centralizzato per i riferimenti agli elementi del DOM.
    var dom = {
        lessonBody: document.getElementById('lesson-body'),
        clock: document.getElementById('clock'),
        floorLabel: document.getElementById('floor-label'),
        currentDate: document.getElementById('current-date'),
        body: document.body
    };

    // EN: Centralized object for managing the application's dynamic state.
    // IT: Oggetto centralizzato per la gestione dello stato dinamico dell'applicazione.
    var state = {
        currentLanguage: 'it',
        lessons: [],
        fetchStatus: 'loading',
        params: new URLSearchParams(window.location.search),
        timeDifference: 0,
        get displayDate() {
            var dateStr = this.params.get('date') || new Date().toISOString().split('T')[0];
            return new Date(dateStr + 'T12:00:00');
        }
    };

    // EN: Centralized object for static configuration values.
    // IT: Oggetto centralizzato per i valori di configurazione statici.
    var config = {
        timeServiceUrl: '/api/time/',
        languageToggleInterval: 15, // seconds
        dataRefreshInterval: 5 * 60, // seconds
    };
    
    // EN: Object containing all translation strings.
    // IT: Oggetto contenente tutte le stringhe di traduzione.
    var translations = {
        it: {
            days: ["Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"],
            months: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
            floor: "Piano",
            building: { "A": "Edificio A", "B": "Edificio B", "SBA": "Edificio SBA" },
            noLessons: "Nessuna lezione trovata per questo piano al momento",
            missingParams: "Parametri 'building' o 'floor' mancanti",
            loadingError: "Errore nel caricamento delle lezioni"
        },
        en: {
            days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            floor: "Floor",
            building: { "A": "Building A", "B": "Building B", "SBA": "Building SBA" },
            noLessons: "No lessons found for this floor at the moment",
            missingParams: "Missing 'building' or 'floor' parameters",
            loadingError: "Error loading lessons"
        }
    };

    /**
     * EN: Syncs the local time with the server's time.
     * IT: Sincronizza l'ora locale con quella del server.
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
                state.timeDifference = 0;
                dom.clock.style.color = 'red';
            });
    }

    /**
     * EN: Updates the clock display every second.
     * IT: Aggiorna l'orologio ogni secondo.
     */
    function updateClock() {
        var serverTime = new Date(new Date().getTime() + state.timeDifference);
        var clockOptions = { timeZone: 'Europe/Rome', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        dom.clock.textContent = serverTime.toLocaleTimeString('it-IT', clockOptions);
    }
    
    /**
     * EN: Updates the static UI elements like date and floor label.
     * IT: Aggiorna gli elementi statici dell'interfaccia come data ed etichetta del piano.
     */
    function updateStaticUI() {
        var lang = translations[state.currentLanguage];
        var displayDate = state.displayDate;
        var dayName = lang.days[displayDate.getUTCDay()];
        var monthName = lang.months[displayDate.getUTCMonth()];
        dom.currentDate.textContent = dayName + ' ' + displayDate.getUTCDate() + ' ' + monthName + ' ' + displayDate.getUTCFullYear();
        
        var buildingKey = state.params.get('building') ? state.params.get('building').toUpperCase() : null;
        var floorNumber = state.params.get('floor');
        if (buildingKey && floorNumber) {
            var buildingName = lang.building[buildingKey] || buildingKey;
            dom.floorLabel.textContent = buildingName + ' - ' + lang.floor + ' ' + floorNumber;
        }
    }
    
    /**
     * EN: Toggles the display language and updates all text content.
     * IT: Cambia la lingua di visualizzazione e aggiorna tutto il contenuto testuale.
     */
    function toggleLanguage() {
        state.currentLanguage = (state.currentLanguage === 'en') ? 'it' : 'en';
        dom.body.className = 'lang-' + state.currentLanguage;
        updateStaticUI();
        if (dom.lessonBody.querySelector('td[colspan="4"]')) {
            var messageKey = (state.fetchStatus === 'error') ? 'loadingError' : 'noLessons';
            showMessageInTable(messageKey);
        }
    }

    /**
     * EN: Displays a message in the table.
     * IT: Mostra un messaggio nella tabella.
     */
    function showMessageInTable(messageKey) {
        var message = translations[state.currentLanguage][messageKey];
        dom.lessonBody.innerHTML = '<tr><td colspan="4">' + message + '</td></tr>';
    }

    /**
     * EN: Renders the lessons into the table.
     * IT: Renderizza le lezioni nella tabella.
     */
    function renderLessons() {
        dom.lessonBody.innerHTML = '';
        if (state.fetchStatus === 'error' || !state.lessons.length) {
            var messageKey = (state.fetchStatus === 'error') ? 'loadingError' : 'noLessons';
            showMessageInTable(messageKey);
            return;
        }

        var fragment = document.createDocumentFragment();
        state.lessons.forEach(function(lesson) {
            var start = new Date(lesson.start_time);
            var end = new Date(lesson.end_time);

            var timeOptions = { timeZone: 'Europe/Rome', hour: '2-digit', minute: '2-digit', hour12: false };
            var startTime = start.toLocaleTimeString('it-IT', timeOptions);
            var endTime = end.toLocaleTimeString('it-IT', timeOptions);
            var timeRange = startTime + ' - ' + endTime;
            
            var row = document.createElement('tr');
            row.innerHTML = '<td>' + lesson.classroom_name + '</td><td>' + timeRange + '</td><td style="text-align: left;">' + lesson.lesson_name + '</td><td style="text-align: left;">' + lesson.instructor + '</td>';
            fragment.appendChild(row);
        });
        dom.lessonBody.appendChild(fragment);
        setTimeout(setupAutoScroll, 100);
    }

    /**
     * EN: Fetches lesson data for the entire floor from the backend.
     * IT: Recupera i dati delle lezioni per l'intero piano dal backend.
     */
    function fetchLessons() {
        var building = state.params.get('building');
        var floor = state.params.get('floor');
        var date = state.displayDate.toISOString().split('T')[0];

        if (!building || !floor) {
            state.fetchStatus = 'error';
            showMessageInTable('missingParams');
            return;
        }

        fetch('/schedule/floor/' + building + '/' + floor + '?date=' + date)
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
     * EN: Sets up a smooth, continuous scrolling animation.
     * IT: Imposta un'animazione di scorrimento continuo e fluido.
     */
    function setupAutoScroll() {
        var wrapper = document.querySelector('.scroll-body');
        if (!wrapper) return;
        var table = wrapper.querySelector('table');
        cancelAnimationFrame(scrollAnimationId);

        var wrapperHeight = wrapper.clientHeight;
        var tableHeight = table.scrollHeight;

        if (tableHeight <= wrapperHeight) {
            table.style.transform = 'translateY(0)';
            return;
        }

        var position = 0;
        var direction = -1;
        var speed = 0.5;
        var pauseDuration = 3000;
        var isPaused = true;
        setTimeout(function() { isPaused = false; }, pauseDuration);

        function animateScroll() {
            if (!isPaused) {
                position += direction * speed;
                var maxScroll = wrapperHeight - tableHeight;

                if (position <= maxScroll) {
                    position = maxScroll;
                    direction = 1;
                    isPaused = true;
                    setTimeout(function() { isPaused = false; }, pauseDuration);
                } else if (position >= 0) {
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
        updateStaticUI();
        fetchLessons();
        
        var secondsCounter = 0;
        
        setInterval(function() {
            secondsCounter++;
            updateClock();
            if (secondsCounter % config.languageToggleInterval === 0) {
                toggleLanguage();
            }
            if (secondsCounter % config.dataRefreshInterval === 0) {
                fetchLessons();
                syncTimeWithServer();
            }
        }, 1000);

        setTimeout(function() { 
            window.location.reload(true); 
        }, 4 * 60 * 60 * 1000);
    }

    init();
});