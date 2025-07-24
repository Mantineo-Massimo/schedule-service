/**
 * Script for the Floor Schedule View.
 */
document.addEventListener('DOMContentLoaded', () => {
    const dom = {
        lessonBody: document.getElementById('lesson-body'),
        clock: document.getElementById('clock'),
        floorLabel: document.getElementById('floor-label'),
        currentDate: document.getElementById('current-date'),
        body: document.body
    };

    let state = { currentLanguage: 'it' };
    const config = {
        languageToggleInterval: 15000,
        dataRefreshInterval: 5 * 60 * 1000
    };

    const translations = {
        it: {
            days: ["Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"],
            months: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
            floor: "Piano",
            building: { "A": "Edificio A", "B": "Edificio B", "SBA": "Edificio SBA" }
        },
        en: {
            days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            floor: "Floor",
            building: { "A": "Building A", "B": "Building B", "SBA": "Building SBA" }
        }
    };

    const getUrlParams = () => new URLSearchParams(window.location.search);
    const padZero = (n) => String(n).padStart(2, '0');

    function updateClockAndDate(dateStr) {
        const now = new Date();
        dom.clock.textContent = `${padZero(now.getHours())}:${padZero(now.getMinutes())}:${padZero(now.getSeconds())}`;
        const displayDate = new Date(dateStr + 'T12:00:00');
        const lang = translations[state.currentLanguage];
        const dayName = lang.days[displayDate.getUTCDay()];
        const monthName = lang.months[displayDate.getUTCMonth()];
        dom.currentDate.textContent = `${dayName} ${displayDate.getUTCDate()} ${monthName} ${displayDate.getUTCFullYear()}`;
    }

    function updateFloorLabel() {
        const params = getUrlParams();
        const buildingKey = params.get('building')?.toUpperCase();
        const floorNumber = params.get('floor');
        if (!buildingKey || !floorNumber) return;
        const lang = translations[state.currentLanguage];
        const buildingName = lang.building[buildingKey] || buildingKey;
        const floorText = lang.floor;
        dom.floorLabel.textContent = `${buildingName} - ${floorText} ${floorNumber}`;
    }

    function toggleLanguage() {
        state.currentLanguage = (state.currentLanguage === 'en') ? 'it' : 'en';
        dom.body.classList.toggle('lang-en');
        dom.body.classList.toggle('lang-it');
        const params = getUrlParams();
        updateClockAndDate(params.get('date') || new Date().toISOString().split('T')[0]);
        updateFloorLabel();
    }
    
    function renderLessons(lessons) {
        dom.lessonBody.innerHTML = '';
        if (!lessons.length) {
            dom.lessonBody.innerHTML = `<tr><td colspan="4">Nessuna lezione trovata per questo piano.</td></tr>`;
            return;
        }
        lessons.forEach(lesson => {
            const start = new Date(lesson.start_time);
            const end = new Date(lesson.end_time);
            const timeRange = `${padZero(start.getHours())}:${padZero(start.getMinutes())} - ${padZero(end.getHours())}:${padZero(end.getMinutes())}`;
            const row = document.createElement('tr');
            row.innerHTML = `<td>${lesson.classroom_name}</td><td>${timeRange}</td><td style="text-align: left;">${lesson.lesson_name}</td><td style="text-align: left;">${lesson.instructor}</td>`;
            dom.lessonBody.appendChild(row);
        });
    }
    
    async function fetchLessons() {
        const params = getUrlParams();
        const buildingKey = params.get('building');
        const floor = params.get('floor');
        const date = params.get('date') || new Date().toISOString().split('T')[0];

        if (!buildingKey || !floor) {
            dom.lessonBody.innerHTML = `<tr><td colspan="4">Parametri 'building' o 'floor' mancanti.</td></tr>`;
            return;
        }
        
        try {
            // MODIFICA: Usa la chiave breve ('A', 'B', etc.) direttamente nella chiamata API
            const response = await fetch(`floor/${buildingKey}/${floor}?date=${date}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            renderLessons(data);
        } catch (error) {
            console.error('Failed to fetch lessons:', error);
            dom.lessonBody.innerHTML = `<tr><td colspan="4">Errore nel caricamento delle lezioni.</td></tr>`;
        }
        
        updateClockAndDate(date);
        updateFloorLabel();
    }
    
    dom.body.classList.add('lang-it');
    dom.body.classList.remove('lang-en');
    fetchLessons();
    setInterval(fetchLessons, config.dataRefreshInterval);
    setInterval(toggleLanguage, config.languageToggleInterval);
    setInterval(() => {
        const params = getUrlParams();
        updateClockAndDate(params.get('date') || new Date().toISOString().split('T')[0]);
    }, 1000);
});