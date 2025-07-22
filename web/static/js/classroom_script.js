/**
 * EN: Classroom view script with fixed header and auto‐scrolling body.
 * IT: Script per la vista delle lezioni in aula con intestazione fissa
 * e corpo scorrevole automaticamente a boomerang.
 */

;(function () {
  // ==========================================================================
  // Element references / Riferimenti agli elementi DOM
  // ==========================================================================
  const lessonBody        = document.getElementById('lesson-body');
  const clockElem         = document.getElementById('clock');
  const classroomNameElem = document.getElementById('classroom-name');
  const currentDateElem   = document.getElementById('current-date');

  // ==========================================================================
  // Language / Lingue
  // ==========================================================================
  const LANGS      = ['it', 'en'];
  let langIndex    = 0;
  let currentLang  = LANGS[langIndex];

  const dayNamesIt   = ['domenica','lunedì','martedì','mercoledì','giovedì','venerdì','sabato'];
  const monthNamesIt = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];

  const translations = {
    it: {
      headers:   ['ORA','NOME LEZIONE','STATO','PROFESSORE'],
      noClasses: 'Nessuna lezione disponibile',
      status:    { soon:'Futura', live:'In corso', ended:'Terminata' }
    },
    en: {
      headers:   ['TIME','LESSON NAME','STATUS','PROFESSOR'],
      noClasses: 'No lessons available',
      status:    { soon:'Upcoming', live:'Ongoing', ended:'Ended' }
    }
  };

  // ==========================================================================
  // URL params / Parametri URL
  // ==========================================================================
  const qp     = (window.location.search || '').substr(1).split('&');
  const params = {};
  qp.forEach(pair => {
    const [k,v] = pair.split('=');
    if (k) params[decodeURIComponent(k)] = decodeURIComponent(v || '');
  });

  const classroomId  = params.classroom || params.aula;
  const buildingId   = params.building  || params.edificio;
  const period       = params.period    || 'all';
  const selectedDate = params.date      || new Date().toISOString().split('T')[0];

  if (!classroomId || !buildingId) {
    lessonBody.innerHTML = '<tr><td colspan="4">Missing "classroom" or "building" parameter</td></tr>';
    return;
  }

  const API_URL  = `${window.location.origin}/lessons`;
  let lastData   = [];

  // ==========================================================================
  // Utility functions / Funzioni di utilità
  // ==========================================================================
  function pad2(n) {
    return (n < 10 ? '0' : '') + n;
  }

  function formatDate(iso) {
    const [yy, mm, dd] = iso.split('-').map((s,i)=> parseInt(s,10));
    const d = new Date(yy, mm-1, dd);
    let day   = currentLang==='it'
                ? dayNamesIt[d.getDay()]
                : d.toLocaleDateString('en-GB',{ weekday:'long' }).toLowerCase();
    let month = currentLang==='it'
                ? monthNamesIt[mm-1]
                : d.toLocaleDateString('en-GB',{ month:'long' });
    day   = day.charAt(0).toUpperCase() + day.slice(1);
    return `${day} ${dd} ${month} ${yy}`;
  }

  function updateHeaders() {
    document.querySelectorAll('thead th').forEach((th,i)=>{
      th.textContent = translations[currentLang].headers[i];
    });
  }

  function updateCurrentDate() {
    currentDateElem.textContent = formatDate(selectedDate);
  }

  function updateClock() {
    const now = new Date();
    clockElem.textContent =
      pad2(now.getHours())+':'+pad2(now.getMinutes())+':'+pad2(now.getSeconds());
  }

  function computeStatus(s,e) {
    const now = Date.now(), start = new Date(s), end = new Date(e);
    if (now < start) return translations[currentLang].status.soon;
    if (now > end)   return translations[currentLang].status.ended;
    return translations[currentLang].status.live;
  }

  function getStatusClass(s,e) {
    const now = Date.now(), start = new Date(s), end = new Date(e);
    if (now < start) return 'status-soon';
    if (now > end)   return 'status-ended';
    return 'status-live';
  }

  // ==========================================================================
  // Rendering / Rendering delle lezioni + status dot
  // ==========================================================================
  function renderLessons(data) {
    lessonBody.innerHTML = '';
    if (!data.length || data[0].message === 'No classes available') {
      lessonBody.innerHTML = `
        <tr>
          <td colspan="4">
            <span class="lang-it">${translations.it.noClasses}</span>
            <span class="lang-en">${translations.en.noClasses}</span>
          </td>
        </tr>
      `;
      return;
    }

    data.forEach(les => {
      const s  = new Date(les.start_time),
            e  = new Date(les.end_time),
            tm = pad2(s.getHours())+':'+pad2(s.getMinutes())
              +' – '+pad2(e.getHours())+':'+pad2(e.getMinutes());

      const row = document.createElement('tr');

      // Funzione helper per creare gli span bilingue
      const createLangSpan = (key, path = 'status') => 
        `<span class="lang-it">${translations.it[path][key]}</span><span class="lang-en">${translations.en[path][key]}</span>`;

      // Calcola la classe e il testo per lo stato
      const statusClass = getStatusClass(les.start_time, les.end_time);
      let statusKey;
      if (statusClass === 'status-soon') statusKey = 'soon';
      else if (statusClass === 'status-live') statusKey = 'live';
      else statusKey = 'ended';

      // Usiamo innerHTML per inserire la struttura con gli SPAN
      row.innerHTML = `
        <td>${tm}</td>
        <td style="text-align: left;">${les.lesson_name || 'N/A'}</td>
        <td class="status-indicator">
          <span class="status-dot ${statusClass}"></span>
          ${createLangSpan(statusKey, 'status')}
        </td>
        <td style="text-align: left;">${les.instructor || 'N/A'}</td>
      `;
      
      lessonBody.appendChild(row);
    });
  }

  // ==========================================================================
  // Auto‐scroll setup (boomerang) / Scorrimento automatico a boomerang
  // ==========================================================================
  let autoScrollInit = false;
  function setupAutoScroll() {
    if (autoScrollInit) return;
    const wrapper = document.querySelector('.scroll-body');
    if (!wrapper) return;
    autoScrollInit = true;

    // il <table> completo incluso thead/tbody
    const tbl = wrapper.querySelector('table');
    let dir = -1, pos = 0, step = 1, delay = 30, pause = 3000;
    tbl.style.transform = 'translateY(0)';

    function stepScroll() {
      const vh = wrapper.clientHeight,
            bh = tbl.scrollHeight;
      if (bh <= vh) return;
      pos += dir * step;
      tbl.style.transform = `translateY(${pos}px)`;
      const max = vh - bh;
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

  // ==========================================================================
  // Fetch lessons / Richiesta AJAX
  // ==========================================================================
  function fetchLessons() {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', API_URL, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
      if (xhr.readyState !== 4) return;
      if (xhr.status === 200) {
        const data = JSON.parse(xhr.responseText);
        lastData = data;
        // nome aula
        const name = data[0] && data[0].classroom_name
                   ? data[0].classroom_name
                   : (currentLang==='it' ? 'Aula ' : 'Classroom ') + classroomId;
        classroomNameElem.textContent = name;

        updateHeaders();
        updateCurrentDate();
        updateClock();
        renderLessons(data);
        setupAutoScroll();
      } else {
        lessonBody.innerHTML = `<tr><td colspan="4">Error: ${xhr.status}</td></tr>`;
      }
    };
    xhr.send(JSON.stringify({
      classroom: classroomId,
      building:  buildingId,
      date:      selectedDate,
      period:    period
    }));
  }

  // ==========================================================================
  // Toggle language / Cambio lingua periodico
  // ==========================================================================
  function toggleLanguage() {
    // 1. Aggiorna l'indice e la lingua corrente
    langIndex   = 1 - langIndex;
    currentLang = LANGS[langIndex];

    // 2. Cambia la classe sul body. Il CSS farà tutta la magia!
    document.body.classList.toggle('lang-it');
    document.body.classList.toggle('lang-en');
    
    // 3. Aggiorna gli elementi fuori dalla tabella che non sono stati creati con gli span
    // NOTA: Queste operazioni sono molto leggere
    updateHeaders();
    updateCurrentDate();
    
    // NON chiamiamo più renderLessons()!
  }

  // ==========================================================================
  // Initialization / Inizializzazione
  // ==========================================================================
  document.body.classList.add('lang-it'); // Assicurati che parta con la classe IT
  fetchLessons();
  updateClock();
  // updateCurrentDate(); // Verrà chiamato da fetchLessons la prima volta

  // periodic updates / aggiornamenti periodici
  setInterval(updateClock,    1000);
  // setInterval(fetchLessons, 60000); // Giustamente disabilitato
  setInterval(toggleLanguage, 15000); // Ora questa funzione è super leggera!
})();