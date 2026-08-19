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

      "update.eyebrow": "Aktualizacja",
      "update.title": "Dostępna jest nowa wersja",
      "update.lede": "{name} {latest} jest już dostępny. Korzystasz z wersji {current}.",
      "update.current": "Zainstalowana",
      "update.latest": "Najnowsza",
      "update.released": "wydano {date}",
      "update.btnPage": "Pobierz aktualizację",
      "update.btnLater": "Przypomnij później",
      "update.skip": "Nie przypominaj o tej wersji",
      "update.directLink": "Pobierz plik bezpośrednio",
      "update.chip": "nowa wersja {latest}",
      "update.chipTitle": "Kliknij, aby zobaczyć szczegóły aktualizacji",

      "modal.title": "Wybierz program",
      "modal.subtitle": "Kliknij dwukrotnie, aby wybrać proces.",
      "modal.searchPlaceholder": "Szukaj procesu…",
      "modal.cancel": "Anuluj",
      "modal.select": "Wybierz",
      "modal.loading": "Wczytywanie procesów…",
      "modal.loadFail": "Nie udało się pobrać listy procesów.",
      "modal.noMatch": "Brak pasujących procesów.",

      "modal.modeLabel": "Zakres",

      "mode.single.short": "Jeden",
      "mode.name.short": "Ta sama nazwa",
      "mode.tree.short": "Z potomkami",
      "mode.set.short": "Zaznaczone",
      "mode.single.hint": "Mierzony będzie wyłącznie zaznaczony proces.",
      "mode.name.hint": "Zaznacz jeden proces, a pomiar obejmie wszystkie o tej samej nazwie — łącznie z tymi, które pojawią się w trakcie.",
      "mode.tree.hint": "Zaznacz proces nadrzędny, a pomiar obejmie jego oraz wszystkie procesy potomne, także uruchomione później.",
      "mode.set.hint": "Zaznacz dowolne procesy z listy. Skład grupy nie zmienia się w trakcie pomiaru.",
      "mode.name.label": "wszystkie procesy o tej nazwie",
      "mode.tree.label": "proces wraz z potomkami",
      "mode.set.label": "ręcznie zaznaczone procesy",
      "mode.single.label": "pojedynczy proces",

      "modal.summary.single": "Wybrano <b>{name}</b> · PID {pid}",
      "modal.summary.group": "Wybrano <b>{name}</b> · {count}",
      "modal.summary.none": "Nie wybrano jeszcze procesu.",
      "modal.summary.checked": "Zaznaczono <b>{count}</b>",

      "group.count.one": "{count} proces",
      "group.count.few": "{count} procesy",
      "group.count.many": "{count} procesów",
      "group.clear": "Wyczyść wybór",

      "metric.procs.name": "Liczba procesów",
      "metric.procs.note": "ilu członków miała grupa w danej chwili",
      "metric.ram.noteGroup": "suma RSS wszystkich procesów — pamięć współdzielona liczona wielokrotnie",

      "procs.title": "Udział procesów",
      "procs.note": "Średnie liczone z próbek, w których dany proces działał. Udział to jego część łącznego zużycia CPU przez grupę.",
      "procs.others": "pozostałe procesy ({count})",
      "procs.col.name": "Proces",
      "procs.col.samples": "Próbek",
      "procs.col.cpuAvg": "CPU śr. (%)",
      "procs.col.cpuMax": "CPU maks. (%)",
      "procs.col.ramAvg": "RAM śr. (MB)",
      "procs.col.ramMax": "RAM maks. (MB)",
      "procs.col.share": "Udział (%)",

      "report.metaGroup": "grupa: {mode} · szczyt: {peak} · łącznie zaobserwowano: {seen}",

      "toast.noneChecked": "Zaznacz przynajmniej jeden proces.",

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

      "update.eyebrow": "Update",
      "update.title": "A new version is available",
      "update.lede": "{name} {latest} has been released. You are running {current}.",
      "update.current": "Installed",
      "update.latest": "Latest",
      "update.released": "released {date}",
      "update.btnPage": "Get the update",
      "update.btnLater": "Remind me later",
      "update.skip": "Don't remind me about this version",
      "update.directLink": "Download the file directly",
      "update.chip": "new version {latest}",
      "update.chipTitle": "Click to see the update details",

      "modal.title": "Choose a program",
      "modal.subtitle": "Double-click to select a process.",
      "modal.searchPlaceholder": "Search a process…",
      "modal.cancel": "Cancel",
      "modal.select": "Select",
      "modal.loading": "Loading processes…",
      "modal.loadFail": "Failed to load the process list.",
      "modal.noMatch": "No matching processes.",

      "modal.modeLabel": "Scope",

      "mode.single.short": "One",
      "mode.name.short": "Same name",
      "mode.tree.short": "With children",
      "mode.set.short": "Selected",
      "mode.single.hint": "Only the selected process will be measured.",
      "mode.name.hint": "Pick one process and the session covers every process sharing its name — including any that appear later.",
      "mode.tree.hint": "Pick a parent process and the session covers it plus all of its descendants, including ones started later.",
      "mode.set.hint": "Tick any processes in the list. The group stays fixed for the whole session.",
      "mode.name.label": "every process with this name",
      "mode.tree.label": "process and its descendants",
      "mode.set.label": "hand-picked processes",
      "mode.single.label": "a single process",

      "modal.summary.single": "Selected <b>{name}</b> · PID {pid}",
      "modal.summary.group": "Selected <b>{name}</b> · {count}",
      "modal.summary.none": "No process selected yet.",
      "modal.summary.checked": "Ticked <b>{count}</b>",

      "group.count.one": "{count} process",
      "group.count.few": "{count} processes",
      "group.count.many": "{count} processes",
      "group.clear": "Clear selection",

      "metric.procs.name": "Process count",
      "metric.procs.note": "how many members the group had at that moment",
      "metric.ram.noteGroup": "summed RSS across the group — shared memory is counted more than once",

      "procs.title": "Per-process share",
      "procs.note": "Averages are taken over the samples in which each process was alive. Share is its slice of the group's total CPU usage.",
      "procs.others": "remaining processes ({count})",
      "procs.col.name": "Process",
      "procs.col.samples": "Samples",
      "procs.col.cpuAvg": "CPU avg (%)",
      "procs.col.cpuMax": "CPU max (%)",
      "procs.col.ramAvg": "RAM avg (MB)",
      "procs.col.ramMax": "RAM max (MB)",
      "procs.col.share": "Share (%)",

      "report.metaGroup": "group: {mode} · peak: {peak} · {seen} seen in total",

      "toast.noneChecked": "Tick at least one process.",

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

  // Polish needs three plural forms (1 proces / 2-4 procesy / 5+ procesów);
  // English only needs two. Keys are suffixed .one / .few / .many.
  function pluralForm(n) {
    n = Math.abs(Number(n) || 0);
    if (lang !== "pl") return n === 1 ? "one" : "many";
    if (n === 1) return "one";
    const m10 = n % 10, m100 = n % 100;
    return (m10 >= 2 && m10 <= 4 && !(m100 >= 12 && m100 <= 14)) ? "few" : "many";
  }

  /** Count-aware lookup: tn("group.count", 4) -> "4 procesy". */
  function tn(baseKey, n, params) {
    const p = params ? Object.assign({}, params) : {};
    if (p.count == null) p.count = n;
    return t(baseKey + "." + pluralForm(n), p);
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

  global.UMi18n = { t, tn, apply, setLang, getLang, init, onChange, createToggle };
})(window);
