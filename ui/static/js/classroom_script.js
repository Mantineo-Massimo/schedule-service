/**
 * Script for the Classroom Schedule View.
 * Fetches and displays lessons for a single classroom, supports bilingual text,
 * and handles automatic scrolling for long lists of lessons.
 */
document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const dom = {
        lessonBody: document.getElementById('lesson-body'),
        clock: document.getElementById('clock'),
        classroomName: document.getElementById('classroom-name'),
        currentDate: document.getElementById('current-date'),
        body: document.body
    };

    // --- State and Configuration ---
    let state = {
        currentLanguage: 'en',
        lessons: []
    };
    const config = {
        apiEndpoint: '/lessons',
        languageToggleInterval: 15000,
        dataRefreshInterval: 5 * 60 * 1000 // 5 minutes
    };

    // --- Language Data ---
    const translations = {
        it: {
            days: ["Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"],
            months: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
            status: { soon: 'Futura', live: 'In corso', ended: 'Terminata' },
            noLessons: 'Nessuna lezione disponibile'
        },
        en: {
            days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            status: { soon: 'Upcoming', live: 'Ongoing', ended: 'Ended' },
            noLessons: 'No lessons available'
        }
    };

    // --- Utility Functions ---
    const getUrlParams = () => new URLSearchParams(window.location.search);
    const padZero = (n) => String(n).padStart(2, '0');
    
    // --- UI Update Functions ---
    function updateClockAndDate(dateStr) {
        const now = new Date();
        dom.clock.textContent = `${padZero(now.getHours())}:${padZero(now.getMinutes())}:${padZero(now.getSeconds())}`;
        
        const displayDate = new Date(dateStr + 'T12:00:00');
        const lang = translations[state.currentLanguage];
        const dayName = lang.days[displayDate.getUTCDay()];
        const monthName = lang.months[displayDate.getUTCMonth()];
        dom.currentDate.textContent = `${dayName} ${displayDate.getUTCDate()} ${monthName} ${displayDate.getUTCFullYear()}`;
    }
    
    function toggleLanguage() {
        state.currentLanguage = (state.currentLanguage === 'en') ? 'it' : 'en';
        dom.body.classList.toggle('lang-en');
        dom.body.classList.toggle('lang-it');
        renderLessons(state.lessons);
        const params = getUrlParams();
        updateClockAndDate(params.get('date') || new Date().toISOString().split('T')[0]);
    }

    function getStatus(startTimeStr, endTimeStr) {
        const now = new Date();
        const start = new Date(startTimeStr);
        const end = new Date(endTimeStr);
        if (now < start) return { key: 'soon', class: 'status-soon' };
        if (now > end) return { key: 'ended', class: 'status-ended' };
        return { key: 'live', class: 'status-live' };
    }

    function renderLessons(lessons) {
        state.lessons = lessons;
        dom.lessonBody.innerHTML = '';

        // Logica corretta: imposta il nome dell'aula in ogni caso
        dom.classroomName.textContent = lessons[0]?.classroom_name || 'Classroom';

        if (!lessons.length || lessons[0].message) {
            const noLessonsMsg = translations[state.currentLanguage].noLessons;
            dom.lessonBody.innerHTML = `<tr><td colspan="4">${noLessonsMsg}</td></tr>`;
            return;
        }
        
        lessons.forEach(lesson => {
            const start = new Date(lesson.start_time);
            const end = new Date(lesson.end_time);
            const timeRange = `${padZero(start.getHours())}:${padZero(start.getMinutes())} - ${padZero(end.getHours())}:${padZero(end.getMinutes())}`;
            const status = getStatus(lesson.start_time, lesson.end_time);
            const statusText = translations[state.currentLanguage].status[status.key];

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${timeRange}</td>
                <td style="text-align: left;">${lesson.lesson_name}</td>
                <td>
                    <div class="status-indicator">
                        <span class="status-dot ${status.class}"></span>
                        <span>${statusText}</span>
                    </div>
                </td>
                <td style="text-align: left;">${lesson.instructor}</td>
            `;
            dom.lessonBody.appendChild(row);
        });
        
        setupAutoScroll();
    }
    
    // --- Data Fetching ---
    async function fetchLessons() {
        const params = getUrlParams();
        const classroomId = params.get('classroom');
        const buildingId = params.get('building');
        const date = params.get('date') || new Date().toISOString().split('T')[0];
        const period = params.get('period') || 'all';

        if (!classroomId || !buildingId) {
            dom.lessonBody.innerHTML = `<tr><td colspan="4">Missing 'classroom' or 'building' URL parameter.</td></tr>`;
            return;
        }

        try {
            const response = await fetch(config.apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ classroom: classroomId, building: buildingId, date, period })
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            renderLessons(data);
        } catch (error) {
            console.error('Failed to fetch lessons:', error);
            dom.lessonBody.innerHTML = `<tr><td colspan="4">Error loading lessons.</td></tr>`;
        }
        updateClockAndDate(date);
    }
    
    // --- Auto-Scrolling ---
    let scrollAnimationId;
    function setupAutoScroll() {
        const wrapper = document.querySelector('.scroll-body');
        const table = wrapper.querySelector('table');
        cancelAnimationFrame(scrollAnimationId);

        const wrapperHeight = wrapper.clientHeight;
        const tableHeight = table.scrollHeight;

        if (tableHeight <= wrapperHeight) {
            table.style.transform = 'translateY(0)';
            return;
        }

        let position = 0;
        let direction = -1;
        const speed = 0.5;
        const pauseDuration = 3000;
        let pauseTimeout;

        function animateScroll() {
            position += direction * speed;
            table.style.transform = `translateY(${position}px)`;

            const maxScroll = wrapperHeight - tableHeight;
            if (position <= maxScroll || position >= 0) {
                direction *= -1;
                clearTimeout(pauseTimeout);
                pauseTimeout = setTimeout(() => {
                    scrollAnimationId = requestAnimationFrame(animateScroll);
                }, pauseDuration);
            } else {
                scrollAnimationId = requestAnimationFrame(animateScroll);
            }
        }
        setTimeout(() => scrollAnimationId = requestAnimationFrame(animateScroll), pauseDuration);
    }

    // --- Initialization ---
    fetchLessons();
    setInterval(fetchLessons, config.dataRefreshInterval);
    setInterval(toggleLanguage, config.languageToggleInterval);
    setInterval(() => {
       const params = getUrlParams();
       updateClockAndDate(params.get('date') || new Date().toISOString().split('T')[0]);
    }, 1000);
});