/**
 * EN: Floor-wide view script, corrected and optimized.
 * IT: Script per la vista delle lezioni di un piano, corretto e ottimizzato.
 */
(function () {
  // ----- Elementi DOM -----
  const lessonBody     = document.getElementById('lesson-body');
  const clockElem      = document.getElementById('clock');
  const dateElem       = document.getElementById('current-date');
  const floorLabelElem = document.getElementById('floor-label');

  // ----- Lettura parametri da URL -----
  const qp        = new URLSearchParams(window.location.search);
  const building  = qp.get('building');
  const floorNum  = qp.get('floor');
  const selDate   = qp.get('date') || new Date().toISOString().split('T')[0];

  if (!building || !floorNum) {
    lessonBody.innerHTML = '<tr><td colspan="4">Missing "building" or "floor" parameter</td></tr>';
    return;
  }

  // ----- Costruzione endpoint API -----
  const apiUrl = `${window.location.origin}/floor/${encodeURIComponent(building)}/${encodeURIComponent(floorNum)}?date=${selDate}`;

  let lastData   = [];
  let scrollInit = false;

  // ----- Lingue e traduzioni -----
  const LANGS     = ['it', 'en'];
  let langIndex   = 0;
  let currentLang = LANGS[langIndex];

  const buildingNames = {
    EdificioA:   { it: 'Edificio A',    en: 'Building A' },
    EdificioB:   { it: 'Edificio B',    en: 'Building B' },
    EdificioSBA: { it: 'Edificio SBA',  en: 'Building SBA' }
  };

  const translations = {
    it: {
      headers:   ['AULA', 'ORA', 'NOME LEZIONE', 'PROFESSORE'],
      noClasses: 'Nessuna lezione disponibile',
      dateOpts:  { locale:'it-IT', options:{ weekday:'long', day:'numeric', month:'long', year:'numeric' } },
      timeOpts:  { locale:'it-IT', options:{ hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:false } }
    },
    en: {
      headers:   ['CLASSROOM', 'TIME', 'LESSON NAME', 'PROFESSOR'],
      noClasses: 'No lessons available',
      dateOpts:  { locale:'en-GB', options:{ weekday:'long', day:'numeric', month:'long', year:'numeric' } },
      timeOpts:  { locale:'en-GB', options:{ hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:false } }
    }
  };

  // ----- Helpers -----
  function pad2(n) {
    return (n < 10 ? '0' : '') + n;
  }

  function updateHeaders() {
    document.querySelectorAll('thead th').forEach((th, i) => {
      th.textContent = translations[currentLang].headers[i];
    });
  }

  function updateDate() {
    const { locale, options } = translations[currentLang].dateOpts;
    const txt = new Date(selDate).toLocaleDateString(locale, options);
    dateElem.textContent = txt.charAt(0).toUpperCase() + txt.slice(1);
  }

  function updateClock() {
    const { locale, options } = translations[currentLang].timeOpts;
    clockElem.textContent = new Date().toLocaleTimeString(locale, options);
  }

  function updateLabel() {
    const names = buildingNames[building] || {};
    const buildingLabel = (names[currentLang] || building);
    const floorLabel    = currentLang === 'it'
      ? `Piano ${floorNum}`
      : `Floor ${floorNum}`;
    floorLabelElem.textContent = `${buildingLabel}\n— ${floorLabel}`;
  }

  // Renderizza le righe nella tabella
  function render(data) {
    lessonBody.innerHTML = ''; // Pulisci la tabella

    // Gestione bilingue per "Nessuna lezione"
    if (!Array.isArray(data) || data.length === 0 || (data[0] && data[0].message)) {
      lessonBody.innerHTML = `
        <tr>
          <td colspan="4">
            <span class="lang-it">${translations.it.noClasses}</span>
            <span class="lang-en">${translations.en.noClasses}</span>
          </td>
        </tr>`;
      return;
    }

    data.forEach(item => {
      const s = new Date(item.start_time), e = new Date(item.end_time);
      const tm = `${pad2(s.getHours())}:${pad2(s.getMinutes())} – ${pad2(e.getHours())}:${pad2(e.getMinutes())}`;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.classroom_name || 'N/A'}</td>
        <td>${tm}</td>
        <td style="text-align:left;">${item.lesson_name || 'N/A'}</td>
        <td>${item.instructor || 'N/A'}</td>
      `;
      lessonBody.appendChild(tr);
    });
  }

  // Configura lo scroll automatico "boomerang"
  function setupAutoScroll() {
    if (scrollInit) return;
    scrollInit = true;

    const w = document.querySelector('.scroll-body');
    if (!w) return;
    const c = w.querySelector('table'); // Seleziona la tabella per lo scroll
    if (!c) return;

    let dir = -1, pos = 0;
    const step = 1, delay = 30, pause = 3000;

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

  // Fetch e render in un unico flusso
  function fetchAndRender() {
    fetch(apiUrl)
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(data => {
        lastData = data; // Salva i dati per il cambio lingua
        
        // Aggiorna tutti gli elementi dell'UI
        updateHeaders();
        updateDate();
        updateLabel();
        render(data);
        
        setupAutoScroll(); // Avvia lo scroll solo dopo aver caricato i dati
      })
      .catch(err => {
        lessonBody.innerHTML = `<tr><td colspan="4">Error: ${err}</td></tr>`;
      });
  }

  // Alterna lingua e aggiorna tutto
  function toggleLang() {
    langIndex   = 1 - langIndex;
    currentLang = LANGS[langIndex];
    document.body.classList.toggle('lang-it');
    document.body.classList.toggle('lang-en');
    
    // Aggiorna tutti gli elementi di testo
    updateHeaders();
    updateDate();
    updateLabel();
    
    // Riesegui il render per aggiornare il messaggio "Nessuna lezione"
    render(lastData);
  }

  // ----- Inizializzazione -----
  document.body.classList.add('lang-it');
  
  fetchAndRender(); // Usa la funzione corretta
  
  setInterval(updateClock, 1000);
  setInterval(toggleLang, 15000);
})();