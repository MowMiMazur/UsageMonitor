// App-window logic and the Python bridge (pywebview).
(function () {
  "use strict";

  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const fmt = (v, d) => (window.UMCharts ? UMCharts.fmt(v, d) : String(v));
  const t = (k, p) => UMi18n.t(k, p);

  // Live metrics come from the shared report config (single source of truth).
  const LIVE = UMReport.METRICS;

  const state = {
    api: null,
    buf: { t: [], cpu_raw: [], cpu_norm: [], ram: [] },
    charts: {},
    tiles: {},
    timer: null,
    t0: 0,
    running: false,
    statusKey: "ready",
    modalPid: null,
    allProcs: [],
    lastReport: null,
    lastReportPath: null,
  };

  function boot() {
    UMi18n.init("pl");
    $("#lang-mount").appendChild(UMi18n.createToggle());
    UMi18n.onChange(onLangChange);
    setStatus("ready", false);
    wireEvents();
    if (window.pywebview && window.pywebview.api) onApiReady();
    else window.addEventListener("pywebviewready", onApiReady);
  }

  async function onApiReady() {
    state.api = window.pywebview.api;
    try { state.api.set_lang(UMi18n.getLang()); } catch (e) {}
    try {
      const info = await state.api.get_app_info();
      $("#footer-version").textContent = info.version;
      const a = $("#footer-author");
      a.textContent = info.author_name;
      a.href = info.author_url;
      a.addEventListener("click", (e) => { e.preventDefault(); state.api.open_url(info.author_url); });
    } catch (e) { /* running without a backend (preview) */ }
  }

  function onLangChange(lang) {
    if (state.api) { try { state.api.set_lang(lang); } catch (e) {} }
    setStatus(state.statusKey, state.running);       // re-translate current status
    if (state.running) relabelLive();
    if (state.lastReport && $("#view-report").classList.contains("is-active")) {
      UMReport.render($("#report-root"), state.lastReport);
    }
  }

  function switchView(id) {
    $$(".view").forEach((v) => v.classList.toggle("is-active", v.id === id));
    window.scrollTo({ top: 0 });
  }
  function setStatus(key, live) {
    state.statusKey = key;
    $("#status-text").textContent = t("status." + key);
    $("#status-pill").classList.toggle("is-live", !!live);
  }

  function stopBtnInner() {
    return '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>'
      + '<span data-i18n="btn.stop">' + t("btn.stop") + "</span>";
  }
  function restoreStopBtn() {
    const btn = $("#stop-btn");
    btn.disabled = false;
    btn.innerHTML = stopBtnInner();
  }

  let toastTimer = null;
  function toast(msg) {
    const el = $("#toast");
    el.textContent = msg;
    el.classList.add("is-show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("is-show"), 4200);
  }

  function wireEvents() {
    $("#start-btn").addEventListener("click", startMonitoring);
    $("#pid-input").addEventListener("keydown", (e) => { if (e.key === "Enter") startMonitoring(); });
    $("#pid-input").addEventListener("input", (e) => { e.target.value = e.target.value.replace(/[^0-9]/g, ""); });
    $("#stop-btn").addEventListener("click", stopMonitoring);
    $("#new-session-btn").addEventListener("click", resetToHome);

    $("#open-html-btn").addEventListener("click", () => {
      if (state.lastReportPath && state.api) state.api.open_path(state.lastReportPath);
    });
    $("#open-folder-btn").addEventListener("click", () => {
      if (state.lastReportPath && state.api) state.api.reveal_path(state.lastReportPath);
    });

    $("#browse-btn").addEventListener("click", openProcModal);
    $("#proc-cancel").addEventListener("click", closeProcModal);
    $("#proc-overlay").addEventListener("click", (e) => { if (e.target.id === "proc-overlay") closeProcModal(); });
    $("#proc-select").addEventListener("click", confirmProcSelection);
    $("#proc-search").addEventListener("input", (e) => renderProcList(e.target.value));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && $("#proc-overlay").classList.contains("is-open")) closeProcModal();
    });
  }

  // Process picker modal
  async function openProcModal() {
    if (!state.api) return;
    $("#proc-overlay").classList.add("is-open");
    state.modalPid = null;
    $("#proc-select").disabled = true;
    $("#proc-search").value = "";
    $("#proc-list").innerHTML = `<div class="proc-empty">${t("modal.loading")}</div>`;
    try {
      state.allProcs = await state.api.get_process_list();
      renderProcList("");
      $("#proc-search").focus();
    } catch (e) {
      $("#proc-list").innerHTML = `<div class="proc-empty">${t("modal.loadFail")}</div>`;
    }
  }
  function closeProcModal() { $("#proc-overlay").classList.remove("is-open"); }

  function renderProcList(query) {
    const q = (query || "").toLowerCase().trim();
    const list = $("#proc-list");
    const items = state.allProcs.filter((p) =>
      !q || p.name.toLowerCase().includes(q) || String(p.pid).includes(q));
    if (!items.length) { list.innerHTML = `<div class="proc-empty">${t("modal.noMatch")}</div>`; return; }
    const frag = document.createDocumentFragment();
    items.slice(0, 400).forEach((p) => {
      const el = document.createElement("div");
      el.className = "proc-item";
      el.dataset.pid = p.pid;
      el.innerHTML = `<span class="pname"></span><span class="ppid">PID ${p.pid}</span>`;
      el.querySelector(".pname").textContent = p.name;
      el.addEventListener("click", () => selectProc(el, p.pid));
      el.addEventListener("dblclick", () => { selectProc(el, p.pid); confirmProcSelection(); });
      frag.appendChild(el);
    });
    list.innerHTML = "";
    list.appendChild(frag);
  }
  function selectProc(el, pid) {
    $$(".proc-item").forEach((x) => x.classList.remove("is-sel"));
    el.classList.add("is-sel");
    state.modalPid = pid;
    $("#proc-select").disabled = false;
  }
  function confirmProcSelection() {
    if (state.modalPid == null) return;
    $("#pid-input").value = state.modalPid;
    closeProcModal();
  }

  // Start / stop
  async function startMonitoring() {
    if (!state.api) { toast(t("toast.backendNotReady")); return; }
    const pid = parseInt($("#pid-input").value, 10);
    if (!Number.isInteger(pid) || pid < 0) { toast(t("toast.invalidPid")); return; }

    const btn = $("#start-btn");
    btn.disabled = true;
    let res;
    try { res = await state.api.start_monitoring(pid); }
    catch (e) { toast(t("toast.startFail")); btn.disabled = false; return; }
    btn.disabled = false;

    if (!res || !res.ok) { toast(errText(res && res.error_key, res) || t("toast.cantStart")); return; }
    beginLiveSession(res);
  }

  function errText(code, params) {
    if (!code) return null;
    const s = t("err." + code, params);
    return s === "err." + code ? null : s;
  }

  function beginLiveSession(info) {
    state.running = true;
    state.buf = { t: [], cpu_raw: [], cpu_norm: [], ram: [] };
    $("#mon-name").firstChild.textContent = info.proc_name || t("default.procName");
    $("#mon-pid").textContent = "PID " + info.pid;
    setStatus("monitoring", true);
    switchView("view-monitor");
    buildLiveUI();

    state.t0 = Date.now();
    $("#timer").textContent = "00:00:00";
    clearInterval(state.timer);
    state.timer = setInterval(tickTimer, 250);
  }

  function tickTimer() {
    const s = Math.floor((Date.now() - state.t0) / 1000);
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), ss = s % 60;
    const p = (n) => String(n).padStart(2, "0");
    $("#timer").textContent = `${p(h)}:${p(m)}:${p(ss)}`;
  }

  function buildLiveUI() {
    const tiles = $("#mon-tiles");
    tiles.innerHTML = "";
    state.tiles = {};
    LIVE.forEach((m) => {
      const el = document.createElement("div");
      el.className = "stat";
      el.innerHTML = `<span class="stat__label" data-live-label="${m.key}"></span>`
        + `<span class="stat__value">—<span class="unit">${m.unit.trim()}</span></span>`;
      el.querySelector("[data-live-label]").textContent = t(m.nameKey);
      tiles.appendChild(el);
      state.tiles[m.key] = el.querySelector(".stat__value");
    });

    const wrap = $("#mon-charts");
    wrap.innerHTML = "";
    state.charts = {};
    LIVE.forEach((m) => {
      const card = document.createElement("div");
      card.className = "chart-card";
      card.innerHTML = `<div class="chart-head">
          <span class="series-key"><span class="dot" style="background:${m.color}"></span><span data-live-name="${m.key}">${t(m.nameKey)}</span></span>
          <span class="chart-now" data-now="${m.key}">—</span>
        </div><div class="chart-mount"></div>`;
      wrap.appendChild(card);
      const mount = card.querySelector(".chart-mount");
      state.charts[m.key] = UMCharts.createLineChart(mount, { color: m.color, unit: m.unit, decimals: m.decimals });
    });
  }

  function relabelLive() {
    LIVE.forEach((m) => {
      const lbl = document.querySelector(`[data-live-label="${m.key}"]`);
      if (lbl) lbl.textContent = t(m.nameKey);
      const nm = document.querySelector(`[data-live-name="${m.key}"]`);
      if (nm) nm.textContent = t(m.nameKey);
    });
  }

  function stopMonitoring() {
    if (!state.running || !state.api) return;
    const btn = $("#stop-btn");
    btn.disabled = true;
    btn.textContent = t("status.stopping");
    setStatus("stopping", true);
    state.api.request_stop();
    // Then wait for UM.onFinished from Python.
  }

  function resetToHome() {
    state.running = false;
    clearInterval(state.timer);
    setStatus("ready", false);
    restoreStopBtn();
    switchView("view-home");
  }

  // Callbacks invoked from Python via window.UM.*
  const UM = {
    onSample(sample) {
      if (!state.running) return;
      const b = state.buf;
      b.t.push(sample.t);
      b.cpu_raw.push(sample.cpu_raw);
      b.cpu_norm.push(sample.cpu_norm);
      b.ram.push(sample.ram);
      LIVE.forEach((m) => {
        const v = sample[m.key];
        state.tiles[m.key].firstChild.textContent = fmt(v, m.decimals) + " ";
        const now = document.querySelector(`[data-now="${m.key}"]`);
        if (now) now.textContent = fmt(v, m.decimals) + m.unit;
        state.charts[m.key].update(b[m.key], b.t);
      });
    },

    onFinished(report) {
      state.running = false;
      clearInterval(state.timer);
      setStatus("ready", false);
      restoreStopBtn();
      if (!report || !report.has_data) {
        toast(t("toast.noData"));
        resetToHome();
        return;
      }
      showReport(report);
    },

    onError(err) {
      state.running = false;
      clearInterval(state.timer);
      restoreStopBtn();
      setStatus("ready", false);
      let msg = t("err.generic");
      if (err && err.code) msg = errText(err.code, err) || err.detail || msg;
      else if (typeof err === "string") msg = err;
      toast(msg);
      resetToHome();
    },
  };
  window.UM = UM;

  function showReport(report) {
    state.lastReport = report;
    state.lastReportPath = report.meta ? report.meta.output_file : null;
    $("#rep-name").textContent = (report.meta && report.meta.proc_name) || t("default.procName");
    $("#rep-path").textContent = state.lastReportPath || "—";
    UMReport.render($("#report-root"), report);
    setStatus("done", false);
    switchView("view-report");
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
