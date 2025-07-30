/**
 * Script for the Classroom Schedule View - Legacy Browser Compatible Version.
 */
document.addEventListener('DOMContentLoaded', function() {
    // --- Riferimenti al DOM ---
    var dom = {
        lessonBody: document.getElementById('lesson-body'),
        clock: document.getElementById('clock'),
        classroomName: document.getElementById('classroom-name'),
        currentDate: document.getElementById('current-date'),
        body: document.body
    };

    // --- Stato e Configurazione Centralizzati ---
    var state = {
        currentLanguage: 'it',
        lessons: [],
        params: new URLSearchParams(window.location.search),
        get displayDate() {
            var dateStr = this.params.get('date') || new Date().toISOString().split('T')[0];
            return new Date(dateStr + 'T12:00:00');
        }
    };

    var config = {
        apiEndpoint: 'lessons',
        languageToggleInterval: 15,
        dataRefreshInterval: 5 * 60,
    };

    var translations = {
        it: {
            days: ["Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"],
            months: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
            status: { soon: 'Futura', live: 'In corso', ended: 'Terminata' },
            noLessons: 'Nessuna lezione disponibile',
            missingParams: "Parametri 'classroom' o 'building' mancanti.",
            loadingError: "Errore nel caricamento delle lezioni."
        },
        en: {
            days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            status: { soon: 'Upcoming', live: 'Ongoing', ended: 'Ended' },
            noLessons: 'No lessons available',
            missingParams: "Missing 'classroom' or 'building' parameters.",
            loadingError: "Error loading lessons."
        }
    };

    var padZero = function(n) { return String(n).padStart(2, '0'); };

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
        if (state.lessons.length > 0) {
            dom.classroomName.textContent = state.lessons[0] ? state.lessons[0].classroom_name : 'Classroom';
        }
    }

    function updateLanguageStrings() {
        updateStaticUI();
        var rows = dom.lessonBody.querySelectorAll('tr');
        if (rows.length > 0 && state.lessons.length > 0 && !state.lessons[0].message) {
            rows.forEach(function(row, index) {
                var lesson = state.lessons[index];
                if (lesson) {
                    var status = getStatus(lesson.start_time, lesson.end_time);
                    var statusText = translations[state.currentLanguage].status[status.key];
                    var statusElement = row.querySelector('.status-text');
                    if (statusElement) {
                        statusElement.textContent = statusText;
                    }
                }
            });
        } else if (dom.lessonBody.querySelector('td[colspan="4"]')) {
            var currentMessageKey = state.lessons.length ? 'noLessons' : 'loadingError';
            showMessageInTable(currentMessageKey);
        }
    }

    function toggleLanguage() {
        state.currentLanguage = (state.currentLanguage === 'en') ? 'it' : 'en';
        dom.body.className = 'lang-' + state.currentLanguage;
        updateLanguageStrings();
    }

    function showMessageInTable(messageKey) {
        var message = translations[state.currentLanguage][messageKey];
        dom.lessonBody.innerHTML = '<tr><td colspan="4">' + message + '</td></tr>';
    }

    function getStatus(startTimeStr, endTimeStr) {
        var now = new Date();
        var start = new Date(startTimeStr);
        var end = new Date(endTimeStr);
        if (now < start) return { key: 'soon', class: 'status-soon' };
        if (now > end) return { key: 'ended', class: 'status-ended' };
        return { key: 'live', class: 'status-live' };
    }

    function renderLessons() {
        dom.lessonBody.innerHTML = '';
        if (!state.lessons.length || state.lessons[0].message) {
            dom.classroomName.textContent = state.lessons[0] ? state.lessons[0].classroom_name : 'Classroom';
            var messageKey = state.lessons.length ? 'noLessons' : 'loadingError';
            showMessageInTable(messageKey);
            return;
        }
        var fragment = document.createDocumentFragment();
        state.lessons.forEach(function(lesson) {
            var start = new Date(lesson.start_time);
            var end = new Date(lesson.end_time);
            var timeRange = padZero(start.getHours()) + ':' + padZero(start.getMinutes()) + ' - ' + padZero(end.getHours()) + ':' + padZero(end.getMinutes());
            var status = getStatus(lesson.start_time, lesson.end_time);
            var statusText = translations[state.currentLanguage].status[status.key];
            var row = document.createElement('tr');
            row.innerHTML = '<td>' + timeRange + '</td><td style="text-align: left;">' + lesson.lesson_name + '</td><td><div class="status-indicator"><span class="status-dot ' + status.class + '"></span><span class="status-text">' + statusText + '</span></div></td><td style="text-align: left;">' + lesson.instructor + '</td>';
            fragment.appendChild(row);
        });
        dom.lessonBody.appendChild(fragment);
        updateStaticUI();
        setTimeout(setupAutoScroll, 100);
    }

    function fetchLessons() {
        var classroomId = state.params.get('classroom');
        var buildingId = state.params.get('building');
        var date = state.displayDate.toISOString().split('T')[0];
        var period = state.params.get('period') || 'all';
        if (!classroomId || !buildingId) {
            showMessageInTable('missingParams');
            return;
        }
        fetch('lessons', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ classroom: classroomId, building: buildingId, date: date, period: period })
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP error! status: ' + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            state.lessons = data;
            renderLessons();
        })
        .catch(function(error) {
            console.error('Failed to fetch lessons:', error);
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
