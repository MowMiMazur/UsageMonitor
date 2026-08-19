// Update notice: the modal on start-up and the badge next to the footer version.
// Fed by Python (core/updates.py) through UM.onUpdate(); needs i18n.js.
(function (global) {
  "use strict";

  const $ = (s, r) => (r || document).querySelector(s);
  const t = (k, p) => UMi18n.t(k, p);
  const SKIP_KEY = "um_update_skip";

  const state = {
    info: null,      // last successful check result
    openUrl: null,   // (url) => void, provided by app.js
  };

  function skipped(version) {
    try { return localStorage.getItem(SKIP_KEY) === version; } catch (e) { return false; }
  }
  function setSkipped(version, on) {
    try {
      if (on) localStorage.setItem(SKIP_KEY, version);
      else localStorage.removeItem(SKIP_KEY);
    } catch (e) {}
  }

  function formatSize(bytes) {
    const n = Number(bytes);
    if (!Number.isFinite(n) || n <= 0) return null;
    const units = ["B", "kB", "MB", "GB"];
    let i = 0, v = n;
    while (v >= 1024 && i < units.length - 1) { v /= 1024; i++; }
    return (i === 0 ? v : v.toFixed(v < 10 ? 1 : 0)) + " " + units[i];
  }

  function formatDate(iso) {
    if (!iso) return null;
    const d = new Date(iso);
    if (isNaN(d.getTime())) return null;
    const locale = UMi18n.getLang() === "en" ? "en-GB" : "pl-PL";
    try {
      return d.toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" });
    } catch (e) { return d.toISOString().slice(0, 10); }
  }

  function openUrl(url) {
    if (!url) return;
    if (state.openUrl) state.openUrl(url);
    else window.open(url, "_blank");
  }

  // --- rendering ---

  function renderChip() {
    const chip = $("#update-chip");
    if (!chip) return;
    const info = state.info;
    const show = !!(info && info.available && info.latest);
    chip.hidden = !show;
    if (!show) return;
    $("#update-chip-text").textContent = t("update.chip", { latest: info.latest });
    chip.title = t("update.chipTitle");
  }

  function renderModal() {
    const info = state.info;
    if (!info || !info.available) return;

    $("#update-lede").textContent = t("update.lede", {
      name: info.name || "UsageMonitor",
      latest: info.latest,
      current: info.current,
    });
    $("#update-from").textContent = info.current;
    $("#update-to").textContent = info.latest;

    const meta = [];
    const date = formatDate(info.released_at);
    if (date) meta.push(t("update.released", { date: date }));
    if (info.channel && info.channel !== "stable") meta.push(info.channel);
    const size = info.download ? formatSize(info.download.size) : null;
    if (size) meta.push(size);
    const metaEl = $("#update-meta");
    metaEl.textContent = meta.join(" · ");
    metaEl.hidden = !meta.length;

    const direct = $("#update-direct");
    if (info.download && info.download.url) {
      direct.hidden = false;
      $("#update-direct-name").textContent = info.download.name || t("update.directLink");
    } else {
      direct.hidden = true;
    }

    $("#update-skip").checked = skipped(info.latest);
    $("#update-skip-label").textContent = t("update.skip");
  }

  function open() {
    if (!state.info || !state.info.available) return;
    renderModal();
    $("#update-overlay").classList.add("is-open");
  }
  function close() { $("#update-overlay").classList.remove("is-open"); }
  function isOpen() { return $("#update-overlay").classList.contains("is-open"); }

  // --- wiring ---

  function wire() {
    $("#update-chip").addEventListener("click", open);
    $("#update-later").addEventListener("click", close);
    $("#update-overlay").addEventListener("click", (e) => {
      if (e.target.id === "update-overlay") close();
    });
    $("#update-get").addEventListener("click", () => {
      if (state.info) openUrl(state.info.page);
      close();
    });
    $("#update-direct").addEventListener("click", (e) => {
      e.preventDefault();
      if (state.info && state.info.download) openUrl(state.info.download.url);
    });
    $("#update-skip").addEventListener("change", (e) => {
      if (state.info) setSkipped(state.info.latest, e.target.checked);
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && isOpen()) close();
    });
  }

  /** Called by app.js once the bridge is up. `opts.openUrl` hands links to Python. */
  function init(opts) {
    state.openUrl = (opts && opts.openUrl) || null;
    wire();
    renderChip();
  }

  /** Result of a check coming back from Python (or a manual re-check). */
  function apply(result) {
    if (!result || !result.ok) return;   // offline / 404 / rate-limited: stay silent
    state.info = result;
    renderChip();
    if (result.available && !skipped(result.latest)) open();
  }

  /** Re-render the visible strings after a language switch. */
  function refresh() {
    renderChip();
    if (isOpen()) renderModal();
  }

  global.UMUpdates = { init, apply, open, close, refresh };
})(window);
