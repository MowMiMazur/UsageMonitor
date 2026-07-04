// Shared i18n (PL/EN) for the app window and the exported HTML report.
(function (global) {
  "use strict";

  const DICT = {
    pl: {
      "brand.sub": "monitor zasobów procesu",

      "status.ready": "Gotowy",
      "status.monitoring": "Monitorowanie",
      "status.stopping": "Zatrzymywanie…",
      "status.done": "Zakończono",

      "home.eyebrow": "Pomiar w czasie rzeczywistym",
      "home.headline": "Zmierz zużycie <em>CPU</em> i <em>RAM</em><br />dowolnego procesu.",
      "home.lede": "Wskaż proces po jego identyfikatorze albo wybierz go z listy. Po zakończeniu otrzymasz przejrzysty raport z wykresami — zapisany także jako samodzielny plik HTML.",
      "home.pidLabel": "Identyfikator procesu (PID)",
      "home.pidPlaceholder": "np. 1234",
      "home.hint": "Wskazówka: naciśnij <kbd>Enter</kbd>, aby rozpocząć.",

      "btn.browse": "Wybierz program",
      "btn.start": "Rozpocznij monitoring",
      "btn.stop": "Zatrzymaj monitoring",
      "btn.openHtml": "Otwórz raport HTML",
      "btn.openFolder": "Pokaż w folderze",
      "btn.newSession": "Nowa sesja",

      "monitor.eyebrow": "Monitorowanie",
      "report.eyebrow": "Raport monitorowania",
      "report.savedTo": "Raport zapisany w",

      "footer.version": "Wersja",
      "footer.madeBy": "Stworzone z ♥ przez",

      "modal.title": "Wybierz program",
      "modal.subtitle": "Kliknij dwukrotnie, aby wybrać proces.",
      "modal.searchPlaceholder": "Szukaj procesu…",
      "modal.cancel": "Anuluj",
      "modal.select": "Wybierz",
      "modal.loading": "Wczytywanie procesów…",
      "modal.loadFail": "Nie udało się pobrać listy procesów.",
      "modal.noMatch": "Brak pasujących procesów.",

      "metric.cpu_raw.name": "CPU — na rdzeń",
      "metric.cpu_raw.note": "sumaryczne obciążenie względem jednego rdzenia",
      "metric.cpu_norm.name": "CPU — całkowite",
      "metric.cpu_norm.note": "obciążenie względem wszystkich rdzeni",
      "metric.ram.name": "Pamięć RAM",
      "metric.ram.note": "zestaw rezydentny (RSS)",

      "stat.min": "min",
      "stat.avg": "śr",
      "stat.max": "maks",

      "tile.start": "Start",
      "tile.stop": "Stop",
      "tile.duration": "Czas trwania",
      "tile.samples": "Próbek",

      "log.summary": "Pełny dziennik próbek",
      "log.col.time": "Czas",
      "log.col.cpuCore": "CPU / rdzeń (%)",
      "log.col.cpuTotal": "CPU total (%)",
      "log.col.ram": "RAM (MB)",

      "chart.collecting": "Zbieranie danych…",

      "report.title": "raport monitorowania",
      "report.tagline": "Zużycie CPU i RAM w czasie sesji monitorowania",
      "report.generated": "wygenerowano {when}",
      "report.meta": "Liczba rdzeni logicznych: {cores} · interwał próbkowania: {interval}s · {samples} próbek",

      "err.invalid_pid": "Nieprawidłowy numer PID.",
      "err.process_missing": "Proces o PID {pid} nie istnieje lub zakończył działanie.",
      "err.generic": "Wystąpił błąd monitorowania.",

      "toast.backendNotReady": "Backend nie jest gotowy.",
      "toast.invalidPid": "Podaj poprawny numer PID.",
      "toast.startFail": "Błąd uruchomienia monitoringu.",
      "toast.cantStart": "Nie można rozpocząć monitoringu.",
      "toast.noData": "Brak danych pomiarowych — proces zakończył się zbyt szybko.",

      "default.procName": "proces",
    },

    en: {
      "brand.sub": "process resource monitor",

      "status.ready": "Ready",
      "status.monitoring": "Monitoring",
      "status.stopping": "Stopping…",
      "status.done": "Done",

      "home.eyebrow": "Real-time measurement",
      "home.headline": "Measure the <em>CPU</em> and <em>RAM</em><br />usage of any process.",
      "home.lede": "Point it at a process by its identifier or pick one from the list. When you stop, you get a clean report with charts — also saved as a self-contained HTML file.",
      "home.pidLabel": "Process identifier (PID)",
      "home.pidPlaceholder": "e.g. 1234",
      "home.hint": "Tip: press <kbd>Enter</kbd> to start.",

      "btn.browse": "Choose a program",
      "btn.start": "Start monitoring",
      "btn.stop": "Stop monitoring",
      "btn.openHtml": "Open HTML report",
      "btn.openFolder": "Show in folder",
      "btn.newSession": "New session",

      "monitor.eyebrow": "Monitoring",
      "report.eyebrow": "Monitoring report",
      "report.savedTo": "Report saved to",

      "footer.version": "Version",
      "footer.madeBy": "Made with ♥ by",

      "modal.title": "Choose a program",
      "modal.subtitle": "Double-click to select a process.",
      "modal.searchPlaceholder": "Search a process…",
      "modal.cancel": "Cancel",
      "modal.select": "Select",
      "modal.loading": "Loading processes…",
      "modal.loadFail": "Failed to load the process list.",
      "modal.noMatch": "No matching processes.",

      "metric.cpu_raw.name": "CPU — per core",
      "metric.cpu_raw.note": "total load relative to a single core",
      "metric.cpu_norm.name": "CPU — total",
      "metric.cpu_norm.note": "load relative to all cores",
      "metric.ram.name": "RAM",
      "metric.ram.note": "resident set size (RSS)",

      "stat.min": "min",
      "stat.avg": "avg",
      "stat.max": "max",

      "tile.start": "Start",
      "tile.stop": "Stop",
      "tile.duration": "Duration",
      "tile.samples": "Samples",

      "log.summary": "Full sample log",
      "log.col.time": "Time",
      "log.col.cpuCore": "CPU / core (%)",
      "log.col.cpuTotal": "CPU total (%)",
      "log.col.ram": "RAM (MB)",

      "chart.collecting": "Collecting data…",

      "report.title": "monitoring report",
      "report.tagline": "CPU and RAM usage during the monitoring session",
      "report.generated": "generated {when}",
      "report.meta": "Logical cores: {cores} · sampling interval: {interval}s · {samples} samples",

      "err.invalid_pid": "Invalid PID.",
      "err.process_missing": "Process with PID {pid} does not exist or has exited.",
      "err.generic": "A monitoring error occurred.",

      "toast.backendNotReady": "Backend is not ready.",
      "toast.invalidPid": "Enter a valid PID.",
      "toast.startFail": "Failed to start monitoring.",
      "toast.cantStart": "Could not start monitoring.",
      "toast.noData": "No samples collected — the process exited too quickly.",

      "default.procName": "process",
    },
  };

  const STORE_KEY = "um_lang";
  let lang = "pl";
  const listeners = [];

  function t(key, params) {
    const table = DICT[lang] || DICT.pl;
    let s = table[key];
    if (s == null) s = (DICT.en[key] != null ? DICT.en[key] : key);
    if (params) s = s.replace(/\{(\w+)\}/g, (m, k) => (params[k] != null ? params[k] : m));
    return s;
  }

  function apply(root) {
    root = root || document;
    root.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t(el.getAttribute("data-i18n")); });
    root.querySelectorAll("[data-i18n-html]").forEach((el) => { el.innerHTML = t(el.getAttribute("data-i18n-html")); });
    root.querySelectorAll("[data-i18n-ph]").forEach((el) => { el.setAttribute("placeholder", t(el.getAttribute("data-i18n-ph"))); });
    if (document.documentElement) document.documentElement.setAttribute("lang", lang);
  }

  function setLang(next) {
    if (next !== "pl" && next !== "en") return;
    if (next === lang) return;
    lang = next;
    try { localStorage.setItem(STORE_KEY, lang); } catch (e) {}
    apply(document);
    listeners.forEach((cb) => { try { cb(lang); } catch (e) {} });
    document.querySelectorAll(".lang-toggle").forEach(reflectToggle);
  }

  function getLang() { return lang; }

  function init(defaultLang) {
    let saved = null;
    try { saved = localStorage.getItem(STORE_KEY); } catch (e) {}
    lang = (saved === "pl" || saved === "en") ? saved : (defaultLang === "en" ? "en" : "pl");
    apply(document);
    document.querySelectorAll(".lang-toggle").forEach(reflectToggle);
    return lang;
  }

  function onChange(cb) { listeners.push(cb); }

  function reflectToggle(el) {
    el.querySelectorAll("[data-lang]").forEach((b) => {
      b.classList.toggle("is-active", b.getAttribute("data-lang") === lang);
    });
  }

  function createToggle() {
    const wrap = document.createElement("div");
    wrap.className = "lang-toggle";
    wrap.setAttribute("role", "group");
    wrap.innerHTML = '<button type="button" data-lang="pl">PL</button><button type="button" data-lang="en">EN</button>';
    wrap.querySelectorAll("[data-lang]").forEach((b) => {
      b.addEventListener("click", () => setLang(b.getAttribute("data-lang")));
    });
    reflectToggle(wrap);
    return wrap;
  }

  global.UMi18n = { t, apply, setLang, getLang, init, onChange, createToggle };
})(window);
