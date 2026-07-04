// Report/summary renderer shared by the app's report view and the exported HTML file. Needs charts.js + i18n.js.
(function (global) {
  "use strict";

  const METRICS = [
    { key: "cpu_raw",  color: "var(--c-cpu)",  unit: "%",   decimals: 1, nameKey: "metric.cpu_raw.name",  noteKey: "metric.cpu_raw.note" },
    { key: "cpu_norm", color: "var(--c-cput)", unit: "%",   decimals: 1, nameKey: "metric.cpu_norm.name", noteKey: "metric.cpu_norm.note" },
    { key: "ram",      color: "var(--c-ram)",  unit: " MB", decimals: 1, nameKey: "metric.ram.name",      noteKey: "metric.ram.note" },
  ];

  const BRAND_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="#04120c" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 13h3l2.5 6 5-14L18 13h3"/></svg>';

  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const f = (v, d) => UMCharts.fmt(v, d);
  const t = (k, p) => UMi18n.t(k, p);

  function tile(label, value, unit, accent) {
    return `<div class="stat${accent ? " stat--accent" : ""}">
      <span class="stat__label">${esc(label)}</span>
      <span class="stat__value">${esc(value)}${unit ? `<span class="unit">${esc(unit)}</span>` : ""}</span>
    </div>`;
  }

  function metricCard(m, stat) {
    const s = stat || { min: 0, max: 0, avg: 0 };
    const u = esc(m.unit.trim());
    return `<div class="chart-card metric" data-key="${m.key}">
      <div class="chart-head">
        <div>
          <span class="series-key"><span class="dot" style="background:${m.color}"></span>${esc(t(m.nameKey))}</span>
          <div class="chart-sub">${esc(t(m.noteKey))}</div>
        </div>
        <div class="metric-stats">
          <span><b>${f(s.min, m.decimals)}<u>${u}</u></b><i>${esc(t("stat.min"))}</i></span>
          <span class="is-avg"><b>${f(s.avg, m.decimals)}<u>${u}</u></b><i>${esc(t("stat.avg"))}</i></span>
          <span><b>${f(s.max, m.decimals)}<u>${u}</u></b><i>${esc(t("stat.max"))}</i></span>
        </div>
      </div>
      <div class="chart-mount"></div>
    </div>`;
  }

  function logTable(data) {
    const s = data.series;
    const t0 = s.t || [], cr = s.cpu_raw || [], cn = s.cpu_norm || [], ram = s.ram || [];
    let rows = "";
    for (let i = 0; i < t0.length; i++) {
      rows += `<tr><td>${esc(t0[i])}</td><td>${f(cr[i], 1)}</td><td>${f(cn[i], 1)}</td><td>${f(ram[i], 1)}</td></tr>`;
    }
    return `<details class="report-logs">
      <summary>
        <span class="chev">▸</span>
        ${esc(t("log.summary"))}
        <span class="count">${t0.length}</span>
      </summary>
      <div class="logtable-wrap">
        <div class="logtable-scroll">
          <table class="logtable">
            <thead><tr>
              <th>${esc(t("log.col.time"))}</th>
              <th>${esc(t("log.col.cpuCore"))}</th>
              <th>${esc(t("log.col.cpuTotal"))}</th>
              <th>${esc(t("log.col.ram"))}</th>
            </tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </div>
    </details>`;
  }

  // render(root, data): body only. data is the report object built in core/report.py.
  function render(root, data) {
    const st = data.stats || {};
    const se = data.session || {};

    const tilesHtml = `<div class="report-tiles">
      ${tile(t("tile.start"), se.start || "—")}
      ${tile(t("tile.stop"), se.end || "—")}
      ${tile(t("tile.duration"), se.duration_str || "—", "", true)}
      ${tile(t("tile.samples"), (se.samples != null ? se.samples : (data.series.t || []).length))}
    </div>`;

    const metricsHtml = `<div class="report-metrics">
      ${METRICS.map((m) => metricCard(m, st[m.key])).join("")}
    </div>`;

    root.innerHTML = tilesHtml + metricsHtml + logTable(data);

    // Mount charts
    root.querySelectorAll(".metric").forEach((card) => {
      const m = METRICS.find((x) => x.key === card.dataset.key);
      const chart = UMCharts.createLineChart(card.querySelector(".chart-mount"), { color: m.color, unit: m.unit, decimals: m.decimals });
      chart.update(data.series[m.key] || [], data.series.t || []);
    });
  }

  // --- Standalone exported file: header, footer, and its own language toggle ---

  function renderHeader(root, data) {
    const meta = data.meta || {}, se = data.session || {};
    root.innerHTML = `<header class="rep-header">
        <span class="mark">${BRAND_SVG}</span>
        <div class="t">
          <h1>${esc(meta.app || "UsageMonitor")} — ${esc(t("report.title"))}</h1>
          <div class="sub">${esc(t("report.tagline"))}</div>
        </div>
        <div class="rep-lang"></div>
      </header>
      <div class="rep-title-row">
        <h2>${esc(meta.proc_name || "")}<span class="pid">PID ${esc(meta.pid)}</span></h2>
        <div class="gen">${esc(t("report.generated", { when: meta.generated_at || "" }))}</div>
      </div>
      <div class="rep-meta-line">${esc(t("report.meta", { cores: meta.cpu_count, interval: se.interval, samples: se.samples }))}</div>`;
    root.querySelector(".rep-lang").appendChild(UMi18n.createToggle());
  }

  function renderFoot(root, data) {
    const meta = data.meta || {};
    root.innerHTML = `${esc(meta.app || "UsageMonitor")} <span class="v">${esc(meta.version || "")}</span> · ${esc(t("footer.madeBy"))} `
      + `<a href="${esc(meta.author_url || "#")}" target="_blank" rel="noopener">${esc(meta.author_name || "MAZNET")}</a>`;
  }

  // Boots the standalone report page: header + body + footer, re-rendered on language change.
  function mountStandalone(data) {
    const h = document.getElementById("report-header");
    const b = document.getElementById("report-root");
    const foot = document.getElementById("report-foot");
    const draw = () => {
      if (h) renderHeader(h, data);
      render(b, data);
      if (foot) renderFoot(foot, data);
    };
    draw();
    UMi18n.onChange(draw);
  }

  global.UMReport = { render, mountStandalone, METRICS };
})(window);
