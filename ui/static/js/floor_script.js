/**
 * Script for the Floor Schedule View - Legacy, Optimized, and Bug-Fixed Version.
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
        fetchStatus: 'loading', // 'loading', 'success', 'error'
        params: new URLSearchParams(window.location.search),
        get displayDate() {
            var dateStr = this.params.get('date') || new Date().toISOString().split('T')[0];
            return new Date(dateStr + 'T12:00:00');
        }
    };

    var config = {
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

    // MODIFIED FOR COMPATIBILITY WITH OLDER BROWSERS
    var padZero = function(n) { return n < 10 ? '0' + n : String(n); };

    function updateClock() {
        var now = new Date();
        dom.clock.textContent = padZero(now.getHours()) + ':' + padZero(now.getMinutes()) + ':' + padZero(now.getSeconds());
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
        // Se è mostrato un messaggio, ritraducilo
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
            var timeRange = padZero(start.getHours()) + ':' + padZero(start.getMinutes()) + ' - ' + padZero(end.getHours()) + ':' + padZero(end.getMinutes());
            var row = document.createElement('tr');
            row.innerHTML = '<td>' + lesson.classroom_name + '</td><td>' + timeRange + '</td><td style="text-align: left;">' + lesson.lesson_name + '</td><td style="text-align: left;">' + lesson.instructor + '</td>';
            fragment.appendChild(row);
        });
        dom.lessonBody.appendChild(fragment);
        setTimeout(setupAutoScroll, 100);
    }

    function fetchLessons() {
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

    function init() {
        dom.body.className = 'lang-' + state.currentLanguage;
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
            }
        }, 1000);
    }

    init();
});
