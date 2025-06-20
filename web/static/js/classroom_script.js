/**
 * EN: Classroom view script.
 * IT: Script per la visualizzazione delle lezioni in aula.
*/

/**
 * EN:
 * - Reads query parameters (classroom, building, date, period)
 * - Calls /lessons via POST to get schedule
 * - Displays lessons in a responsive table
 * - Toggles language (IT/EN) every 15 seconds
 * - Updates clock every second
 * 
 * IT:
 * - Legge i parametri della query (aula, edificio, data, periodo)
 * - Chiamate/lezioni via POST per ottenere il programma
 * - Visualizza le lezioni in una tabella reattiva
 * - Cambia lingua (IT/EN) ogni 15 secondi
 * - Aggiorna l'orologio ogni secondo
 */

;(function () {
  var lessonBody        = document.getElementById('lesson-body');
  var clockElem         = document.getElementById('clock');
  var classroomNameElem = document.getElementById('classroom-name');
  var currentDateElem   = document.getElementById('current-date');
  var theadThs          = document.querySelectorAll('thead th');

  // EN/IT: Extract parameters from URL / Estrai i parametri dalla URL
  var qp     = (window.location.search || '').substr(1).split('&');
  var params = {};
  for (var i = 0; i < qp.length; i++) {
    var kv = qp[i].split('=');
    if (kv[0]) params[decodeURIComponent(kv[0])] = decodeURIComponent(kv[1] || '');
  }

  var classroomId  = params.classroom || params.aula;
  var buildingId   = params.building  || params.edificio;
  var period       = params.period    || 'all';
  var selectedDate = params.date      || new Date().toISOString().split('T')[0];

  if (!classroomId || !buildingId) {
    lessonBody.innerHTML = '<tr><td colspan="4">Missing "classroom" or "building" parameter</td></tr>';
    return;
  }

  var API_URL  = window.location.origin + '/lessons';
  var lastData = [];

  var LANGS        = ['it','en'];
  var langIndex    = 0;
  var currentLang  = LANGS[langIndex];

  var dayNamesIt   = ['domenica','lunedì','martedì','mercoledì','giovedì','venerdì','sabato'];
  var monthNamesIt = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];

  var translations = {
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

  function pad2(n) {
    return (n < 10 ? '0' : '') + n;
  }

  function formatDate(iso) {
    var parts = iso.split('-'),
        yy = parseInt(parts[0],10),
        mm = parseInt(parts[1],10) - 1,
        dd = parseInt(parts[2],10),
        d  = new Date(yy, mm, dd);

    var day = (currentLang === 'it')
      ? dayNamesIt[d.getDay()]
      : d.toLocaleDateString('en-GB', { weekday:'long' }).toLowerCase();

    var month = (currentLang === 'it')
      ? monthNamesIt[mm]
      : d.toLocaleDateString('en-GB', { month:'long' });

    day = day.charAt(0).toUpperCase() + day.slice(1);

    return `${day} ${dd} ${month} ${yy}`;
  }

  function updateHeaders() {
    for (var i = 0; i < theadThs.length; i++) {
      theadThs[i].textContent = translations[currentLang].headers[i];
    }
  }

  function updateCurrentDate() {
    currentDateElem.textContent = formatDate(selectedDate);
  }

  function updateClock() {
    var now = new Date();
    clockElem.textContent = pad2(now.getHours()) + ':' + pad2(now.getMinutes()) + ':' + pad2(now.getSeconds());
  }

  function computeStatus(s,e) {
    var now = new Date(), start = new Date(s), end = new Date(e);
    if (now < start) return translations[currentLang].status.soon;
    if (now > end)   return translations[currentLang].status.ended;
    return translations[currentLang].status.live;
  }

  function getStatusClass(s,e) {
    var now = new Date(), start = new Date(s), end = new Date(e);
    if (now < start) return 'status-soon';
    if (now > end)   return 'status-ended';
    return 'status-live';
  }

  function renderLessons(data) {
    lessonBody.innerHTML = '';
    if (!data.length || data[0].message === 'No classes available') {
      lessonBody.innerHTML = `<tr><td colspan="4">${translations[currentLang].noClasses}</td></tr>`;
      return;
    }

    data.forEach(function(les) {
      var s  = new Date(les.start_time),
          e  = new Date(les.end_time),
          tm = `${pad2(s.getHours())}:${pad2(s.getMinutes())} – ${pad2(e.getHours())}:${pad2(e.getMinutes())}`;

      var row = document.createElement('tr');
      row.innerHTML = `
        <td>${tm}</td>
        <td style="text-align:left;">${les.lesson_name || 'N/A'}</td>
        <td class="status-indicator">
          <span class="status-dot ${getStatusClass(les.start_time, les.end_time)}"></span>
          ${computeStatus(les.start_time, les.end_time)}
        </td>
        <td>${les.instructor || 'N/A'}</td>
      `;
      lessonBody.appendChild(row);
    });
  }

  function fetchLessons() {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', API_URL, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
      if (xhr.readyState !== 4) return;
      if (xhr.status === 200) {
        var data = JSON.parse(xhr.responseText);
        lastData = data;
        var name = data[0] && data[0].classroom_name
          ? data[0].classroom_name
          : (currentLang === 'it' ? 'Aula ' : 'Classroom ') + classroomId;
        classroomNameElem.textContent = name;
        updateHeaders();
        updateCurrentDate();
        updateClock();
        renderLessons(data);
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

  function toggleLanguage() {
    langIndex = 1 - langIndex;
    currentLang = LANGS[langIndex];
    document.body.classList.toggle('lang-it');
    document.body.classList.toggle('lang-en');
    updateHeaders();
    updateCurrentDate();
    updateClock();
    renderLessons(lastData);
  }

  // EN/IT: Initialization /Inizializzazione
  document.body.classList.add('lang-it');
  fetchLessons();
  updateCurrentDate();
  updateClock();

  setInterval(updateClock,     1000);
  setInterval(fetchLessons,   60000);
  setInterval(toggleLanguage, 15000);
})();
