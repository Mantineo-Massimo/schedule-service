/**
 * EN: Floor-wide view script.
 * IT: Script per la vista delle lezioni di un piano.
 */

/**
 * EN:
 * - Fetches all classrooms on a floor via /floor/<floor>
 * - Renders lessons in a scrollable table
 * - Updates clock and language periodically
 * 
 * IT:
 * - Recupera tutte le aule di un piano tramite /floor/<floor>
 * - Rende le lezioni in una tabella scorrevole
 * - Aggiorna l'orologio e la lingua periodicamente
 */

(function () {
  const lessonBody      = document.getElementById('lesson-body');
  const clockElem       = document.getElementById('clock');
  const currentDateElem = document.getElementById('current-date');
  const floorLabelElem  = document.getElementById('floor-label');

  let floor = window.location.pathname
    .split('/')
    .pop()
    .replace('.html', '')
    .toLowerCase();

  const qp           = new URLSearchParams(window.location.search);
  const selectedDate = qp.get('date') || new Date().toISOString().split('T')[0];
  const API_URL      = `${window.location.origin}/floor/${floor}`;
  let lastData       = [];

  const LANGS        = ['it', 'en'];
  let langIndex      = 0;
  let currentLang    = LANGS[langIndex];
  let autoScrollInitialized = false;

  const floorNames = {
    floor0:  { it: 'Piano 0',  en: 'Floor 0'  },
    floor1:  { it: 'Piano 1',  en: 'Floor 1'  },
    floorm1:{ it: 'Piano -1', en: 'Floor -1' }
  };

  const translations = {
    it: {
      headers:   ['AULA', 'ORA', 'NOME LEZIONE', 'PROFESSORE'],
      noClasses: 'Nessuna lezione imminente',
      dateOpts: {
        locale: 'it-IT',
        options: { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }
      },
      timeOpts: {
        locale: 'it-IT',
        options: { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }
      }
    },
    en: {
      headers:   ['CLASSROOM', 'TIME', 'LESSON NAME', 'PROFESSOR'],
      noClasses: 'No upcoming lessons',
      dateOpts: {
        locale: 'en-GB',
        options: { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }
      },
      timeOpts: {
        locale: 'en-GB',
        options: { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }
      }
    }
  };

  function pad2(n) {
    return (n < 10 ? '0' : '') + n;
  }

  function updateHeaders() {
    document.querySelectorAll('thead th').forEach((th, i) => {
      th.textContent = translations[currentLang].headers[i];
    });
  }

  function updateCurrentDate() {
    const { locale, options } = translations[currentLang].dateOpts;
    const txt = new Date(selectedDate).toLocaleDateString(locale, options);
    currentDateElem.textContent = txt.charAt(0).toUpperCase() + txt.slice(1);
  }

  function updateClock() {
    const { locale, options } = translations[currentLang].timeOpts;
    clockElem.textContent = new Date().toLocaleTimeString(locale, options);
  }

  function updateFloorLabel() {
    const names = floorNames[floor] || {};
    floorLabelElem.textContent = names[currentLang] || floor;
  }

  function renderLessons(data) {
    const scrollBody = document.querySelector('.scroll-body');
    const scrollTop = scrollBody ? scrollBody.scrollTop : 0;

    lessonBody.innerHTML = '';
    if (!data.length) {
      lessonBody.innerHTML = `<tr><td colspan="4">${translations[currentLang].noClasses}</td></tr>`;
      return;
    }

    data.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));

    data.forEach(l => {
      const s = new Date(l.start_time), e = new Date(l.end_time);
      const tm = `${pad2(s.getHours())}:${pad2(s.getMinutes())} – ${pad2(e.getHours())}:${pad2(e.getMinutes())}`;
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${l.classroom_name || 'N/A'}</td>
        <td>${tm}</td>
        <td>${l.lesson_name || 'N/A'}</td>
        <td>${l.instructor  || 'N/A'}</td>
      `;
      lessonBody.appendChild(row);
    });

    if (scrollBody) scrollBody.scrollTop = scrollTop;
  }

  function setupAutoScroll() {
    if (autoScrollInitialized) return;
    autoScrollInitialized = true;

    const w = document.querySelector('.scroll-body');
    const c = lessonBody;
    if (!w || !c) return;

    let dir = -1, pos = 0, step = 1, delay = 30, pause = 3000;
    c.style.transform = 'translateY(0)';
    function stepScroll() {
      const wh = w.clientHeight, ch = c.scrollHeight;
      if (ch <= wh) return;
      pos += step * dir;
      c.style.transform = `translateY(${pos}px)`;
      const max = wh - ch;
      if (pos <= max) {
        dir = 1;
        setTimeout(stepScroll, pause);
      } else if (pos >= 0) {
        dir = -1;
        setTimeout(stepScroll, pause);
      } else {
        setTimeout(stepScroll, delay);
      }
    }
    setTimeout(stepScroll, pause);
  }

  function toggleLanguage() {
    langIndex = 1 - langIndex;
    currentLang = LANGS[langIndex];
    document.body.classList.toggle('lang-it');
    document.body.classList.toggle('lang-en');
    updateHeaders();
    updateCurrentDate();
    updateClock();
    updateFloorLabel();
    renderLessons(lastData);
  }

  // EN/IT: Initialization /Inizializzazione
  document.body.classList.add('lang-it');
  updateFloorLabel();
  fetch(`${API_URL}?date=${selectedDate}`)
    .then(r => {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    })
    .then(data => {
      lastData = data;
      updateHeaders();
      updateCurrentDate();
      updateClock();
      renderLessons(data);
      setupAutoScroll();
    })
    .catch(err => {
      lessonBody.innerHTML = `<tr><td colspan="4">Errore: ${err.message}</td></tr>`;
    });

  setInterval(toggleLanguage, 15000);
  setInterval(updateClock, 1000);
})();
