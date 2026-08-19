// App-window logic and the Python bridge (pywebview).
(function () {
  "use strict";

  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const fmt = (v, d) => (window.UMCharts ? UMCharts.fmt(v, d) : String(v));
  const t = (k, p) => UMi18n.t(k, p);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const MODES = ["single", "name", "tree", "set"];

  const state = {
    api: null,
    buf: { t: [], cpu_raw: [], cpu_norm: [], ram: [], procs: [] },
    charts: {},
    tiles: {},
    timer: null,
    t0: 0,
    running: false,
    statusKey: "ready",
    allProcs: [],
    lastReport: null,
    lastReportPath: null,

    // What the next session will measure. `single` keeps the classic PID flow.
    target: { mode: "single", pid: null, name: null, pids: [] },
    // Draft selection inside the picker, committed only on "Wybierz".
    modal: { mode: "single", pid: null, name: null, checked: [] },
    // Metric set of the running session (a group adds the process-count series).
    liveMetrics: [],
    liveIsGroup: false,
  };

  function openExternal(url) {
    if (!state.api) return;
    try { state.api.open_url(url); } catch (e) {}
  }

  function boot() {
    UMi18n.init("pl");
    $("#lang-mount").appendChild(UMi18n.createToggle());
    UMi18n.onChange(onLangChange);
    setStatus("ready", false);
    wireEvents();
    UMUpdates.init({ openUrl: openExternal });
    renderTargetChip();
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

    try { state.api.start_update_check(); } catch (e) {}
  }

  function onLangChange(lang) {
    if (state.api) { try { state.api.set_lang(lang); } catch (e) {} }
    setStatus(state.statusKey, state.running);       // re-translate current status
    if (state.running) { relabelLive(); renderMonHeader(); }
    renderTargetChip();
    if ($("#proc-overlay").classList.contains("is-open")) {
      renderModeUI();
      renderProcList($("#proc-search").value);
    }
    if (state.lastReport && $("#view-report").classList.contains("is-active")) {
      UMReport.render($("#report-root"), state.lastReport);
    }
    UMUpdates.refresh();
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
    $("#pid-input").addEventListener("input", (e) => {
      e.target.value = e.target.value.replace(/[^0-9]/g, "");
      // Typing a PID by hand always means "just this one process".
      setTarget({ mode: "single", pid: parseInt(e.target.value, 10) || null, name: null, pids: [] });
    });
    $("#target-clear").addEventListener("click", () => {
      setTarget({ mode: "single", pid: parseInt($("#pid-input").value, 10) || null, name: null, pids: [] });
    });
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
    $$("#mode-toggle [data-mode]").forEach((b) => {
      b.addEventListener("click", () => setModalMode(b.getAttribute("data-mode")));
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && $("#proc-overlay").classList.contains("is-open")) closeProcModal();
    });
  }

  // --- Target (what the next session measures) ---

  function setTarget(next) {
    state.target = Object.assign({ mode: "single", pid: null, name: null, pids: [] }, next);
    renderTargetChip();
  }

  /** Processes covered by a target, resolved from the cached list for preview only. */
  function previewMembers(target) {
    const all = state.allProcs;
    if (!all.length) return [];
    if (target.mode === "name") {
      const n = (target.name || "").toLowerCase();
      return all.filter((p) => p.name.toLowerCase() === n);
    }
    if (target.mode === "tree") {
      const children = {};
      all.forEach((p) => { (children[p.ppid] = children[p.ppid] || []).push(p.pid); });
      const found = new Set([target.pid]);
      const stack = [target.pid];
      while (stack.length) {
        (children[stack.pop()] || []).forEach((pid) => {
          if (!found.has(pid)) { found.add(pid); stack.push(pid); }
        });
      }
      return all.filter((p) => found.has(p.pid));
    }
    if (target.mode === "set") {
      const want = new Set(target.pids);
      return all.filter((p) => want.has(p.pid));
    }
    return all.filter((p) => p.pid === target.pid);
  }

  function renderTargetChip() {
    const chip = $("#target-chip");
    const tg = state.target;
    if (tg.mode === "single") { chip.hidden = true; return; }

    const count = tg.mode === "set" ? tg.pids.length : previewMembers(tg).length;
    chip.hidden = false;
    $("#target-chip-label").textContent = tg.name || t("default.procName");
    $("#target-chip-mode").textContent =
      t("mode." + tg.mode + ".label") + " · " + UMi18n.tn("group.count", count);
    $("#target-clear").title = t("group.clear");
  }

  // --- Process picker modal ---

  async function openProcModal() {
    if (!state.api) return;
    $("#proc-overlay").classList.add("is-open");
    // Reopen with whatever is already chosen, so the modal never loses context.
    state.modal = {
      mode: state.target.mode,
      pid: state.target.pid,
      name: state.target.name,
      checked: state.target.mode === "set" ? state.target.pids.slice() : [],
    };
    $("#proc-search").value = "";
    $("#proc-list").innerHTML = `<div class="proc-empty">${esc(t("modal.loading"))}</div>`;
    renderModeUI();
    try {
      state.allProcs = await state.api.get_process_list();
      renderProcList("");
      $("#proc-search").focus();
    } catch (e) {
      $("#proc-list").innerHTML = `<div class="proc-empty">${esc(t("modal.loadFail"))}</div>`;
    }
  }
  function closeProcModal() { $("#proc-overlay").classList.remove("is-open"); }

  function setModalMode(mode) {
    if (MODES.indexOf(mode) < 0) return;
    state.modal.mode = mode;
    renderModeUI();
    renderProcList($("#proc-search").value);
  }

  function renderModeUI() {
    const mode = state.modal.mode;
    $$("#mode-toggle [data-mode]").forEach((b) => {
      b.classList.toggle("is-active", b.getAttribute("data-mode") === mode);
    });
    $("#mode-hint").textContent = t("mode." + mode + ".hint");
    $("#proc-list").classList.toggle("is-multi", mode === "set");
    renderModalSummary();
  }

  /** PIDs the current draft would measure — drives both the highlight and the count. */
  function modalMembers() {
    const m = state.modal;
    if (m.mode === "set") return m.checked.slice();
    if (m.pid == null) return [];
    return previewMembers({ mode: m.mode, pid: m.pid, name: m.name, pids: [] }).map((p) => p.pid);
  }

  function renderModalSummary() {
    const m = state.modal;
    const el = $("#proc-summary");
    const btn = $("#proc-select");

    if (m.mode === "set") {
      btn.disabled = m.checked.length === 0;
      el.innerHTML = m.checked.length
        ? t("modal.summary.checked", { count: m.checked.length })
        : esc(t("modal.summary.none"));
      return;
    }
    btn.disabled = m.pid == null;
    if (m.pid == null) { el.innerHTML = esc(t("modal.summary.none")); return; }

    if (m.mode === "single") {
      el.innerHTML = t("modal.summary.single", { name: esc(m.name || "?"), pid: m.pid });
    } else {
      el.innerHTML = t("modal.summary.group", {
        name: esc(m.name || "?"),
        count: UMi18n.tn("group.count", modalMembers().length),
      });
    }
  }

  function renderProcList(query) {
    const q = (query || "").toLowerCase().trim();
    const list = $("#proc-list");
    const mode = state.modal.mode;
    const items = state.allProcs.filter((p) =>
      !q || p.name.toLowerCase().includes(q) || String(p.pid).includes(q));
    if (!items.length) { list.innerHTML = `<div class="proc-empty">${esc(t("modal.noMatch"))}</div>`; return; }

    // How many processes share each name, so "same name" mode shows its reach up front.
    const byName = {};
    state.allProcs.forEach((p) => {
      const k = p.name.toLowerCase();
      byName[k] = (byName[k] || 0) + 1;
    });
    const kin = new Set(modalMembers());
    const checked = new Set(state.modal.checked);

    const frag = document.createDocumentFragment();
    items.slice(0, 400).forEach((p) => {
      const el = document.createElement("div");
      el.className = "proc-item";
      el.dataset.pid = p.pid;
      const siblings = byName[p.name.toLowerCase()] || 1;
      const badge = (mode === "name" && siblings > 1) ? `<span class="nsiblings">×${siblings}</span>` : "";
      el.innerHTML = `<input type="checkbox" class="box" ${checked.has(p.pid) ? "checked" : ""} />`
        + `<span class="pname"></span>${badge}<span class="ppid">PID ${p.pid}</span>`;
      el.querySelector(".pname").textContent = p.name;
      if (mode !== "set" && state.modal.pid === p.pid) el.classList.add("is-sel");
      if (mode !== "single" && kin.has(p.pid)) el.classList.add("is-kin");

      el.addEventListener("click", (ev) => {
        if (state.modal.mode === "set") {
          const box = el.querySelector(".box");
          if (ev.target !== box) box.checked = !box.checked;
          toggleChecked(p.pid, box.checked);
        } else {
          selectAnchor(p);
        }
      });
      el.addEventListener("dblclick", () => {
        if (state.modal.mode !== "set") { selectAnchor(p); confirmProcSelection(); }
      });
      frag.appendChild(el);
    });
    list.innerHTML = "";
    list.appendChild(frag);
  }

  function selectAnchor(p) {
    state.modal.pid = p.pid;
    state.modal.name = p.name;
    // Re-render so the highlight follows the new anchor's family.
    renderProcList($("#proc-search").value);
    renderModalSummary();
  }

  function toggleChecked(pid, on) {
    const set = new Set(state.modal.checked);
    if (on) set.add(pid); else set.delete(pid);
    state.modal.checked = Array.from(set);
    // Name the hand-picked group after whatever it mostly contains.
    const picked = state.allProcs.filter((p) => set.has(p.pid));
    const counts = {};
    picked.forEach((p) => { counts[p.name] = (counts[p.name] || 0) + 1; });
    state.modal.name = Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0] || null;
    $$(".proc-item").forEach((el) => el.classList.toggle("is-kin", set.has(parseInt(el.dataset.pid, 10))));
    renderModalSummary();
  }

  function confirmProcSelection() {
    const m = state.modal;
    if (m.mode === "set") {
      if (!m.checked.length) { toast(t("toast.noneChecked")); return; }
      setTarget({ mode: "set", pid: null, name: m.name, pids: m.checked.slice() });
      $("#pid-input").value = "";
    } else {
      if (m.pid == null) return;
      setTarget({ mode: m.mode, pid: m.pid, name: m.name, pids: [] });
      $("#pid-input").value = m.pid;
    }
    closeProcModal();
  }

  // --- Start / stop ---

  function targetSpec() {
    const tg = state.target;
    if (tg.mode === "single") {
      const pid = parseInt($("#pid-input").value, 10);
      return Number.isInteger(pid) && pid >= 0 ? { mode: "single", pid: pid } : null;
    }
    if (tg.mode === "set") return tg.pids.length ? { mode: "set", pids: tg.pids } : null;
    return { mode: tg.mode, pid: tg.pid, name: tg.name };
  }

  async function startMonitoring() {
    if (!state.api) { toast(t("toast.backendNotReady")); return; }
    const spec = targetSpec();
    if (!spec) { toast(t("toast.invalidPid")); return; }

    const btn = $("#start-btn");
    btn.disabled = true;
    let res;
    try { res = await state.api.start_monitoring(spec); }
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
    state.liveIsGroup = !!info.is_group;
    state.liveMetrics = UMReport.metricsFor(state.liveIsGroup);
    state.buf = { t: [], cpu_raw: [], cpu_norm: [], ram: [], procs: [] };
    state.liveCount = info.count || 1;
    $("#mon-name").firstChild.textContent = info.proc_name || t("default.procName");
    renderMonHeader();
    setStatus("monitoring", true);
    switchView("view-monitor");
    buildLiveUI();

    state.t0 = Date.now();
    $("#timer").textContent = "00:00:00";
    clearInterval(state.timer);
    state.timer = setInterval(tickTimer, 250);
  }

  /** The tag next to the monitored name: a PID, or a live headcount for a group. */
  function renderMonHeader() {
    $("#mon-pid").textContent = state.liveIsGroup
      ? UMi18n.tn("group.count", state.liveCount)
      : "PID " + (state.target.pid != null ? state.target.pid : $("#pid-input").value);
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
    state.liveMetrics.forEach((m) => {
      const el = document.createElement("div");
      el.className = "stat";
      el.innerHTML = `<span class="stat__label" data-live-label="${m.key}"></span>`
        + `<span class="stat__value">—<span class="unit">${esc(m.unit.trim())}</span></span>`;
      el.querySelector("[data-live-label]").textContent = t(m.nameKey);
      tiles.appendChild(el);
      state.tiles[m.key] = el.querySelector(".stat__value");
    });

    const wrap = $("#mon-charts");
    wrap.innerHTML = "";
    state.charts = {};
    state.liveMetrics.forEach((m) => {
      const card = document.createElement("div");
      card.className = "chart-card";
      card.innerHTML = `<div class="chart-head">
          <span class="series-key"><span class="dot" style="background:${m.color}"></span><span data-live-name="${m.key}">${esc(t(m.nameKey))}</span></span>
          <span class="chart-now" data-now="${m.key}">—</span>
        </div><div class="chart-mount"></div>`;
      wrap.appendChild(card);
      const mount = card.querySelector(".chart-mount");
      state.charts[m.key] = UMCharts.createLineChart(mount, { color: m.color, unit: m.unit, decimals: m.decimals });
    });
  }

  function relabelLive() {
    state.liveMetrics.forEach((m) => {
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
      b.procs.push(sample.procs != null ? sample.procs : 1);
      if (state.liveIsGroup && sample.procs != null && sample.procs !== state.liveCount) {
        state.liveCount = sample.procs;   // the group grew or shrank mid-session
        renderMonHeader();
      }
      state.liveMetrics.forEach((m) => {
        const v = sample[m.key];
        if (v == null) return;
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

    onUpdate(result) {
      UMUpdates.apply(result);
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
