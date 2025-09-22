/**
 * Script for the Floor Schedule View - FINAL VERSION with Nginx Proxy Time Sync.
 */
document.addEventListener('DOMContentLoaded', function() {
    // --- Riferimenti al DOM ---
    var dom = {
        lessonBody: document.getElementById('lesson-body'),
        clock: document.getElementById('clock'),
        floorLabel: document.getElementById('floor-label'),
        currentDate: document.getElementById('current-date'),
        body: document.body
    };

    // --- Stato e Configurazione Centralizzati ---
    var state = {
        currentLanguage: 'it',
        lessons: [],
        fetchStatus: 'loading',
        params: new URLSearchParams(window.location.search),
        timeDifference: 0, // Differenza tra ora del server e ora locale
        get displayDate() {
            var dateStr = this.params.get('date') || new Date().toISOString().split('T')[0];
            return new Date(dateStr + 'T12:00:00');
        }
    };

    var config = {
        // L'URL ora punta al percorso gestito da Nginx
        timeServiceUrl: 'http://172.16.32.13/api/time/', 
        languageToggleInterval: 15,
        dataRefreshInterval: 5 * 60,
    };
    
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

    var padZero = function(n) { return n < 10 ? '0' + n : String(n); };

    // VERSIONE NUOVA E CORRETTA
    function updateClock() {
        // Calcoliamo l'ora del server stimata
        var serverTime = new Date(new Date().getTime() + state.timeDifference);

        // Opzioni per formattare l'ora nel fuso orario di Roma, includendo i secondi
        var clockOptions = {
            timeZone: 'Europe/Rome',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        };
        
        // Usiamo lo stesso metodo delle lezioni per garantire coerenza
        dom.clock.textContent = serverTime.toLocaleTimeString('it-IT', clockOptions);
    }

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
    
    function toggleLanguage() {
        state.currentLanguage = (state.currentLanguage === 'en') ? 'it' : 'en';
        dom.body.className = 'lang-' + state.currentLanguage;
        updateStaticUI();
        if (dom.lessonBody.querySelector('td[colspan="4"]')) {
            var messageKey = (state.fetchStatus === 'error') ? 'loadingError' : 'noLessons';
            showMessageInTable(messageKey);
        }
    }

    function showMessageInTable(messageKey) {
        var message = translations[state.currentLanguage][messageKey];
        dom.lessonBody.innerHTML = '<tr><td colspan="4">' + message + '</td></tr>';
    }

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

            // Opzioni per formattare l'ora nel fuso orario di Roma
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

    function fetchLessons() {
        try {
            var building = state.params.get('building');
            var floor = state.params.get('floor');
            var date = state.displayDate.toISOString().split('T')[0];
            if (!building || !floor) {
                state.fetchStatus = 'error';
                showMessageInTable('missingParams');
                return;
            }
            fetch('floor/' + building + '/' + floor + '?date=' + date)
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('HTTP error! status: ' + response.status);
                    }
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
        } catch (e) {
            console.error("Errore critico in fetchLessons:", e);
        }
    }
    
    var scrollAnimationId;
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

    window.onload = function() {
        var loader = document.getElementById('loader');
        if (loader) {
            loader.classList.add('hidden');
        }
    };
    
    function init() {
        dom.body.className = 'lang-' + state.currentLanguage;
        
        syncTimeWithServer();
        updateStaticUI();
        fetchLessons();
        
        var secondsCounter = 0;
        
        setInterval(function() {
            try {
                secondsCounter++;
                updateClock();
                if (secondsCounter % config.languageToggleInterval === 0) {
                    toggleLanguage();
                }
                if (secondsCounter % config.dataRefreshInterval === 0) {
                    fetchLessons();
                    syncTimeWithServer();
                }
            } catch (e) {
                console.error("Errore nell'intervallo principale:", e);
            }
        }, 1000);

        setTimeout(function() { 
            window.location.reload(true); 
        }, 4 * 60 * 60 * 1000);
    }

    init();
});