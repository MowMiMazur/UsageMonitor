// Dependency-free SVG line chart, shared by the app window and the exported HTML report.
(function (global) {
  "use strict";

  const SVGNS = "http://www.w3.org/2000/svg";
  const VBW = 760; // viewBox width
  const VBH = 240; // viewBox height
  const PAD = { l: 48, r: 16, t: 14, b: 26 };
  let _uid = 0;

  function el(name, attrs) {
    const n = document.createElementNS(SVGNS, name);
    if (attrs) for (const k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  }

  // Round Y-axis step to 1/2/5 * 10^n.
  function niceStep(range, targetTicks) {
    const rough = range / targetTicks;
    const mag = Math.pow(10, Math.floor(Math.log10(rough || 1)));
    const norm = rough / mag;
    let step;
    if (norm < 1.5) step = 1;
    else if (norm < 3) step = 2;
    else if (norm < 7) step = 5;
    else step = 10;
    return step * mag;
  }

  function fmt(v, decimals) {
    if (decimals === 0) return Math.round(v).toLocaleString("pl-PL");
    return v.toLocaleString("pl-PL", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  }

  // createLineChart(container, { color, unit, decimals }) -> { update(values, labels), element }
  function createLineChart(container, opts) {
    opts = opts || {};
    const color = opts.color || "#3987e5";
    const unit = opts.unit || "";
    const decimals = opts.decimals != null ? opts.decimals : 1;

    container.classList.add("chart-wrap");
    container.innerHTML = "";
    const uid = ++_uid;

    const svg = el("svg", { viewBox: `0 0 ${VBW} ${VBH}`, role: "img" });
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    // Drive series color via currentColor so marks follow the light/dark theme.
    svg.style.color = color;
    container.appendChild(svg);

    const tooltip = document.createElement("div");
    tooltip.className = "viz-tooltip";
    container.appendChild(tooltip);

    let state = { values: [], labels: [] };

    const gGrid = el("g", { class: "viz-grid" });
    const gAxis = el("g");
    const gPlot = el("g");
    const gOver = el("g");
    svg.appendChild(gGrid);
    svg.appendChild(gAxis);
    svg.appendChild(gPlot);
    svg.appendChild(gOver);

    const crosshair = el("line", { class: "viz-crosshair", y1: PAD.t, y2: VBH - PAD.b });
    const hoverDot = el("circle", { r: 4.5, fill: "currentColor", stroke: "var(--surface-1)", "stroke-width": 3, opacity: 0 });
    const hitRect = el("rect", { class: "viz-hit", x: PAD.l, y: PAD.t, width: VBW - PAD.l - PAD.r, height: VBH - PAD.t - PAD.b });
    gOver.appendChild(crosshair);
    gOver.appendChild(hoverDot);
    gOver.appendChild(hitRect);

    let scale = null;

    function computeScale(values) {
      let lo = Math.min.apply(null, values);
      let hi = Math.max.apply(null, values);
      if (!isFinite(lo)) { lo = 0; hi = 1; }
      if (lo === hi) { const p = hi === 0 ? 1 : Math.abs(hi) * 0.15; lo -= p; hi += p; }
      const step = niceStep(hi - lo, 5);
      let yMin = Math.floor(lo / step) * step;
      let yMax = Math.ceil(hi / step) * step;
      if (yMin < 0 && lo >= 0) yMin = 0;
      const plotW = VBW - PAD.l - PAD.r;
      const plotH = VBH - PAD.t - PAD.b;
      const n = values.length;
      return {
        yMin, yMax, step,
        xAt: (i) => PAD.l + (n <= 1 ? plotW / 2 : (i / (n - 1)) * plotW),
        yAt: (v) => PAD.t + plotH - ((v - yMin) / (yMax - yMin)) * plotH,
      };
    }

    function render() {
      const values = state.values;
      gGrid.innerHTML = "";
      gAxis.innerHTML = "";
      gPlot.innerHTML = "";

      if (!values.length) {
        const t = el("text", { x: VBW / 2, y: VBH / 2, "text-anchor": "middle", class: "viz-tick" });
        t.textContent = (global.UMi18n ? global.UMi18n.t("chart.collecting") : "…");
        gAxis.appendChild(t);
        scale = null;
        return;
      }

      scale = computeScale(values);
      const plotW = VBW - PAD.l - PAD.r;

      // Horizontal gridlines + Y labels
      for (let v = scale.yMin; v <= scale.yMax + 1e-9; v += scale.step) {
        const y = scale.yAt(v);
        gGrid.appendChild(el("line", { x1: PAD.l, x2: VBW - PAD.r, y1: y, y2: y }));
        const lbl = el("text", { x: PAD.l - 8, y: y + 3, "text-anchor": "end", class: "viz-tick" });
        lbl.textContent = fmt(v, scale.step < 1 ? 1 : 0);
        gAxis.appendChild(lbl);
      }

      // X baseline
      gAxis.appendChild(el("line", { class: "viz-axis", x1: PAD.l, x2: VBW - PAD.r, y1: VBH - PAD.b, y2: VBH - PAD.b }));

      // Up to 5 X time labels
      if (state.labels.length) {
        const n = values.length;
        const ticks = Math.min(5, n);
        for (let k = 0; k < ticks; k++) {
          const i = ticks === 1 ? n - 1 : Math.round((k / (ticks - 1)) * (n - 1));
          const x = scale.xAt(i);
          const t = el("text", {
            x: Math.max(PAD.l, Math.min(VBW - PAD.r, x)),
            y: VBH - PAD.b + 16,
            "text-anchor": k === 0 ? "start" : k === ticks - 1 ? "end" : "middle",
            class: "viz-tick",
          });
          t.textContent = state.labels[i] || "";
          gAxis.appendChild(t);
        }
      }

      // Line path + area fill
      let d = "", area = "";
      for (let i = 0; i < values.length; i++) {
        const x = scale.xAt(i), y = scale.yAt(values[i]);
        d += (i === 0 ? "M" : "L") + x.toFixed(2) + " " + y.toFixed(2) + " ";
      }
      const baseY = VBH - PAD.b;
      if (values.length === 1) {
        // Single sample: draw a flat line
        const y = scale.yAt(values[0]);
        d = `M${PAD.l} ${y.toFixed(2)} L${VBW - PAD.r} ${y.toFixed(2)}`;
      }
      area = d + `L${scale.xAt(values.length - 1).toFixed(2)} ${baseY} L${scale.xAt(0).toFixed(2)} ${baseY} Z`;

      // Area gradient (currentColor, theme-aware; id unique per chart)
      const gradId = "umgrad-" + uid;
      const defs = el("defs");
      const grad = el("linearGradient", { id: gradId, x1: 0, y1: 0, x2: 0, y2: 1 });
      grad.appendChild(el("stop", { offset: "0%", "stop-color": "currentColor", "stop-opacity": "0.20" }));
      grad.appendChild(el("stop", { offset: "100%", "stop-color": "currentColor", "stop-opacity": "0.02" }));
      defs.appendChild(grad);
      gPlot.appendChild(defs);

      gPlot.appendChild(el("path", { d: area, fill: `url(#${gradId})`, stroke: "none" }));
      gPlot.appendChild(el("path", { class: "viz-line", d: d }));

      // End dot with a surface ring
      const lastX = scale.xAt(values.length - 1), lastY = scale.yAt(values[values.length - 1]);
      gPlot.appendChild(el("circle", { cx: lastX, cy: lastY, r: 4.5, fill: "currentColor", stroke: "var(--surface-1)", "stroke-width": 3 }));
    }

    // Crosshair + tooltip
    function onMove(ev) {
      if (!scale || !state.values.length) return;
      const rect = svg.getBoundingClientRect();
      const vbX = ((ev.clientX - rect.left) / rect.width) * VBW;
      const n = state.values.length;
      const plotW = VBW - PAD.l - PAD.r;
      let i = Math.round(((vbX - PAD.l) / plotW) * (n - 1));
      i = Math.max(0, Math.min(n - 1, i));
      const x = scale.xAt(i), y = scale.yAt(state.values[i]);
      crosshair.setAttribute("x1", x); crosshair.setAttribute("x2", x); crosshair.setAttribute("opacity", 1);
      hoverDot.setAttribute("cx", x); hoverDot.setAttribute("cy", y); hoverDot.setAttribute("opacity", 1);

      const px = (x / VBW) * rect.width;
      const py = (y / VBH) * rect.height;
      tooltip.style.left = px + "px";
      tooltip.style.top = py + "px";
      tooltip.style.opacity = 1;
      const time = state.labels[i] ? `<div class="tt-time">${state.labels[i]}</div>` : "";
      tooltip.innerHTML = `${time}<div class="tt-val">${fmt(state.values[i], decimals)}${unit}</div>`;
    }
    function onLeave() {
      crosshair.setAttribute("opacity", 0);
      hoverDot.setAttribute("opacity", 0);
      tooltip.style.opacity = 0;
    }
    hitRect.addEventListener("mousemove", onMove);
    hitRect.addEventListener("mouseleave", onLeave);

    render();

    return {
      update(values, labels) {
        state.values = values || [];
        state.labels = labels || [];
        render();
      },
    };
  }

  global.UMCharts = { createLineChart, fmt };
})(window);
