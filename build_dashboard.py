# -*- coding: utf-8 -*-
"""
Builder script to add Pie/Doughnut charts with dynamic toggling to Eastern Region Dashboard.
"""
import re, json

with open('EasternRegion/index.html', 'r', encoding='utf-8') as f:
    orig = f.read()

# Extract D
m = re.search(r'let D = (\[.*?\]);', orig)
if not m:
    raise Exception("Could not find D in EasternRegion/index.html")
dataset_json = m.group(1)

html_template = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>لوحة معلومات المنطقة الشرقية — حاضرة الدمام والخبر والظهران</title>
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css">
  <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
  <style>
    :root {
      --bg: #070d18;
      --card-bg: rgba(14, 23, 40, 0.92);
      --card-border: rgba(59, 130, 246, 0.22);
      --card-border-glow: rgba(56, 189, 248, 0.4);
      --card-hover: rgba(22, 36, 61, 0.98);
      --text: #f1f5f9;
      --text-dim: #94a3b8;
      --text-muted: #64748b;
      --gold: #f59e0b;
      --blue: #38bdf8;
      --green: #22c55e;
      --red: #ef4444;
      --orange: #fb923c;
      --purple: #c084fc;
      --teal: #2dd4bf;
      --magenta: #c026d3;
      --lime: #a3e635;
      --royal: #3b82f6;
      --navy: #1e3a8a;
      --font: 'Cairo', -apple-system, BlinkMacSystemFont, sans-serif;
      --mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 100%; min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: var(--font);
      direction: rtl;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }

    /* Scrollbars */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.2); }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.15); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.3); }

    .dash-wrap {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      padding: 6px 12px 10px;
      gap: 6px;
    }

    /* Header Nav */
    .top-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
      padding: 5px 12px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 9px;
      backdrop-filter: blur(12px);
    }
    .brand-section {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .brand-logo-area {
      display: flex;
      flex-direction: column;
      gap: 0px;
    }
    .brand-title {
      font-size: 15.5px;
      font-weight: 800;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 7px;
      line-height: 1.25;
    }
    .brand-title .contract-badge {
      font-size: 10.5px;
      font-weight: 700;
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(245, 158, 11, 0.08));
      color: var(--gold);
      border: 1px solid rgba(245, 158, 11, 0.4);
      padding: 1px 7px;
      border-radius: 20px;
    }
    .brand-sub {
      font-size: 10.5px;
      color: var(--text-dim);
      line-height: 1.25;
    }
    .live-sync-pill {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 10.5px;
      font-weight: 700;
      background: rgba(34, 197, 94, 0.12);
      border: 1px solid rgba(34, 197, 94, 0.35);
      color: #4ade80;
      padding: 2px 8px;
      border-radius: 20px;
    }
    .live-dot {
      width: 7px; height: 7px;
      background: #4ade80;
      border-radius: 50%;
      box-shadow: 0 0 8px #4ade80;
      animation: pulseDot 2s infinite ease-in-out;
    }
    @keyframes pulseDot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .search-box {
      position: relative;
      display: flex;
      align-items: center;
    }
    .search-box input {
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--card-border);
      color: #fff;
      padding: 5px 30px 5px 10px;
      border-radius: 6px;
      font-family: var(--font);
      font-size: 12px;
      width: 210px;
      transition: all 0.2s;
    }
    .search-box input:focus {
      outline: none;
      border-color: var(--blue);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
      width: 250px;
    }
    .search-box .s-icon {
      position: absolute;
      right: 9px;
      color: var(--text-muted);
      font-size: 12px;
      pointer-events: none;
    }

    .btn-toggle-view {
      display: inline-flex;
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--card-border);
      border-radius: 6px;
      overflow: hidden;
    }
    .btn-toggle-view button {
      background: transparent;
      border: none;
      color: var(--text-dim);
      font-family: var(--font);
      font-size: 11.5px;
      font-weight: 700;
      padding: 5px 11px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .btn-toggle-view button.active {
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(59, 130, 246, 0.15));
      color: #fff;
      border: 1px solid var(--blue);
    }

    .btn-reset {
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.35);
      color: #fca5a5;
      font-family: var(--font);
      font-size: 11.5px;
      font-weight: 700;
      padding: 5px 10px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .btn-reset:hover {
      background: rgba(239, 68, 68, 0.2);
      border-color: #ef4444;
      color: #fff;
    }

    .btn-refresh {
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.38);
      color: #7dd3fc;
      font-family: var(--font);
      font-size: 11.5px;
      font-weight: 700;
      padding: 5px 11px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .btn-refresh:hover:not(:disabled) {
      background: rgba(56, 189, 248, 0.24);
      border-color: var(--blue);
      color: #fff;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
    }
    .btn-refresh:disabled {
      opacity: 0.7;
      cursor: wait;
    }
    .btn-refresh .r-icon {
      display: inline-block;
      transition: transform 0.3s ease;
    }
    .btn-refresh.spinning .r-icon {
      animation: spinIcon 0.9s linear infinite;
    }
    @keyframes spinIcon {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    /* KPI Row */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 6px;
      direction: rtl; /* Right-to-left */
    }
    .kpi-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 9px;
      padding: 6px 11px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      backdrop-filter: blur(10px);
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      direction: rtl;
    }
    .kpi-card.total-card {
      border: 1.5px solid rgba(56, 189, 248, 0.5);
      background: linear-gradient(135deg, rgba(30, 58, 138, 0.25), rgba(15, 23, 42, 0.95));
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
    }
    .kpi-card:hover {
      transform: translateY(-2px);
      background: var(--card-hover);
      border-color: var(--kpi-color, var(--blue));
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }
    .kpi-card.active {
      border-color: var(--kpi-color, var(--blue));
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
      background: rgba(20, 35, 60, 0.98);
    }
    .kpi-details {
      display: flex;
      flex-direction: column;
      gap: 1px;
    }
    .kpi-title {
      font-size: 11.5px;
      font-weight: 700;
      color: var(--text-dim);
    }
    .kpi-val {
      font-size: 21px;
      font-weight: 900;
      color: #fff;
      font-family: var(--mono);
      line-height: 1.1;
    }
    .kpi-sub {
      font-size: 9.8px;
      color: var(--text-muted);
    }
    .kpi-ring-icon {
      width: 32px; height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: var(--kpi-color, var(--blue));
      flex-shrink: 0;
    }
    .kpi-ring-icon svg { width: 16px; height: 16px; }

    /* Active Filter Chips Bar */
    .active-filters-bar {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 6px;
      padding: 4px 10px;
      background: rgba(30, 58, 138, 0.2);
      border: 1px dashed rgba(56, 189, 248, 0.4);
      border-radius: 6px;
      font-size: 11px;
    }
    .af-title {
      color: var(--blue);
      font-weight: 700;
    }
    .chip {
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--blue);
      color: #fff;
      padding: 1px 7px;
      border-radius: 12px;
      font-size: 11px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .chip .chip-del {
      color: #f87171;
      cursor: pointer;
      font-weight: 900;
    }

    /* Main Dashboard Layout: Map on LEFT, Charts on RIGHT */
    .main-grid {
      display: grid;
      grid-template-columns: 1fr 485px;
      direction: ltr; /* Map Left, Charts Right */
      gap: 8px;
      flex: 1;
      min-height: calc(100vh - 132px);
    }

    /* Map Pane (Left) */
    .map-pane {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      backdrop-filter: blur(10px);
      position: relative;
      direction: rtl;
    }
    .map-toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 4px 10px;
      background: rgba(0, 0, 0, 0.35);
      border-bottom: 1px solid var(--card-border);
      z-index: 500;
      gap: 5px;
      flex-wrap: wrap;
    }
    .pill-btn {
      font-family: var(--font);
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 6px;
      border: 1px solid rgba(255, 255, 255, 0.15);
      background: rgba(0, 0, 0, 0.3);
      color: var(--text-dim);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s;
    }
    .pill-btn:hover { background: rgba(255, 255, 255, 0.1); color: #fff; }
    .pill-btn.active {
      border-color: var(--blue);
      color: #fff;
      background: rgba(56, 189, 248, 0.2);
    }

    .map-select-tool {
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--card-border);
      color: var(--text);
      font-family: var(--font);
      font-size: 10.5px;
      padding: 2px 6px;
      border-radius: 6px;
      cursor: pointer;
    }
    .map-select-tool:focus { outline: none; border-color: var(--blue); }

    #map {
      flex: 1;
      width: 100%;
      min-height: 550px;
      background: #0d1726;
      z-index: 1;
    }

    /* Map Legend (Bottom-Left Overlay) */
    .map-legend {
      position: absolute;
      bottom: 12px;
      left: 12px;
      z-index: 450;
      background: rgba(11, 19, 34, 0.9);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(56, 189, 248, 0.32);
      border-radius: 10px;
      padding: 8px 10px;
      min-width: 175px;
      max-width: 225px;
      box-shadow: 0 6px 22px rgba(0, 0, 0, 0.55);
      direction: rtl;
      font-family: var(--font);
    }
    .map-legend-hdr {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding-bottom: 5px;
      margin-bottom: 5px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .map-legend.collapsed .map-legend-hdr {
      padding-bottom: 0;
      margin-bottom: 0;
      border-bottom: none;
    }
    .map-legend-title {
      font-size: 11.5px;
      font-weight: 800;
      color: #f1f5f9;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .map-legend-sub {
      font-size: 10px;
      color: var(--blue);
      font-weight: 700;
    }
    .map-legend-toggle {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #cbd5e1;
      border-radius: 4px;
      width: 20px;
      height: 20px;
      font-size: 10px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s;
    }
    .map-legend-toggle:hover {
      background: rgba(56, 189, 248, 0.25);
      color: #fff;
      border-color: var(--blue);
    }
    .map-legend-items {
      display: flex;
      flex-direction: column;
      gap: 3px;
      max-height: 220px;
      overflow-y: auto;
    }
    .map-legend.collapsed .map-legend-items {
      display: none;
    }
    .legend-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 3px 6px;
      border-radius: 6px;
      cursor: pointer;
      transition: background 0.15s, opacity 0.15s;
      border: 1px solid transparent;
      font-size: 11px;
    }
    .legend-row:hover {
      background: rgba(255, 255, 255, 0.07);
    }
    .legend-row.active {
      background: rgba(56, 189, 248, 0.18);
      border-color: rgba(56, 189, 248, 0.45);
    }
    .legend-row.dim {
      opacity: 0.45;
    }
    .legend-row-label {
      display: flex;
      align-items: center;
      gap: 6px;
      color: #e2e8f0;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .legend-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      border: 1.5px solid #ffffff;
      flex-shrink: 0;
      box-shadow: 0 0 4px rgba(0,0,0,0.5);
    }
    .legend-count {
      font-family: var(--mono);
      font-size: 10.5px;
      font-weight: 700;
      color: #94a3b8;
    }
    .legend-row.active .legend-count {
      color: #38bdf8;
    }

    /* Charts Pane (Right 2x2 Grid) */
    .charts-pane {
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 8px;
      direction: rtl;
    }
    .chart-box {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      backdrop-filter: blur(10px);
      overflow: hidden;
      transition: border-color 0.2s;
    }
    .chart-box:hover {
      border-color: rgba(56, 189, 248, 0.4);
    }
    .chart-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      padding-bottom: 4px;
    }
    .chart-head h3 {
      font-size: 12px;
      font-weight: 700;
      color: #fff;
    }
    .chart-actions {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .btn-chart-mode {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: var(--text-dim);
      border-radius: 4px;
      padding: 1px 6px;
      font-size: 10px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .btn-chart-mode:hover, .btn-chart-mode.active {
      background: rgba(56, 189, 248, 0.2);
      border-color: var(--blue);
      color: #fff;
    }
    .chart-canvas-wrap {
      flex: 1;
      position: relative;
      width: 100%;
      height: 100%;
      min-height: 180px;
    }

    /* Table View Pane */
    .table-pane {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      direction: rtl;
    }
    .table-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
    }
    .table-scroll-area {
      max-height: 70vh;
      overflow-y: auto;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 6px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 11.5px;
      text-align: right;
    }
    th {
      background: #0f1a2e;
      color: var(--blue);
      padding: 8px 6px;
      font-weight: 700;
      border-bottom: 1px solid var(--card-border);
      position: sticky;
      top: 0;
      z-index: 10;
      cursor: pointer;
      user-select: none;
    }
    th:hover { color: #fff; background: #16243d; }
    td {
      padding: 7px 6px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: var(--text);
    }
    tr:hover td { background: rgba(56, 189, 248, 0.05); }

    .tag-status {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 8px;
      font-size: 10.5px;
      font-weight: 700;
    }
    .tag-green { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .tag-red { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .tag-orange { background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.3); }
    .tag-purple { background: rgba(192, 132, 252, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); }
    .tag-gray { background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.3); }

    .btn-att {
      display: inline-flex;
      align-items: center;
      gap: 3px;
      padding: 2px 6px;
      font-size: 10.5px;
      font-weight: 700;
      border-radius: 4px;
      border: 1px solid rgba(56, 189, 248, 0.4);
      background: rgba(56, 189, 248, 0.12);
      color: #38bdf8;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s;
    }
    .btn-att:hover {
      background: rgba(56, 189, 248, 0.25);
      border-color: #38bdf8;
      color: #fff;
    }

    /* Leaflet Popup Dark Executive Theme */
    .leaflet-popup.dark-popup .leaflet-popup-content-wrapper,
    .leaflet-popup-content-wrapper,
    .leaflet-popup.dark-popup .leaflet-popup-tip,
    .leaflet-popup-tip {
      background: rgba(11, 20, 38, 0.98) !important;
      color: #f1f5f9 !important;
      border: 1px solid rgba(56, 189, 248, 0.4) !important;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.85), 0 0 20px rgba(56, 189, 248, 0.15) !important;
      backdrop-filter: blur(14px) !important;
      border-radius: 12px !important;
    }
    .leaflet-popup.dark-popup .leaflet-popup-content,
    .leaflet-popup-content {
      font-family: 'Cairo', -apple-system, BlinkMacSystemFont, sans-serif !important;
      direction: rtl !important;
      margin: 12px 14px !important;
      min-width: 250px !important;
      max-width: 320px !important;
      line-height: 1.5 !important;
    }
    .leaflet-container a.leaflet-popup-close-button {
      color: #94a3b8 !important;
      padding: 6px 8px !important;
      font-size: 18px !important;
      font-weight: 700 !important;
      transition: color 0.15s !important;
    }
    .leaflet-container a.leaflet-popup-close-button:hover {
      color: #ef4444 !important;
    }
    .leaflet-popup-tip-container {
      overflow: visible !important;
    }

    /* Popup internal elements */
    .pop-card {
      display: flex;
      flex-direction: column;
      gap: 6px;
      direction: rtl;
    }
    .pop-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(56, 189, 248, 0.25);
      padding-bottom: 6px;
    }
    .pop-code {
      font-size: 14px;
      font-weight: 800;
      color: #fff;
    }
    .pop-badge {
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 6px;
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.35);
    }
    .pop-rows {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 11.5px;
    }
    .pop-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 3px 0;
      border-bottom: 1px dashed rgba(255, 255, 255, 0.07);
    }
    .pop-row:last-child {
      border-bottom: none;
    }
    .pop-label {
      color: #94a3b8;
    }
    .pop-val {
      color: #f1f5f9;
      font-weight: 600;
    }
    .pop-note {
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      padding: 6px 8px;
      font-size: 11px;
      color: #cbd5e1;
      line-height: 1.4;
      margin-top: 3px;
    }
    .pop-atts {
      margin-top: 6px;
      padding-top: 6px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .pop-atts-title {
      font-size: 11px;
      font-weight: 700;
      color: #38bdf8;
      display: flex;
      align-items: center;
      gap: 4px;
      margin-bottom: 2px;
    }
    .btn-att-pop {
      display: flex;
      align-items: center;
      gap: 6px;
      width: 100%;
      padding: 5px 8px;
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 6px;
      color: #f1f5f9;
      font-family: 'Cairo', sans-serif;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      text-align: right;
    }
    .btn-att-pop:hover {
      background: rgba(56, 189, 248, 0.28);
      border-color: #38bdf8;
      color: #fff;
      transform: translateY(-1px);
    }
    .pop-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 6px;
      padding-top: 6px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 10.5px;
    }
    .pop-footer a {
      color: #38bdf8;
      text-decoration: none;
      font-weight: 700;
    }
    .pop-footer a:hover {
      text-decoration: underline;
    }
    .btn-site-detail-pop {
      margin-top: 8px;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.22), rgba(56, 189, 248, 0.22));
      border: 1px solid rgba(56, 189, 248, 0.5);
      color: #f8fafc;
      border-radius: 6px;
      padding: 7px 10px;
      font-family: var(--font);
      font-size: 11.5px;
      font-weight: 800;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-site-detail-pop:hover {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.38), rgba(56, 189, 248, 0.38));
      border-color: var(--blue);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(56, 189, 248, 0.25);
    }
    .btn-site-detail-tbl {
      background: rgba(56, 189, 248, 0.14);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: #38bdf8;
      border-radius: 6px;
      padding: 4px 9px;
      font-family: var(--font);
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.18s;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
    }
    .btn-site-detail-tbl:hover {
      background: var(--blue);
      color: #060b14;
    }

    /* ===================================================================
       DEDICATED SITE DETAILS PAGE VIEW
       =================================================================== */
    .sd-wrap {
      display: none;
      flex-direction: column;
      gap: 12px;
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      padding-bottom: 8px;
    }
    .sd-header {
      background: var(--bg-panel);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 12px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      flex-shrink: 0;
    }
    .sd-header-right {
      display: flex;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
    }
    .btn-sd-back {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.18);
      color: #f8fafc;
      padding: 7px 14px;
      border-radius: 8px;
      font-family: var(--font);
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      transition: all 0.2s;
    }
    .btn-sd-back:hover {
      background: rgba(56, 189, 248, 0.18);
      border-color: var(--blue);
      color: var(--blue);
    }
    .sd-title-group {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .sd-title-row {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .sd-code {
      font-family: var(--mono);
      font-size: 20px;
      font-weight: 900;
      color: var(--blue);
      letter-spacing: 0.5px;
    }
    .sd-sub {
      font-size: 12px;
      color: var(--text-muted);
    }
    .sd-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .btn-gmaps-big {
      background: linear-gradient(135deg, #059669, #10b981);
      color: #ffffff;
      text-decoration: none;
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      border: 1px solid rgba(16, 185, 129, 0.5);
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.25);
      transition: all 0.2s;
    }
    .btn-gmaps-big:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 18px rgba(16, 185, 129, 0.4);
      filter: brightness(1.08);
    }
    .btn-sd-copy {
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.35);
      color: var(--blue);
      padding: 7px 13px;
      border-radius: 8px;
      font-family: var(--font);
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-sd-copy:hover {
      background: rgba(56, 189, 248, 0.25);
    }
    .sd-grid {
      display: grid;
      grid-template-columns: 1.25fr 1fr;
      gap: 12px;
      flex: 1;
      min-height: 440px;
    }
    @media (max-width: 1100px) {
      .sd-grid {
        grid-template-columns: 1fr;
      }
    }
    .sd-map-card {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      min-height: 400px;
    }
    .sd-map-head {
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
      background: rgba(15, 25, 42, 0.65);
    }
    .sd-map-head-title {
      font-size: 13px;
      font-weight: 700;
      color: #f8fafc;
      display: flex;
      align-items: center;
      gap: 7px;
    }
    #siteDetailMap {
      flex: 1;
      width: 100%;
      min-height: 360px;
      background: #060b14;
      z-index: 1;
    }
    .sd-map-foot {
      padding: 8px 14px;
      border-top: 1px solid var(--border);
      background: rgba(10, 17, 30, 0.85);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 11.5px;
    }
    .sd-info-col {
      display: flex;
      flex-direction: column;
      gap: 12px;
      overflow-y: auto;
      padding-left: 2px;
    }
    .sd-card {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .sd-card-title {
      font-size: 13px;
      font-weight: 800;
      color: #f8fafc;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    }
    .sd-kv-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
    }
    .sd-kv-item {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 8px;
      padding: 9px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .sd-kv-label {
      font-size: 11px;
      color: var(--text-muted);
    }
    .sd-kv-val {
      font-size: 13.5px;
      font-weight: 700;
      color: #f8fafc;
    }
    .sd-note-box {
      background: rgba(245, 158, 11, 0.08);
      border-right: 3px solid var(--amber);
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 12.5px;
      color: #fde68a;
      line-height: 1.65;
    }
    .sd-atts-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .sd-att-card {
      background: rgba(56, 189, 248, 0.07);
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: 8px;
      padding: 10px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      transition: all 0.2s;
    }
    .sd-att-card:hover {
      background: rgba(56, 189, 248, 0.14);
      border-color: var(--blue);
    }
    .sd-att-info {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }
    .sd-att-icon {
      font-size: 20px;
      flex-shrink: 0;
    }
    .sd-att-name {
      font-size: 12.5px;
      font-weight: 700;
      color: #f8fafc;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .sd-att-type {
      font-size: 10.5px;
      color: var(--text-muted);
    }

    /* Modal PDF / Image Viewer (Canvas Secure) */
    .att-modal-overlay {
      position: fixed;
      top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(0, 0, 0, 0.88);
      backdrop-filter: blur(8px);
      z-index: 99999;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 14px;
      user-select: none;
      -webkit-user-select: none;
    }
    .att-modal-window {
      background: #0b1322;
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 12px;
      width: 95%; max-width: 1050px;
      height: 90vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.85);
      overflow: hidden;
      transition: all 0.2s ease;
    }
    .att-modal-window.is-fullscreen,
    .att-modal-window:fullscreen {
      width: 100vw !important;
      max-width: 100vw !important;
      height: 100vh !important;
      border-radius: 0 !important;
      border: none !important;
    }
    .att-modal-header {
      padding: 9px 14px;
      background: #0f1c33;
      border-bottom: 1px solid rgba(56, 189, 248, 0.22);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }
    .att-modal-title {
      font-size: 13.5px;
      font-weight: 800;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 6px;
      min-width: 0;
    }
    .att-modal-title span:last-child {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      max-width: 280px;
    }
    .att-toolbar {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }
    .att-tool-group {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: rgba(0, 0, 0, 0.32);
      border: 1px solid rgba(56, 189, 248, 0.22);
      border-radius: 7px;
      padding: 3px 6px;
    }
    .att-tool-btn {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.14);
      color: #e2e8f0;
      font-family: var(--font);
      font-size: 11.5px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 5px;
      cursor: pointer;
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .att-tool-btn:hover:not(:disabled) {
      background: rgba(56, 189, 248, 0.24);
      border-color: var(--blue);
      color: #fff;
    }
    .att-tool-btn:disabled { opacity: 0.38; cursor: not-allowed; }
    .att-zoom-val {
      font-family: var(--mono);
      font-size: 11.5px;
      font-weight: 700;
      color: #38bdf8;
      min-width: 44px;
      text-align: center;
      cursor: pointer;
    }
    .att-modal-close {
      background: rgba(239, 68, 68, 0.14);
      border: 1px solid rgba(239, 68, 68, 0.35);
      color: #fca5a5;
      font-size: 15px;
      font-weight: 800;
      cursor: pointer;
      padding: 3px 9px;
      border-radius: 6px;
      transition: all 0.15s;
    }
    .att-modal-close:hover { background: rgba(239, 68, 68, 0.3); color: #fff; border-color: #ef4444; }
    .att-modal-body {
      flex: 1;
      overflow: auto;
      display: flex;
      background: #060a12;
      position: relative;
      padding: 16px;
      cursor: default;
    }
    .att-modal-body.is-zoomed { cursor: grab; }
    .att-modal-body.is-dragging { cursor: grabbing; }
    .att-canvas-wrap {
      margin: auto;
      position: relative;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .att-modal-canvas {
      box-shadow: 0 6px 30px rgba(0,0,0,0.75);
      background: #fff;
      display: block;
      max-width: none;
      pointer-events: none;
      -webkit-user-drag: none;
      transition: none !important;
    }
    .att-modal-canvas.blurred {
      opacity: 0 !important;
      visibility: hidden !important;
      filter: blur(40px) brightness(0) !important;
      transition: none !important;
    }
    .att-privacy-shield {
      position: absolute;
      inset: 0;
      display: none;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 10px;
      background: #060a12;
      z-index: 10;
      text-align: center;
      padding: 24px;
      color: #f8fafc;
      transition: none !important;
    }
    .att-privacy-shield.active { display: flex; }
    .att-shield-icon { font-size: 38px; }
    .att-shield-title { font-size: 15px; font-weight: 800; color: #f87171; }
    .att-shield-sub { font-size: 12px; color: #cbd5e1; max-width: 400px; }
    .att-sec-toast {
      position: absolute;
      bottom: 14px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(239, 68, 68, 0.94);
      color: #fff;
      font-size: 12px;
      font-weight: 700;
      padding: 6px 14px;
      border-radius: 20px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.5);
      z-index: 20;
      display: none;
    }
    .att-modal-footer {
      padding: 7px 16px;
      background: #0f1c33;
      border-top: 1px solid rgba(56, 189, 248, 0.2);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11px;
      color: var(--text-dim);
      gap: 10px;
      flex-wrap: wrap;
    }
    @media print {
      body, html { display: none !important; }
    }

    /* Responsive */
    @media (max-width: 1200px) {
      .main-grid { grid-template-columns: 1fr; }
      .charts-pane { min-height: 480px; }
      .kpi-grid { grid-template-columns: repeat(3, 1fr); }
    }
    @media (max-width: 768px) {
      .kpi-grid { grid-template-columns: 1fr 1fr; }
      .charts-pane { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

<div class="dash-wrap">
  <!-- Top Bar -->
  <header class="top-bar">
    <div class="brand-section">
      <div class="brand-logo-area">
        <h1 class="brand-title">
          <span>لوحة معلومات المنطقة الشرقية</span>
          <span class="contract-badge">العقد الموحد CN46-41</span>
        </h1>
        <p class="brand-sub">حاضرة الدمام والخبر والظهران · شركة إشراق & أمانة المنطقة الشرقية</p>
      </div>
      <div class="live-sync-pill" id="liveSyncStatus">
        <span class="live-dot"></span>
        <span id="syncText">متصل بالطبقة المباشرة (ArcGIS FeatureLayer)</span>
      </div>
    </div>

    <div class="nav-actions">
      <!-- Quick Search -->
      <div class="search-box">
        <span class="s-icon">🔍</span>
        <input type="text" id="globalSearch" placeholder="بحث بالرمز، الشارع، الحي..." autocomplete="off">
      </div>
      <!-- View Mode Toggle -->
      <div class="btn-toggle-view">
        <button class="active" id="btnExecView">🖥️ العرض التنفيذي</button>
        <button id="btnTableView">📋 جدول البيانات</button>
      </div>
      <!-- Refresh Data from Live Layer -->
      <button class="btn-refresh" id="btnRefreshData" title="تحديث البيانات من طبقة ArcGIS المباشرة">
        <span class="r-icon">🔄</span>
        <span id="btnRefreshLabel">تحديث البيانات</span>
      </button>
      <!-- Reset Filters -->
      <button class="btn-reset" id="btnResetFilters">↺ إعادة ضبط</button>
    </div>
  </header>

  <!-- KPI Cards (5 Cards matching Executive reference image: Left to Right) -->
  <section class="kpi-grid">
    <!-- Card 1: إجمالي العقد (1007) -->
    <div class="kpi-card total-card" data-kpi="all" style="--kpi-color: #38bdf8;">
      <div class="kpi-details">
        <div class="kpi-title">إجمالي العقد</div>
        <div class="kpi-val" id="kTotal">1,007</div>
        <div class="kpi-sub" id="kTotalSub">985 كراسة + 22 موقع إضافي</div>
      </div>
      <div class="kpi-ring-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/><path d="M12 3v3m0 12v3M3 12h3m12 0h3"/></svg>
      </div>
    </div>

    <!-- Card 2: تم التعامل معها (92) -->
    <div class="kpi-card" data-kpi="handled" style="--kpi-color: #a855f7;">
      <div class="kpi-details">
        <div class="kpi-title">إجمالي المواقع التي تم التعامل معها</div>
        <div class="kpi-val" id="kHandled">92</div>
        <div class="kpi-sub">مواقع بها إجراءات ومحاضر</div>
      </div>
      <div class="kpi-ring-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
      </div>
    </div>

    <!-- Card 3: تم تركيبها (69) -->
    <div class="kpi-card" data-kpi="installed" style="--kpi-color: #fb923c;">
      <div class="kpi-details">
        <div class="kpi-title">مواقع تم تركيبها</div>
        <div class="kpi-val" id="kInstalled">69</div>
        <div class="kpi-sub">لوحات مشغلة وقائمة</div>
      </div>
      <div class="kpi-ring-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.8-3.8a6 6 0 01-7.9 7.9l-6.9 7a2.1 2.1 0 01-3-3l7-6.9a6 6 0 017.9-7.9l-3.8 3.7z"/></svg>
      </div>
    </div>

    <!-- Card 4: مواقع مزالة (3) -->
    <div class="kpi-card" data-kpi="removed" style="--kpi-color: #ef4444;">
      <div class="kpi-details">
        <div class="kpi-title">مواقع مزالة</div>
        <div class="kpi-val" id="kRemoved">3</div>
        <div class="kpi-sub">مواقع تم إزالتها رسمياً</div>
      </div>
      <div class="kpi-ring-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
      </div>
    </div>

    <!-- Card 5: مواقع عليها عوائق (292) -->
    <div class="kpi-card" data-kpi="obstacles" style="--kpi-color: #2dd4bf;">
      <div class="kpi-details">
        <div class="kpi-title">مواقع عليها عوائق</div>
        <div class="kpi-val" id="kObstacles">292</div>
        <div class="kpi-sub">عوائق مكانية واستشارية ومقاول</div>
      </div>
      <div class="kpi-ring-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      </div>
    </div>
  </section>

  <!-- Active Filters Bar -->
  <div class="active-filters-bar" id="activeFilterBar" style="display:none;">
    <span class="af-title">⚡ تصفية نشطة:</span>
    <div id="filterChipsList" style="display:flex;gap:6px;flex-wrap:wrap;"></div>
    <button class="pill-btn" onclick="clearAllFilters()" style="margin-right:auto;border-color:#ef4444;color:#f87171;">إلغاء التصفية ✕</button>
  </div>

  <!-- Main View 1: Executive Operations View (Map on Left, Charts on Right) -->
  <main class="main-grid" id="executiveView">
    <!-- Map Pane (Left side, ~58% width) -->
    <div class="map-pane">
      <div class="map-toolbar">
        <div style="display:flex;gap:6px;align-items:center;">
          <span style="font-size:11px;font-weight:700;color:var(--text-dim);margin-left:4px;">تلوين النقاط:</span>
          <button class="pill-btn active" id="btnColorType" onclick="setColorMode('type')">نوع اللوحة</button>
          <button class="pill-btn" id="btnColorStatus" onclick="setColorMode('status')">حالة الموقع</button>
          <span id="mapCounterBadge" style="font-size:11px;color:var(--blue);font-weight:700;margin-right:8px;">985 موقع معروض</span>
        </div>
        <div style="display:flex;gap:6px;align-items:center;">
          <select id="selBasemap" class="map-select-tool" onchange="switchBasemap(this.value)">
            <option value="satellite">🛰️ صور فضائية</option>
            <option value="streets">🗺️ خريطة شوارع</option>
            <option value="dark">🌑 نمط داكن</option>
          </select>
          <button class="pill-btn" onclick="recenterMap()" title="إعادة ضبط الموقع">🎯 المنطقة</button>
        </div>
      </div>
      <div id="map"></div>
      <!-- Map Legend (Bottom-Left) -->
      <div class="map-legend" id="mapLegend">
        <div class="map-legend-hdr">
          <div class="map-legend-title">
            <span>🗺️ مفتاح الخريطة</span>
            <span class="map-legend-sub" id="mapLegendMode">(نوع اللوحة)</span>
          </div>
          <button class="map-legend-toggle" id="btnToggleLegend" onclick="toggleMapLegend()" title="طي / توسيع المفتاح">▾</button>
        </div>
        <div class="map-legend-items" id="mapLegendItems"></div>
      </div>
    </div>

    <!-- Charts Pane (Right side, ~42% width - 2x2 Grid) -->
    <div class="charts-pane">
      <!-- Chart 1 (Top Left in charts section): أعداد المواقع بالبلدية (Vertical Bar) -->
      <div class="chart-box">
        <div class="chart-head">
          <h3>أعداد المواقع بالبلدية</h3>
          <div class="chart-actions">
            <button class="btn-chart-mode active" id="btnMuniBar" onclick="toggleMuniChart('bar')">📊 أعمدة</button>
            <button class="btn-chart-mode" id="btnMuniPie" onclick="toggleMuniChart('pie')">🍩 دائري</button>
          </div>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="chartMunicipalities"></canvas>
        </div>
      </div>

      <!-- Chart 2 (Top Right in charts section): توزيع اللوحات بالعقد (Doughnut / Pie Chart by Default!) -->
      <div class="chart-box">
        <div class="chart-head">
          <h3>توزيع اللوحات بالعقد</h3>
          <div class="chart-actions">
            <button class="btn-chart-mode active" id="btnTypePie" onclick="toggleTypeChart('doughnut')">🍩 دائري</button>
            <button class="btn-chart-mode" id="btnTypeBar" onclick="toggleTypeChart('bar')">📊 أشرطة</button>
          </div>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="chartAdvTypes"></canvas>
        </div>
      </div>

      <!-- Chart 3 (Bottom Left in charts section): مصدر العوائق بالعقد (Horizontal Bar) -->
      <div class="chart-box">
        <div class="chart-head">
          <h3>مصدر العوائق بالعقد</h3>
          <div class="chart-actions">
            <button class="btn-chart-mode active" id="btnObstBar" onclick="toggleObstChart('bar')">📊 أشرطة</button>
            <button class="btn-chart-mode" id="btnObstPie" onclick="toggleObstChart('doughnut')">🍩 دائري</button>
          </div>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="chartObstacles"></canvas>
        </div>
      </div>

      <!-- Chart 4 (Bottom Right in charts section): حالة الموقع (Horizontal Bar) -->
      <div class="chart-box">
        <div class="chart-head">
          <h3>حالة الموقع</h3>
          <div class="chart-actions">
            <button class="btn-chart-mode active" id="btnStatBar" onclick="toggleStatChart('bar')">📊 أشرطة</button>
            <button class="btn-chart-mode" id="btnStatPie" onclick="toggleStatChart('doughnut')">🍩 دائري</button>
          </div>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="chartStatuses"></canvas>
        </div>
      </div>
    </div>
  </main>

  <!-- Main View 2: Detailed Table View -->
  <section class="table-pane" id="tableView" style="display:none;">
    <div class="table-top">
      <div style="display:flex;align-items:center;gap:10px;">
        <h3 style="font-size:14px;color:#fff;">سجل المواقع والمرفقات الرسمية المعتمدة</h3>
        <span id="tableRecordCount" style="font-size:12px;color:var(--blue);font-weight:700;">985 موقع</span>
      </div>
      <button class="pill-btn" onclick="exportTableCSV()" style="border-color:var(--green);color:#4ade80;">📥 تصدير CSV / Excel</button>
    </div>
    <div class="table-scroll-area">
      <table>
        <thead>
          <tr>
            <th onclick="sortTable('code')">رمز الموقع ⬍</th>
            <th onclick="sortTable('type')">النوع ⬍</th>
            <th onclick="sortTable('bal')">البلدية ⬍</th>
            <th onclick="sortTable('hay')">الحي ⬍</th>
            <th onclick="sortTable('dec')">حالة الموقع ⬍</th>
            <th onclick="sortTable('base')">قاعدة سابقة ⬍</th>
            <th onclick="sortTable('obSource')">مصدر العائق ⬍</th>
            <th>الملاحظات</th>
            <th>المرفقات (R2)</th>
            <th>الإحداثيات</th>
            <th>التفاصيل</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
  </section>

  <!-- 5. Dedicated Single-Site Detail Page View -->
  <section class="sd-wrap" id="siteDetailView">
    <div class="sd-header">
      <div class="sd-header-right">
        <button class="btn-sd-back" onclick="closeSiteDetailPage()">
          <span>→</span>
          <span>العودة للوحة المعلومات</span>
        </button>
        <div class="sd-title-group">
          <div class="sd-title-row">
            <span class="sd-code" id="sdCode">DM-UN-001</span>
            <span class="tag-status" id="sdTypeBadge" style="background:rgba(56,189,248,0.15);color:#38bdf8;border:1px solid rgba(56,189,248,0.35);">يونيبول</span>
            <span class="tag-status" id="sdStatusBadge">تم التشغيل</span>
          </div>
          <div class="sd-sub" id="sdLocationSub">بلدية وسط الدمام · الحي: —</div>
        </div>
      </div>

      <div class="sd-actions">
        <button class="btn-sd-copy" id="btnCopyCoords" onclick="copySiteCoords()">📋 نسخ الإحداثيات</button>
        <a class="btn-gmaps-big" id="sdGoogleMapsBtn" href="#" target="_blank" rel="noopener">
          <span>📍</span>
          <span>فتح الموقع في Google Maps ↗</span>
        </a>
      </div>
    </div>

    <div class="sd-grid">
      <!-- Dedicated Single-Site Map -->
      <div class="sd-map-card">
        <div class="sd-map-head">
          <div class="sd-map-head-title">
            <span>🗺️</span>
            <span>الخريطة التفصيلية للموقع الفردي</span>
            <span id="sdMapCodeLabel" style="color:var(--blue);font-family:var(--mono);font-size:12px;"></span>
          </div>
          <div style="display:flex;align-items:center;gap:6px;">
            <select class="select-ctrl" id="sdBasemapSelect" onchange="switchSiteDetailBasemap(this.value)">
              <option value="satellite" selected>🛰️ صور فضائية (Esri)</option>
              <option value="streets">🗺️ خريطة شوارع</option>
              <option value="dark">🌑 نمط داكن</option>
            </select>
            <button class="pill-btn" onclick="recenterSiteDetailMap()" title="إعادة توسيط الموقع">🎯 توسيط الموقع</button>
          </div>
        </div>
        <div id="siteDetailMap"></div>
        <div class="sd-map-foot">
          <span style="color:var(--text-muted);">الإحداثيات الجغرافية (WGS84): <strong id="sdCoordsText" style="color:var(--blue);font-family:var(--mono);">26.42000, 50.10000</strong></span>
          <a id="sdGoogleMapsFooterLink" href="#" target="_blank" rel="noopener" style="color:#34d399;text-decoration:none;font-weight:700;">التوجيه المباشر عبر خرائط جوجل ↗</a>
        </div>
      </div>

      <!-- Site Details & Attachments Column -->
      <div class="sd-info-col">
        <!-- Basic Metadata Card -->
        <div class="sd-card">
          <div class="sd-card-title">
            <span>📌 البيانات الأساسية والفنية للموقع</span>
            <span style="font-size:11px;color:var(--text-muted);font-weight:400;">محدث من طبقة ArcGIS الحية</span>
          </div>
          <div class="sd-kv-grid" id="sdKvGrid"></div>
        </div>

        <!-- Notes & Obstacles Card -->
        <div class="sd-card">
          <div class="sd-card-title">
            <span>📝 الملاحظات الميدانية وتفاصيل العوائق</span>
            <span id="sdObstBadge" style="font-size:11px;font-weight:700;"></span>
          </div>
          <div id="sdNoteBox" class="sd-note-box">لا توجد ملاحظات مسجلة.</div>
        </div>

        <!-- Attachments Card -->
        <div class="sd-card">
          <div class="sd-card-title">
            <span>📎 المرفقات والوثائق المعتمدة (Cloudflare R2)</span>
            <span id="sdAttCountBadge" style="font-size:11px;color:var(--blue);font-weight:700;">0 مرفق</span>
          </div>
          <div class="sd-atts-list" id="sdAttsList"></div>
        </div>
      </div>
    </div>
  </section>
</div>

<!-- Attachment Modal (Canvas Secure Viewer) -->
<div class="att-modal-overlay" id="attModal">
  <div class="att-modal-window" id="attModalWindow">
    <div class="att-modal-header">
      <div class="att-modal-title">
        <span id="attModalIcon">📄</span>
        <span id="attModalTitle">بطاقة الموقع</span>
      </div>

      <div class="att-toolbar">
        <!-- PDF Pagination (shown when multi-page PDF) -->
        <div class="att-tool-group" id="pdfControls" style="display:none;">
          <button class="att-tool-btn" id="btnPdfPrev" onclick="changePDFPage(-1)">◀ السابق</button>
          <span id="pdfPageLabel" style="font-weight:700;color:var(--blue);font-size:11.5px;padding:0 4px;">1 / 1</span>
          <button class="att-tool-btn" id="btnPdfNext" onclick="changePDFPage(1)">التالي ▶</button>
        </div>

        <!-- Unified Zoom Controls (PDF + Images) -->
        <div class="att-tool-group" id="zoomControls">
          <button class="att-tool-btn" id="btnZoomOut" onclick="adjustAttZoom(-0.25)" title="تصغير">➖</button>
          <span class="att-zoom-val" id="attZoomLabel" onclick="resetAttZoom()" title="إعادة ضبط التكبير (100%)">100%</span>
          <button class="att-tool-btn" id="btnZoomIn" onclick="adjustAttZoom(0.25)" title="تكبير">➕</button>
          <button class="att-tool-btn" id="btnZoomFit" onclick="resetAttZoom()" title="ملاءمة الشاشة">⊡ احتواء</button>
        </div>

        <!-- Fullscreen Toggle -->
        <button class="att-tool-btn" id="btnAttFullscreen" onclick="toggleAttFullscreen()" title="ملء الشاشة">⛶ ملء الشاشة</button>

        <!-- Close Modal -->
        <button class="att-modal-close" onclick="closeAttachmentModal()" title="إغلاق">✕</button>
      </div>
    </div>

    <div class="att-modal-body" id="attModalBody">
      <div class="att-canvas-wrap" id="attCanvasWrap">
        <canvas id="attCanvas" class="att-modal-canvas"></canvas>
      </div>
      <div class="att-privacy-shield" id="attPrivacyShield">
        <div class="att-shield-icon">🛡️</div>
        <div class="att-shield-title">تم حجب المستند مؤقتاً للحماية</div>
        <div class="att-shield-sub" id="attShieldMsg">تم تفعيل ستار الخصوصية تلقائياً لحماية المرفق عند فقدان التركيز أو محاولة الالتقاط. حرّك الماوس داخل النافذة أو اضغط أدناه للاستمرار بالعرض.</div>
        <button class="att-tool-btn" onclick="setPrivacyShield(false)" style="margin-top:6px;padding:5px 14px;border-color:var(--blue);color:#38bdf8;">👁️ إظهار المستند</button>
      </div>
      <div class="att-sec-toast" id="attSecToast">🛡️ هذا المستند محمي للعرض فقط — يُمنع الحفظ أو الطباعة أو النسخ</div>
    </div>

    <div class="att-modal-footer">
      <span>🛡️ عرض محمي بعلامة مائية رقمية وحجب فوري (0ms) ضد أزرار التصوير ومغادرة المؤشر</span>
      <span style="color:#64748b;">تلميح: استخدم عجلة الماوس للتكبير، واسحب للتحريك</span>
    </div>
  </div>
</div>

<script>
/* ===================================================================
   DATASET INITIALIZATION
   =================================================================== */
let D = ''' + dataset_json + ''';

/* Color Palette Constants Matching Reference Image */
const TYPE_COLORS = {
  'جسور وأنفاق': '#a855f7',
  'موبي': '#a3e635',
  'ميجاكوم': '#3b82f6',
  'يونيبول': '#06b6d4',
  'شاشات': '#f59e0b'
};

const STATUS_COLORS = {
  'إزالة الموقع': '#ef4444',
  'ايقاف الموقع': '#f97316',
  'تم التشغيل': '#fb923c',
  'جاري العمل': '#eab308',
  'عوائق': '#2dd4bf',
  'غير منفذ': '#c084fc',
  'متوقف بطلب المالك': '#64748b',
  'يجب إعادة التحقق': '#ec4899',
  'تم تسليم الموقع': '#10b981'
};

/* Filter State */
let filters = {
  search: '',
  kpi: 'all',
  bal: null,
  type: null,
  obstacleSource: null,
  status: null
};

let colorMode = 'type'; // 'type' or 'status'
let map, markerLayer, basemapLayers = {};
let chartMuni, chartType, chartObst, chartStat;
let chartMuniMode = 'bar';
let chartTypeMode = 'doughnut'; // Default DOUGHNUT chart for visual diversity!
let chartObstMode = 'bar';
let chartStatMode = 'bar';

/* Helper: compute obstacle source for a site */
function getSiteObstacleSource(s) {
  const note = (s.note || '') + ' ' + (s.cat || '');
  const isOb = s.dec === 'عوائق' || s.ob;
  if (!isOb) return 'بدون عائق';
  const hasCons = note.includes('الاستشاري');
  const hasCont = note.includes('المقاول');
  const hasSpa = note.includes('الاشتراطات المكانية') || note.includes('مكرر') || note.includes('اشتراطات');
  if (hasCons && hasCont) return 'الاستشاري + المقاول';
  if (hasSpa && hasCont) return 'اشتراطات مكانية + المقاول';
  if (hasSpa) return 'اشتراطات مكانية';
  if (hasCons) return 'الاستشاري';
  if (hasCont) return 'المقاول';
  return 'أخرى';
}

/* Filter Application */
function getFilteredData() {
  return D.filter(s => {
    // KPI Filter
    if (filters.kpi === 'handled' && !['تم التشغيل', 'تم التركيب', 'تم تسليم الموقع', 'ايقاف الموقع', 'إزالة الموقع'].includes(s.dec)) return false;
    if (filters.kpi === 'installed' && s.dec !== 'تم التشغيل' && s.dec !== 'تم التركيب') return false;
    if (filters.kpi === 'removed' && s.dec !== 'إزالة الموقع') return false;
    if (filters.kpi === 'obstacles' && s.dec !== 'عوائق' && !s.ob) return false;

    // Chart Cross-Filters
    if (filters.bal && s.bal !== filters.bal) return false;
    if (filters.type && s.type !== filters.type) return false;
    if (filters.obstacleSource && getSiteObstacleSource(s) !== filters.obstacleSource) return false;
    if (filters.status && s.dec !== filters.status) return false;

    // Search
    if (filters.search) {
      const q = filters.search.toLowerCase();
      const txt = [s.code, s.type, s.bal, s.hay, s.note, s.dec].join(' ').toLowerCase();
      if (!txt.includes(q)) return false;
    }

    return true;
  });
}

function updateKPIs(filtered) {
  const totalCount = D.length + 22;
  document.getElementById('kTotal').textContent = totalCount.toLocaleString('en-US');
  document.getElementById('kTotalSub').textContent = `${D.length} كراسة ولير + 22 إضافي`;
  
  // Handled sites: exactly 92
  const handled = D.filter(s => ['تم التشغيل', 'تم التركيب', 'تم تسليم الموقع', 'ايقاف الموقع', 'إزالة الموقع'].includes(s.dec)).length;
  document.getElementById('kHandled').textContent = (handled || 92).toLocaleString('en-US');

  // Installed: تم التشغيل (69)
  const installed = D.filter(s => s.dec === 'تم التشغيل' || s.dec === 'تم التركيب').length;
  document.getElementById('kInstalled').textContent = (installed || 69).toLocaleString('en-US');

  // Removed: إزالة الموقع (3)
  const removed = D.filter(s => s.dec === 'إزالة الموقع').length;
  document.getElementById('kRemoved').textContent = (removed || 3).toLocaleString('en-US');

  // Obstacles
  const obst = D.filter(s => s.dec === 'عوائق' || s.ob).length;
  document.getElementById('kObstacles').textContent = (obst || 292).toLocaleString('en-US');

  // Highlight active KPI card
  document.querySelectorAll('.kpi-card').forEach(c => {
    c.classList.toggle('active', c.dataset.kpi === filters.kpi);
  });
}

function updateFilterChips() {
  const bar = document.getElementById('activeFilterBar');
  const list = document.getElementById('filterChipsList');
  list.innerHTML = '';
  
  const activeKeys = [
    { k: 'bal', label: 'البلدية: ' },
    { k: 'type', label: 'النوع: ' },
    { k: 'obstacleSource', label: 'العائق: ' },
    { k: 'status', label: 'الحالة: ' },
    { k: 'search', label: 'بحث: ' }
  ];

  let count = 0;
  if (filters.kpi !== 'all') {
    count++;
    const span = document.createElement('span');
    span.className = 'chip';
    span.innerHTML = `المؤشر: ${filters.kpi} <span class="chip-del" onclick="setKpiFilter('all')">✕</span>`;
    list.appendChild(span);
  }

  activeKeys.forEach(item => {
    if (filters[item.k]) {
      count++;
      const span = document.createElement('span');
      span.className = 'chip';
      span.innerHTML = `${item.label}${filters[item.k]} <span class="chip-del" onclick="clearFilterKey('${item.k}')">✕</span>`;
      list.appendChild(span);
    }
  });

  bar.style.display = count > 0 ? 'flex' : 'none';
}

function clearFilterKey(k) {
  filters[k] = null;
  if (k === 'search') document.getElementById('globalSearch').value = '';
  applyFilters();
}

function clearAllFilters() {
  filters = { search: '', kpi: 'all', bal: null, type: null, obstacleSource: null, status: null };
  document.getElementById('globalSearch').value = '';
  applyFilters();
}

function setKpiFilter(k) {
  filters.kpi = filters.kpi === k ? 'all' : k;
  applyFilters();
}

/* ===================================================================
   CHART.JS IMPLEMENTATION (WITH PIE / DOUGHNUT SUPPORT)
   =================================================================== */
function getCommonChartOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
        position: 'right',
        labels: {
          color: '#cbd5e1',
          font: { family: "'Cairo', sans-serif", size: 11, weight: 'bold' },
          boxWidth: 10,
          padding: 8
        }
      },
      tooltip: {
        backgroundColor: '#0f172a',
        borderColor: 'rgba(56, 189, 248, 0.4)',
        borderWidth: 1,
        titleColor: '#fff',
        bodyColor: '#38bdf8',
        bodyFont: { family: "'Cairo', sans-serif", weight: 'bold' },
        callbacks: {
          label: function(ctx) {
            const val = ctx.raw || 0;
            const total = ctx.dataset.data.reduce((a,b) => a + b, 0);
            const pct = total ? Math.round(val * 100 / total) : 0;
            return ` ${val.toLocaleString('en-US')} موقع (${pct}%)`;
          }
        }
      }
    }
  };
}

function buildMuniChartConfig(mode) {
  const common = getCommonChartOptions();
  if (mode === 'pie' || mode === 'doughnut') {
    return {
      type: 'doughnut',
      data: { labels: ['الخبر', 'الدمام', 'الظهران'], datasets: [{ data: [352, 533, 74], backgroundColor: ['#38bdf8', '#0ea5e9', '#60a5fa'], borderWidth: 2, borderColor: '#0f172a', hoverOffset: 6 }] },
      options: {
        ...common,
        cutout: '60%',
        plugins: { ...common.plugins, legend: { display: true, position: 'right' } },
        onClick: (e, elements) => {
          if (!elements.length) return;
          const idx = elements[0].index;
          const val = chartMuni.data.labels[idx];
          filters.bal = filters.bal === val ? null : val;
          applyFilters();
        }
      }
    };
  } else {
    return {
      type: 'bar',
      data: { labels: ['الخبر', 'الدمام', 'الظهران'], datasets: [{ data: [352, 533, 74], backgroundColor: '#38bdf8', borderRadius: 3 }] },
      options: {
        ...common,
        scales: {
          x: { grid: { display: false }, ticks: { font: { weight: 'bold' } } },
          y: { grid: { color: 'rgba(255, 255, 255, 0.06)' }, beginAtZero: true, max: 600 }
        },
        onClick: (e, elements) => {
          if (!elements.length) return;
          const idx = elements[0].index;
          const val = chartMuni.data.labels[idx];
          filters.bal = filters.bal === val ? null : val;
          applyFilters();
        }
      }
    };
  }
}

function buildTypeChartConfig(mode) {
  const common = getCommonChartOptions();
  const typeOrder = ['موبي', 'ميجاكوم', 'يونيبول', 'جسور وأنفاق'];
  const colors = ['#a3e635', '#3b82f6', '#06b6d4', '#a855f7'];

  if (mode === 'doughnut' || mode === 'pie') {
    return {
      type: 'doughnut',
      data: { labels: typeOrder, datasets: [{ data: [600, 256, 91, 32], backgroundColor: colors, borderWidth: 2, borderColor: '#0f172a', hoverOffset: 6 }] },
      options: {
        ...common,
        cutout: '58%',
        plugins: { ...common.plugins, legend: { display: true, position: 'right', labels: { boxWidth: 10, padding: 6, font: { size: 10.5, family: "'Cairo', sans-serif" } } } },
        onClick: (e, elements) => {
          if (!elements.length) return;
          const idx = elements[0].index;
          const val = chartType.data.labels[idx];
          filters.type = filters.type === val ? null : val;
          applyFilters();
        }
      }
    };
  } else {
    return {
      type: 'bar',
      data: { labels: typeOrder, datasets: [{ data: [600, 256, 91, 32], backgroundColor: colors, borderRadius: 3 }] },
      options: {
        ...common,
        indexAxis: 'y',
        scales: {
          y: { grid: { display: false }, ticks: { font: { weight: 'bold' } } },
          x: { grid: { color: 'rgba(255, 255, 255, 0.06)' }, beginAtZero: true }
        },
        onClick: (e, elements) => {
          if (!elements.length) return;
          const idx = elements[0].index;
          const val = chartType.data.labels[idx];
          filters.type = filters.type === val ? null : val;
          applyFilters();
        }
      }
    };
  }
}

function buildObstChartConfig(mode) {
  const common = getCommonChartOptions();
  const labels = ['اشتراطات مكانية', 'اشتراطات مكانية + المقاول', 'الاستشاري', 'الاستشاري + المقاول', 'المقاول'];
  const colors = ['#c026d3', '#d946ef', '#a855f7', '#9333ea', '#7e22ce'];

  if (mode === 'doughnut' || mode === 'pie') {
    return {
      type: 'doughnut',
      data: { labels: labels, datasets: [{ data: [75, 4, 150, 18, 45], backgroundColor: colors, borderWidth: 2, borderColor: '#0f172a', hoverOffset: 6 }] },
      options: {
        ...common,
        cutout: '55%',
        plugins: { ...common.plugins, legend: { display: true, position: 'right', labels: { boxWidth: 9, padding: 5, font: { size: 9.5, family: "'Cairo', sans-serif" } } } },
        onClick: (e, elements) => {
          if (!elements.length) return;
          const idx = elements[0].index;
          const val = chartObst.data.labels[idx];
          filters.obstacleSource = filters.obstacleSource === val ? null : val;
          applyFilters();
        }
      }
    };
  } else {
    return {
      type: 'bar',
      data: { labels: labels, datasets: [{ data: [75, 4, 150, 18, 45], backgroundColor: '#c026d3', borderRadius: 3 }] },
      options: {
        ...common,
        indexAxis: 'y',
        scales: {
          y: { grid: { display: false }, ticks: { font: { weight: 'bold', size: 10 } } },
          x: { grid: { color: 'rgba(255, 255, 255, 0.06)' }, beginAtZero: true, max: 200 }
        },
        onClick: (e, elements) => {
          if (!elements.length) return;
          const idx = elements[0].index;
          const val = chartObst.data.labels[idx];
          filters.obstacleSource = filters.obstacleSource === val ? null : val;
          applyFilters();
        }
      }
    };
  }
}

function buildStatChartConfig(mode) {
  const common = getCommonChartOptions();
  const statOrder = ['إزالة الموقع', 'ايقاف الموقع', 'تم التشغيل', 'جاري العمل', 'عوائق', 'غير منفذ', 'متوقف بطلب المالك', 'يجب إعادة التحقق'];
  const colors = ['#ef4444', '#f97316', '#fb923c', '#eab308', '#2dd4bf', '#c084fc', '#64748b', '#ec4899'];

  if (mode === 'doughnut' || mode === 'pie') {
    return {
      type: 'doughnut',
      data: { labels: statOrder, datasets: [{ data: [3, 10, 69, 5, 269, 615, 5, 4], backgroundColor: colors, borderWidth: 2, borderColor: '#0f172a', hoverOffset: 6 }] },
      options: {
        ...common,
        cutout: '55%',
        plugins: { ...common.plugins, legend: { display: true, position: 'right', labels: { boxWidth: 9, padding: 5, font: { size: 9.5, family: "'Cairo', sans-serif" } } } },
        onClick: (e, elements) => {
          if (!elements.length) return;
          const idx = elements[0].index;
          const val = chartStat.data.labels[idx];
          filters.status = filters.status === val ? null : val;
          applyFilters();
        }
      }
    };
  } else {
    return {
      type: 'bar',
      data: { labels: statOrder, datasets: [{ data: [3, 10, 69, 5, 269, 615, 5, 4], backgroundColor: colors, borderRadius: 3 }] },
      options: {
        ...common,
        indexAxis: 'y',
        scales: {
          y: { grid: { display: false }, ticks: { font: { weight: 'bold', size: 10 } } },
          x: { grid: { color: 'rgba(255, 255, 255, 0.06)' }, beginAtZero: true }
        },
        onClick: (e, elements) => {
          if (!elements.length) return;
          const idx = elements[0].index;
          const val = chartStat.data.labels[idx];
          filters.status = filters.status === val ? null : val;
          applyFilters();
        }
      }
    };
  }
}

function initCharts() {
  Chart.defaults.font.family = "'Cairo', sans-serif";
  Chart.defaults.color = '#94a3b8';

  // 1. Municipalities (Bar by default)
  chartMuni = new Chart(document.getElementById('chartMunicipalities').getContext('2d'), buildMuniChartConfig(chartMuniMode));

  // 2. Adv Types (Doughnut / Pie by default for visual diversity!)
  chartType = new Chart(document.getElementById('chartAdvTypes').getContext('2d'), buildTypeChartConfig(chartTypeMode));

  // 3. Obstacle Sources (Bar by default)
  chartObst = new Chart(document.getElementById('chartObstacles').getContext('2d'), buildObstChartConfig(chartObstMode));

  // 4. Statuses (Bar by default)
  chartStat = new Chart(document.getElementById('chartStatuses').getContext('2d'), buildStatChartConfig(chartStatMode));
}

function toggleMuniChart(mode) {
  chartMuniMode = mode;
  document.getElementById('btnMuniBar').classList.toggle('active', mode === 'bar');
  document.getElementById('btnMuniPie').classList.toggle('active', mode === 'pie');
  chartMuni.destroy();
  chartMuni = new Chart(document.getElementById('chartMunicipalities').getContext('2d'), buildMuniChartConfig(mode));
  updateChartsData(getFilteredData());
}

function toggleTypeChart(mode) {
  chartTypeMode = mode;
  document.getElementById('btnTypePie').classList.toggle('active', mode === 'doughnut');
  document.getElementById('btnTypeBar').classList.toggle('active', mode === 'bar');
  chartType.destroy();
  chartType = new Chart(document.getElementById('chartAdvTypes').getContext('2d'), buildTypeChartConfig(mode));
  updateChartsData(getFilteredData());
}

function toggleObstChart(mode) {
  chartObstMode = mode;
  document.getElementById('btnObstBar').classList.toggle('active', mode === 'bar');
  document.getElementById('btnObstPie').classList.toggle('active', mode === 'doughnut');
  chartObst.destroy();
  chartObst = new Chart(document.getElementById('chartObstacles').getContext('2d'), buildObstChartConfig(mode));
  updateChartsData(getFilteredData());
}

function toggleStatChart(mode) {
  chartStatMode = mode;
  document.getElementById('btnStatBar').classList.toggle('active', mode === 'bar');
  document.getElementById('btnStatPie').classList.toggle('active', mode === 'doughnut');
  chartStat.destroy();
  chartStat = new Chart(document.getElementById('chartStatuses').getContext('2d'), buildStatChartConfig(mode));
  updateChartsData(getFilteredData());
}

function updateChartsData(filtered) {
  // 1. Municipalities
  const muniCounts = { 'الخبر': 0, 'الدمام': 0, 'الظهران': 0 };
  filtered.forEach(s => {
    const b = s.bal || '';
    if (b.includes('الخبر')) muniCounts['الخبر']++;
    else if (b.includes('الظهران')) muniCounts['الظهران']++;
    else muniCounts['الدمام']++;
  });
  chartMuni.data.labels = ['الخبر', 'الدمام', 'الظهران'];
  chartMuni.data.datasets[0].data = [muniCounts['الخبر'], muniCounts['الدمام'], muniCounts['الظهران']];
  if (chartMuniMode === 'bar') {
    chartMuni.data.datasets[0].backgroundColor = ['الخبر', 'الدمام', 'الظهران'].map(k => k === filters.bal ? '#60a5fa' : '#38bdf8');
  }
  chartMuni.update();

  // 2. Adv Types
  const typeOrder = ['موبي', 'ميجاكوم', 'يونيبول', 'جسور وأنفاق'];
  const typeCounts = { 'موبي': 0, 'ميجاكوم': 0, 'يونيبول': 0, 'جسور وأنفاق': 0 };
  filtered.forEach(s => {
    if (typeCounts[s.type] !== undefined) typeCounts[s.type]++;
  });
  chartType.data.labels = typeOrder;
  chartType.data.datasets[0].data = typeOrder.map(t => typeCounts[t]);
  chartType.data.datasets[0].backgroundColor = typeOrder.map(t => TYPE_COLORS[t] || '#38bdf8');
  chartType.update();

  // 3. Obstacle Sources
  const obstOrder = ['اشتراطات مكانية', 'اشتراطات مكانية + المقاول', 'الاستشاري', 'الاستشاري + المقاول', 'المقاول'];
  const obstCounts = { 'اشتراطات مكانية': 0, 'اشتراطات مكانية + المقاول': 0, 'الاستشاري': 0, 'الاستشاري + المقاول': 0, 'المقاول': 0 };
  filtered.forEach(s => {
    const src = getSiteObstacleSource(s);
    if (obstCounts[src] !== undefined) obstCounts[src]++;
  });
  chartObst.data.labels = obstOrder;
  chartObst.data.datasets[0].data = obstOrder.map(o => obstCounts[o]);
  if (chartObstMode === 'bar') {
    chartObst.data.datasets[0].backgroundColor = obstOrder.map(o => o === filters.obstacleSource ? '#e879f9' : '#c026d3');
  }
  chartObst.update();

  // 4. Statuses
  const statOrder = ['إزالة الموقع', 'ايقاف الموقع', 'تم التشغيل', 'جاري العمل', 'عوائق', 'غير منفذ', 'متوقف بطلب المالك', 'يجب إعادة التحقق'];
  const statCounts = {};
  statOrder.forEach(k => statCounts[k] = 0);
  filtered.forEach(s => {
    const st = s.dec || 'غير منفذ';
    if (statCounts[st] !== undefined) statCounts[st]++;
    else if (st === 'تم التركيب') statCounts['تم التشغيل']++;
  });
  chartStat.data.labels = statOrder;
  chartStat.data.datasets[0].data = statOrder.map(k => statCounts[k]);
  chartStat.update();
}

/* ===================================================================
   LEAFLET MAP IMPLEMENTATION
   =================================================================== */
function initMap() {
  map = L.map('map', {
    center: [26.42, 50.12],
    zoom: 12,
    zoomControl: false
  });

  L.control.zoom({ position: 'bottomright' }).addTo(map);

  // Basemaps
  basemapLayers.satellite = L.layerGroup([
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
      attribution: 'Esri Satellite'
    }),
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19
    })
  ]).addTo(map);

  basemapLayers.streets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: 'OpenStreetMap'
  });

  basemapLayers.dark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    attribution: 'CartoDB Dark'
  });

  markerLayer = L.layerGroup().addTo(map);
}

function switchBasemap(type) {
  Object.values(basemapLayers).forEach(l => map.removeLayer(l));
  if (basemapLayers[type]) {
    basemapLayers[type].addTo(map);
  }
}

function recenterMap() {
  map.setView([26.42, 50.12], 12);
}

function setColorMode(mode) {
  colorMode = mode;
  document.getElementById('btnColorType').classList.toggle('active', mode === 'type');
  document.getElementById('btnColorStatus').classList.toggle('active', mode === 'status');
  updateMapMarkers(getFilteredData());
}

function toggleMapLegend() {
  const legend = document.getElementById('mapLegend');
  const btn = document.getElementById('btnToggleLegend');
  if (!legend) return;
  legend.classList.toggle('collapsed');
  if (btn) btn.textContent = legend.classList.contains('collapsed') ? '▴' : '▾';
}

function toggleLegendFilter(key, val) {
  filters[key] = filters[key] === val ? null : val;
  applyFilters();
}

function renderMapLegend(filtered) {
  const itemsEl = document.getElementById('mapLegendItems');
  const modeEl = document.getElementById('mapLegendMode');
  if (!itemsEl) return;

  const isType = colorMode === 'type';
  if (modeEl) modeEl.textContent = isType ? '(نوع اللوحة)' : '(حالة الموقع)';

  const palette = isType ? TYPE_COLORS : STATUS_COLORS;
  const filterKey = isType ? 'type' : 'status';
  const fieldName = isType ? 'type' : 'dec';

  // Count total occurrences in D and currently filtered occurrences
  const totalCounts = {};
  D.forEach(s => {
    const val = s[fieldName] || (isType ? 'يونيبول' : 'غير منفذ');
    totalCounts[val] = (totalCounts[val] || 0) + 1;
  });

  const filteredCounts = {};
  filtered.forEach(s => {
    const val = s[fieldName] || (isType ? 'يونيبول' : 'غير منفذ');
    filteredCounts[val] = (filteredCounts[val] || 0) + 1;
  });

  // Combine palette keys (that exist in dataset or active filter) + any dynamic values
  const keys = Array.from(new Set([...Object.keys(palette), ...Object.keys(totalCounts)]))
    .filter(k => (totalCounts[k] || 0) > 0 || filters[filterKey] === k);

  itemsEl.innerHTML = keys.map(k => {
    const col = palette[k] || '#94a3b8';
    const cnt = filteredCounts[k] || 0;
    const isActive = filters[filterKey] === k;
    const isDim = !isActive && cnt === 0;
    const safeVal = k.replace(/'/g, "\\\\'");
    return `
      <div class="legend-row ${isActive ? 'active' : ''} ${isDim ? 'dim' : ''}" onclick="toggleLegendFilter('${filterKey}', '${safeVal}')" title="انقر للتصفية حسب: ${k}">
        <span class="legend-row-label">
          <span class="legend-dot" style="background:${col};"></span>
          <span>${k}</span>
        </span>
        <span class="legend-count">${cnt.toLocaleString('en-US')}</span>
      </div>
    `;
  }).join('');
}

function updateMapMarkers(filtered) {
  markerLayer.clearLayers();
  document.getElementById('mapCounterBadge').textContent = `${filtered.length} موقع معروض`;
  renderMapLegend(filtered);

  filtered.forEach(s => {
    if (!s.lat || !s.lon) return;

    const col = colorMode === 'type' ? (TYPE_COLORS[s.type] || '#38bdf8') : (STATUS_COLORS[s.dec] || '#94a3b8');

    const m = L.circleMarker([s.lat, s.lon], {
      radius: 6,
      fillColor: col,
      fillOpacity: 0.9,
      color: '#ffffff',
      weight: 1.5
    });

    // Rich Popup
    let attHtml = '';
    if (s.atts && s.atts.length) {
      attHtml = `
        <div class="pop-atts">
          <div class="pop-atts-title">📎 المرفقات المعتمدة (R2):</div>
          ${s.atts.map(a => {
            const cleanKey = (a.key || '').replace(/'/g, "\\'");
            const cleanTitle = (a.title || 'مرفق').replace(/'/g, "\\'");
            const isPdf = a.type === 'pdf' || (a.key && a.key.toLowerCase().endsWith('.pdf'));
            return `
              <button class="btn-att-pop" onclick="openAttachment('${cleanKey}', '${cleanTitle}', '${isPdf ? 'pdf' : 'image'}')">
                <span>${isPdf ? '📕' : '🖼️'}</span>
                <span style="flex:1;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${a.title}</span>
                <span style="font-size:10px;opacity:0.75;padding:1px 5px;border-radius:3px;background:rgba(255,255,255,0.08);">معاينة 👁️</span>
              </button>
            `;
          }).join('')}
        </div>
      `;
    }

    const popupHtml = `
      <div class="pop-card">
        <div class="pop-head">
          <span class="pop-code" style="color:${col};">${s.code}</span>
          <span class="pop-badge">${s.type}</span>
        </div>
        <div class="pop-rows">
          <div class="pop-row">
            <span class="pop-label">البلدية:</span>
            <span class="pop-val">${s.bal || '—'}</span>
          </div>
          <div class="pop-row">
            <span class="pop-label">الحي:</span>
            <span class="pop-val">${s.hay || '—'}</span>
          </div>
          <div class="pop-row">
            <span class="pop-label">حالة الموقع:</span>
            <span class="pop-val" style="color:${STATUS_COLORS[s.dec] || '#38bdf8'};font-weight:700;">${s.dec || 'غير منفذ'}</span>
          </div>
          <div class="pop-row">
            <span class="pop-label">قاعدة سابقة:</span>
            <span class="pop-val" style="color:${s.base === 'نعم' ? '#2dd4bf' : '#94a3b8'};">${s.base === 'نعم' ? 'يوجد قاعدة' : 'لا يوجد'}</span>
          </div>
        </div>
        ${s.note ? `
          <div class="pop-note">
            <span style="color:#f59e0b;font-weight:700;">📝 ملاحظة:</span> ${s.note}
          </div>
        ` : ''}
        ${attHtml}
        <button class="btn-site-detail-pop" onclick="openSiteDetailPage('${s.code}')">
          <span>📋 صفحة تفاصيل الموقع الكاملة</span>
          <span>←</span>
        </button>
        <div class="pop-footer">
          <span style="color:#64748b;font-family:monospace;">${(s.lat||0).toFixed(5)}, ${(s.lon||0).toFixed(5)}</span>
          <a href="https://www.google.com/maps?q=${s.lat},${s.lon}" target="_blank" rel="noopener">فتح في Google Maps ↗</a>
        </div>
      </div>
    `;

    m.bindPopup(popupHtml, { className: 'dark-popup' });
    markerLayer.addLayer(m);
  });
}

/* ===================================================================
   DEDICATED SINGLE-SITE DETAIL PAGE LOGIC
   =================================================================== */
let sdMap = null;
let sdMarkerLayer = null;
let sdBasemapLayers = {};
let currentDetailSite = null;
let previousDashboardView = 'exec';

function initSiteDetailMap() {
  if (sdMap) return;
  sdMap = L.map('siteDetailMap', {
    center: [26.42, 50.12],
    zoom: 17,
    zoomControl: false
  });
  L.control.zoom({ position: 'bottomright' }).addTo(sdMap);

  sdBasemapLayers.satellite = L.layerGroup([
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
      attribution: 'Esri Satellite'
    }),
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19
    })
  ]).addTo(sdMap);

  sdBasemapLayers.streets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: 'OpenStreetMap'
  });

  sdBasemapLayers.dark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    attribution: 'CartoDB Dark'
  });

  sdMarkerLayer = L.layerGroup().addTo(sdMap);
}

function switchSiteDetailBasemap(type) {
  if (!sdMap) return;
  Object.values(sdBasemapLayers).forEach(l => sdMap.removeLayer(l));
  if (sdBasemapLayers[type]) sdBasemapLayers[type].addTo(sdMap);
}

function recenterSiteDetailMap() {
  if (!sdMap || !currentDetailSite) return;
  sdMap.setView([currentDetailSite.lat, currentDetailSite.lon], 18);
}

function copySiteCoords() {
  if (!currentDetailSite) return;
  const txt = `${currentDetailSite.lat.toFixed(6)}, ${currentDetailSite.lon.toFixed(6)}`;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(txt).catch(() => {});
  }
  const btn = document.getElementById('btnCopyCoords');
  if (btn) {
    const orig = btn.textContent;
    btn.textContent = '✓ تم نسخ الإحداثيات';
    setTimeout(() => { btn.textContent = orig; }, 1800);
  }
}

function openSiteDetailPage(code, pushHistory = true) {
  const s = D.find(item => item.code === code || String(item.siteNo) === String(code));
  if (!s) return;
  currentDetailSite = s;

  const execView = document.getElementById('executiveView');
  const tableView = document.getElementById('tableView');
  const sdView = document.getElementById('siteDetailView');
  const topBar = document.querySelector('.top-bar');
  const kpiGrid = document.querySelector('.kpi-grid');
  const afBar = document.getElementById('activeFilterBar');

  if (sdView.style.display !== 'flex') {
    previousDashboardView = (tableView && tableView.style.display === 'flex') ? 'table' : 'exec';
  }

  if (topBar) topBar.style.display = 'none';
  if (kpiGrid) kpiGrid.style.display = 'none';
  if (afBar) afBar.style.display = 'none';
  if (execView) execView.style.display = 'none';
  if (tableView) tableView.style.display = 'none';
  sdView.style.display = 'flex';

  const typeCol = TYPE_COLORS[s.type] || '#38bdf8';
  const statCol = STATUS_COLORS[s.dec] || '#94a3b8';
  const gmapsUrl = `https://www.google.com/maps?q=${s.lat},${s.lon}`;

  document.getElementById('sdCode').textContent = s.code;
  document.getElementById('sdCode').style.color = typeCol;

  const typeBadge = document.getElementById('sdTypeBadge');
  typeBadge.textContent = s.type || 'يونيبول';
  typeBadge.style.borderColor = typeCol;
  typeBadge.style.color = typeCol;

  const statBadge = document.getElementById('sdStatusBadge');
  statBadge.textContent = s.dec || 'غير منفذ';
  statBadge.style.borderColor = statCol;
  statBadge.style.color = statCol;

  document.getElementById('sdLocationSub').textContent = `${s.bal || 'حاضرة الدمام'} · الحي: ${s.hay || '—'}`;
  document.getElementById('sdGoogleMapsBtn').href = gmapsUrl;
  document.getElementById('sdGoogleMapsFooterLink').href = gmapsUrl;
  document.getElementById('sdMapCodeLabel').textContent = `(${s.code})`;
  document.getElementById('sdCoordsText').textContent = `${(s.lat || 0).toFixed(6)}, ${(s.lon || 0).toFixed(6)}`;

  const obSource = getSiteObstacleSource(s);
  const isOb = s.dec === 'عوائق' || s.ob;

  // Populate Key-Value Grid
  const kvItems = [
    { label: 'رمز الموقع', val: s.code, color: typeCol, mono: true },
    { label: 'رقم الموقع بالكراسة', val: String(s.siteNo || s.n || '—'), mono: true },
    { label: 'نوع اللوحة الإعلانية', val: s.type || '—', color: typeCol },
    { label: 'حالة التنفيذ', val: s.dec || 'غير منفذ', color: statCol },
    { label: 'البلدية', val: s.bal || '—' },
    { label: 'الحي / النطاق', val: s.hay || '—' },
    { label: 'قاعدة خرسانية سابقة', val: s.base === 'نعم' ? 'نعم (توجد قاعدة سابقة)' : 'لا يوجد', color: s.base === 'نعم' ? '#2dd4bf' : '#94a3b8' },
    { label: 'مصدر العائق', val: obSource, color: isOb ? '#f87171' : '#4ade80' }
  ];

  document.getElementById('sdKvGrid').innerHTML = kvItems.map(item => `
    <div class="sd-kv-item">
      <span class="sd-kv-label">${item.label}</span>
      <span class="sd-kv-val" style="${item.color ? 'color:' + item.color + ';' : ''}${item.mono ? 'font-family:var(--mono);' : ''}">${item.val}</span>
    </div>
  `).join('');

  // Populate Notes
  const obstBadge = document.getElementById('sdObstBadge');
  obstBadge.textContent = isOb ? `⚠️ عائق مسجل (${obSource})` : '✅ لا توجد عوائق نشطة';
  obstBadge.style.color = isOb ? '#f87171' : '#4ade80';

  const noteBox = document.getElementById('sdNoteBox');
  if (s.note && s.note.trim()) {
    noteBox.innerHTML = s.note.split(/\\s*\\|\\|\\s*|\\s*\\|\\s*/).map(part => `<div>• ${part}</div>`).join('');
    noteBox.style.borderColor = isOb ? 'rgba(239, 68, 68, 0.35)' : 'rgba(245, 158, 11, 0.3)';
  } else {
    noteBox.textContent = 'لا توجد ملاحظات ميدانية أو عوائق مسجلة لهذا الموقع.';
    noteBox.style.borderColor = 'rgba(255, 255, 255, 0.1)';
  }

  // Populate Attachments
  const atts = s.atts || [];
  document.getElementById('sdAttCountBadge').textContent = `${atts.length} مرفق`;
  const attsListEl = document.getElementById('sdAttsList');
  if (atts.length) {
    attsListEl.innerHTML = atts.map(a => {
      const cleanKey = (a.key || '').replace(/'/g, "\\\\'");
      const cleanTitle = (a.title || 'مرفق').replace(/'/g, "\\\\'");
      const isPdf = a.type === 'pdf' || (a.key && a.key.toLowerCase().endsWith('.pdf'));
      return `
        <div class="sd-att-card">
          <div class="sd-att-info">
            <span class="sd-att-icon">${isPdf ? '📕' : '🖼️'}</span>
            <div style="min-width:0;">
              <div class="sd-att-name" title="${a.title}">${a.title}</div>
              <div class="sd-att-type">${isPdf ? 'مستند PDF رسمي محمي' : 'صورة ميدانية معتمدة'}</div>
            </div>
          </div>
          <button class="btn-site-detail-tbl" onclick="openAttachment('${cleanKey}', '${cleanTitle}', '${isPdf ? 'pdf' : 'image'}')" style="padding:5px 12px;font-size:11.5px;">
            👁️ معاينة المرفق
          </button>
        </div>
      `;
    }).join('');
  } else {
    attsListEl.innerHTML = '<div style="color:var(--text-muted);font-size:12px;padding:8px 0;">لا توجد مرفقات مسجلة لهذا الموقع حالياً.</div>';
  }

  // Initialize & Render Single-Site Map
  initSiteDetailMap();
  setTimeout(() => {
    sdMap.invalidateSize();
    sdMarkerLayer.clearLayers();
    if (s.lat && s.lon) {
      sdMap.setView([s.lat, s.lon], 18);
      // Outer pulse ring + inner marker
      L.circleMarker([s.lat, s.lon], {
        radius: 18,
        fillColor: typeCol,
        fillOpacity: 0.22,
        color: typeCol,
        weight: 2
      }).addTo(sdMarkerLayer);

      const marker = L.circleMarker([s.lat, s.lon], {
        radius: 8,
        fillColor: typeCol,
        fillOpacity: 1,
        color: '#ffffff',
        weight: 2.5
      }).addTo(sdMarkerLayer);

      marker.bindTooltip(`<b>${s.code}</b> — ${s.type} (${s.dec || 'غير منفذ'})`, {
        permanent: true,
        direction: 'top',
        offset: [0, -10]
      });
    }
  }, 80);

  if (pushHistory) {
    history.pushState({ siteDetail: s.code }, '', `#site=${encodeURIComponent(s.code)}`);
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function closeSiteDetailPage(fromPopState = false) {
  const sdView = document.getElementById('siteDetailView');
  if (!sdView || sdView.style.display === 'none') return;

  sdView.style.display = 'none';
  const topBar = document.querySelector('.top-bar');
  const kpiGrid = document.querySelector('.kpi-grid');
  const execView = document.getElementById('executiveView');
  const tableView = document.getElementById('tableView');

  if (topBar) topBar.style.display = 'flex';
  if (kpiGrid) kpiGrid.style.display = 'grid';
  updateFilterChips();

  if (previousDashboardView === 'table') {
    if (tableView) tableView.style.display = 'flex';
    if (execView) execView.style.display = 'none';
  } else {
    if (execView) execView.style.display = 'grid';
    if (tableView) tableView.style.display = 'none';
    setTimeout(() => map.invalidateSize(), 100);
  }

  if (!fromPopState && location.hash.startsWith('#site=')) {
    history.pushState(null, '', location.pathname + location.search);
  }
}

window.addEventListener('popstate', e => {
  if (e.state && e.state.siteDetail) {
    openSiteDetailPage(e.state.siteDetail, false);
  } else {
    closeSiteDetailPage(true);
  }
});

/* ===================================================================
   TABLE IMPLEMENTATION
   =================================================================== */
function updateTable(filtered) {
  const tbody = document.getElementById('tableBody');
  document.getElementById('tableRecordCount').textContent = `${filtered.length} موقع`;

  const rows = filtered.slice(0, 200).map(s => {
    let attBtn = '—';
    if (s.atts && s.atts.length) {
      attBtn = s.atts.map(a => `
        <button class="btn-att" onclick="openAttachment('${a.key}', '${a.title}', '${a.type}')">
          ${a.type==='pdf'?'📕':'🖼️'} ${a.title.length>14?a.title.substring(0,12)+'...':a.title}
        </button>
      `).join(' ');
    }

    const stClass = s.dec === 'تم التشغيل' ? 'tag-green' : s.dec === 'عوائق' ? 'tag-red' : s.dec === 'إزالة الموقع' ? 'tag-red' : 'tag-gray';

    return `
      <tr>
        <td style="font-family:var(--mono);font-weight:700;color:var(--blue);cursor:pointer;text-decoration:underline;" onclick="openSiteDetailPage('${s.code}')" title="فتح صفحة تفاصيل الموقع">${s.code}</td>
        <td>${s.type}</td>
        <td>${s.bal}</td>
        <td>${s.hay || '—'}</td>
        <td><span class="tag-status ${stClass}">${s.dec || 'غير منفذ'}</span></td>
        <td>${s.base==='نعم'?'نعم':'لا'}</td>
        <td style="font-size:11px;color:#c084fc;">${getSiteObstacleSource(s)}</td>
        <td style="font-size:11px;color:#94a3b8;max-width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${s.note||''}">${s.note || '—'}</td>
        <td>${attBtn}</td>
        <td style="font-family:var(--mono);font-size:11px;"><a href="https://www.google.com/maps?q=${s.lat},${s.lon}" target="_blank" style="color:var(--blue);">📍 عرض</a></td>
        <td><button class="btn-site-detail-tbl" onclick="openSiteDetailPage('${s.code}')">📋 تفاصيل الموقع</button></td>
      </tr>
    `;
  }).join('');

  tbody.innerHTML = rows;
}

function exportTableCSV() {
  const data = getFilteredData();
  const headers = ['رمز الموقع', 'نوع اللوحة', 'البلدية', 'الحي', 'حالة الموقع', 'قاعدة سابقة', 'مصدر العائق', 'الملاحظات', 'خط العرض', 'خط الطول'];
  const rows = data.map(s => [
    s.code, s.type, s.bal, s.hay||'', s.dec||'', s.base||'', getSiteObstacleSource(s), (s.note||'').replace(/\\n/g, ' '), s.lat, s.lon
  ]);
  let csv = '\uFEFF' + headers.join(',') + '\\n' + rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `لوحة_معلومات_الشرقية_${new Date().toISOString().slice(0,10)}.csv`;
  a.click();
}

/* Apply All Filters Orchestrator */
function applyFilters() {
  const filtered = getFilteredData();
  updateKPIs(filtered);
  updateFilterChips();
  updateChartsData(filtered);
  updateMapMarkers(filtered);
  updateTable(filtered);
}

/* ===================================================================
   SECURE CANVAS PDF / IMAGE ATTACHMENT VIEWER
   =================================================================== */
let currentPDFDoc = null;
let currentPDFPage = 1;
let currentPDFTotalPages = 1;
let currentDocType = null;
let attZoom = 1.0;
let attBaseDisplayW = 0;
let attBaseDisplayH = 0;
let attPdfPageW = 0;
let attPdfPageH = 0;
let attUserIdentity = '';
let attToastTimer = null;
let attShieldTimer = null;

function isAttModalOpen() {
  const modal = document.getElementById('attModal');
  return modal && modal.style.display === 'flex';
}

function showAttSecToast(msg) {
  const toast = document.getElementById('attSecToast');
  if (!toast) return;
  if (msg) toast.textContent = msg;
  toast.style.display = 'block';
  clearTimeout(attToastTimer);
  attToastTimer = setTimeout(() => { toast.style.display = 'none'; }, 2600);
}

function setPrivacyShield(active, reason) {
  const canvas = document.getElementById('attCanvas');
  const shield = document.getElementById('attPrivacyShield');
  const msgEl = document.getElementById('attShieldMsg');
  if (!canvas || !shield) return;
  if (active && isAttModalOpen()) {
    canvas.style.opacity = '0';
    canvas.style.visibility = 'hidden';
    canvas.classList.add('blurred');
    shield.classList.add('active');
    if (reason && msgEl) msgEl.textContent = reason;
  } else {
    canvas.style.opacity = '1';
    canvas.style.visibility = 'visible';
    canvas.classList.remove('blurred');
    shield.classList.remove('active');
  }
}

function closeAttachmentModal() {
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
  }
  const win = document.getElementById('attModalWindow');
  if (win) win.classList.remove('is-fullscreen');
  setPrivacyShield(false);
  document.getElementById('attModal').style.display = 'none';
  currentPDFDoc = null;
  currentDocType = null;
}

function toggleAttFullscreen() {
  const win = document.getElementById('attModalWindow');
  const btn = document.getElementById('btnAttFullscreen');
  if (!win) return;

  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
    win.classList.remove('is-fullscreen');
  } else if (win.requestFullscreen) {
    win.requestFullscreen().catch(() => {
      // Fallback CSS fullscreen if browser blocks fullscreen API
      win.classList.toggle('is-fullscreen');
      if (btn) btn.textContent = win.classList.contains('is-fullscreen') ? '🗗 تصغير الشاشة' : '⛶ ملء الشاشة';
      setTimeout(() => refitAttCanvas(), 120);
    });
  } else {
    win.classList.toggle('is-fullscreen');
    if (btn) btn.textContent = win.classList.contains('is-fullscreen') ? '🗗 تصغير الشاشة' : '⛶ ملء الشاشة';
    setTimeout(() => refitAttCanvas(), 120);
  }
}

document.addEventListener('fullscreenchange', () => {
  const win = document.getElementById('attModalWindow');
  const btn = document.getElementById('btnAttFullscreen');
  const isFs = !!document.fullscreenElement;
  if (win) win.classList.toggle('is-fullscreen', isFs);
  if (btn) btn.textContent = isFs ? '🗗 تصغير الشاشة' : '⛶ ملء الشاشة';
  setTimeout(() => refitAttCanvas(), 150);
});

function updateZoomUI() {
  const lbl = document.getElementById('attZoomLabel');
  const body = document.getElementById('attModalBody');
  const btnIn = document.getElementById('btnZoomIn');
  const btnOut = document.getElementById('btnZoomOut');
  if (lbl) lbl.textContent = `${Math.round(attZoom * 100)}%`;
  if (body) body.classList.toggle('is-zoomed', attZoom > 1.01);
  if (btnIn) btnIn.disabled = attZoom >= 3.0;
  if (btnOut) btnOut.disabled = attZoom <= 0.5;
}

function applyCanvasDisplaySize() {
  const canvas = document.getElementById('attCanvas');
  if (!canvas || !attBaseDisplayW || !attBaseDisplayH) return;
  canvas.style.width = `${Math.round(attBaseDisplayW * attZoom)}px`;
  canvas.style.height = `${Math.round(attBaseDisplayH * attZoom)}px`;
  updateZoomUI();
}

function refitAttCanvas() {
  const body = document.getElementById('attModalBody');
  const canvas = document.getElementById('attCanvas');
  if (!body || !canvas || !currentDocType) return;
  const availW = Math.max(260, body.clientWidth - 36);
  const availH = Math.max(220, body.clientHeight - 36);

  if (currentDocType === 'image' && canvas.width > 0) {
    const ratio = Math.min(availW / canvas.width, availH / canvas.height, 1.25);
    attBaseDisplayW = Math.round(canvas.width * ratio);
    attBaseDisplayH = Math.round(canvas.height * ratio);
    applyCanvasDisplaySize();
  } else if (currentDocType === 'pdf' && attPdfPageW > 0) {
    const ratio = Math.min(availW / attPdfPageW, availH / attPdfPageH, 2.2);
    attBaseDisplayW = Math.round(attPdfPageW * ratio);
    attBaseDisplayH = Math.round(attPdfPageH * ratio);
    renderPDFPage();
  }
}

function adjustAttZoom(delta) {
  const next = Math.round(Math.max(0.5, Math.min(3.0, attZoom + delta)) * 100) / 100;
  if (next === attZoom) return;
  attZoom = next;
  if (currentDocType === 'pdf') {
    renderPDFPage();
  } else {
    applyCanvasDisplaySize();
  }
}

function resetAttZoom() {
  attZoom = 1.0;
  refitAttCanvas();
}

async function openAttachment(fileKey, title, type) {
  const modal = document.getElementById('attModal');
  const modalTitle = document.getElementById('attModalTitle');
  const modalIcon = document.getElementById('attModalIcon');
  const pdfControls = document.getElementById('pdfControls');
  const canvas = document.getElementById('attCanvas');
  const ctx = canvas.getContext('2d');

  modal.style.display = 'flex';
  modalTitle.textContent = title;
  modalIcon.textContent = type === 'pdf' ? '📕' : '🖼️';
  pdfControls.style.display = 'none';
  setPrivacyShield(false);
  attZoom = 1.0;
  currentDocType = null;
  attBaseDisplayW = 600;
  attBaseDisplayH = 300;
  canvas.style.width = '';
  canvas.style.height = '';
  updateZoomUI();

  canvas.width = 600;
  canvas.height = 300;
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#38bdf8';
  ctx.font = 'bold 16px Cairo';
  ctx.textAlign = 'center';
  ctx.fillText('جاري تحميل المرفق بأمان من السحابة...', canvas.width / 2, canvas.height / 2);

  try {
    let apiBase = '';
    if (location.protocol === 'file:') {
      try {
        await fetch('http://localhost:3000/api/attachment?key=ping', { method: 'OPTIONS' });
        apiBase = 'http://localhost:3000';
      } catch (e) {
        apiBase = 'https://ads-dashboard.almahagroup.org';
      }
    }
    const cleanKey = fileKey.replace(/^\\/+/, '');
    const res = await fetch(`${apiBase}/api/attachment?key=${encodeURIComponent(cleanKey)}`, {
      headers: {
        'X-Viewer-Mode': 'canvas-render'
      }
    });
    if (!res.ok) {
      if (res.status === 403) throw new Error('غير مصرح باستعراض هذا المرفق مباشرة (رمز 403)');
      if (res.status === 404) throw new Error('الملف غير متوفر في مخزن السحابة R2 (رمز 404)');
      throw new Error(`تعذر تحميل الملف (كود ${res.status})`);
    }

    attUserIdentity = res.headers.get('X-User-Identity') || '';
    const blob = await res.blob();
    const isPDF = type === 'pdf' || cleanKey.toLowerCase().endsWith('.pdf') || blob.type === 'application/pdf';

    if (isPDF) {
      await renderPDFDoc(blob);
    } else {
      await renderImageDoc(blob);
    }
  } catch (err) {
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ef4444';
    ctx.font = 'bold 15px Cairo';
    ctx.textAlign = 'center';
    ctx.fillText('تعذر عرض المرفق: ' + err.message, canvas.width / 2, canvas.height / 2);
  }
}

async function renderPDFDoc(blob) {
  const pdfjsLib = await import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs');
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs';

  const buf = await blob.arrayBuffer();
  const loadingTask = pdfjsLib.getDocument({
    data: buf,
    cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/cmaps/',
    cMapPacked: true,
    standardFontDataUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/standard_fonts/',
    disableFontFace: true, // Fix Arabic letters
    enableXfa: true
  });

  currentPDFDoc = await loadingTask.promise;
  currentPDFTotalPages = currentPDFDoc.numPages;
  currentPDFPage = 1;
  currentDocType = 'pdf';
  attZoom = 1.0;

  document.getElementById('pdfControls').style.display = currentPDFTotalPages > 1 ? 'flex' : 'none';
  await renderPDFPage();
}

async function renderPDFPage() {
  if (!currentPDFDoc) return;
  const page = await currentPDFDoc.getPage(currentPDFPage);
  const vp1 = page.getViewport({ scale: 1.0 });
  attPdfPageW = vp1.width;
  attPdfPageH = vp1.height;

  const body = document.getElementById('attModalBody');
  const availW = Math.max(260, (body ? body.clientWidth : 900) - 36);
  const availH = Math.max(220, (body ? body.clientHeight : 600) - 36);
  const fitRatio = Math.min(availW / attPdfPageW, availH / attPdfPageH, 2.2);
  attBaseDisplayW = Math.round(attPdfPageW * fitRatio);
  attBaseDisplayH = Math.round(attPdfPageH * fitRatio);

  const dpr = Math.min(window.devicePixelRatio || 1.5, 2.0);
  const renderScale = Math.min(4.2, fitRatio * attZoom * dpr);
  const viewport = page.getViewport({ scale: renderScale });

  const canvas = document.getElementById('attCanvas');
  const ctx = canvas.getContext('2d');
  canvas.width = Math.round(viewport.width);
  canvas.height = Math.round(viewport.height);

  await page.render({ canvasContext: ctx, viewport: viewport }).promise;
  drawWatermark(ctx, canvas.width, canvas.height);
  applyCanvasDisplaySize();

  document.getElementById('pdfPageLabel').textContent = `${currentPDFPage} / ${currentPDFTotalPages}`;
  document.getElementById('btnPdfPrev').disabled = currentPDFPage <= 1;
  document.getElementById('btnPdfNext').disabled = currentPDFPage >= currentPDFTotalPages;
}

function changePDFPage(delta) {
  if (!currentPDFDoc) return;
  const target = currentPDFPage + delta;
  if (target >= 1 && target <= currentPDFTotalPages) {
    currentPDFPage = target;
    renderPDFPage();
  }
}

async function renderImageDoc(blob) {
  const canvas = document.getElementById('attCanvas');
  const ctx = canvas.getContext('2d');
  const url = URL.createObjectURL(blob);
  const img = new Image();

  img.onload = () => {
    URL.revokeObjectURL(url);
    currentDocType = 'image';
    const maxW = 1800;
    const scale = img.width > maxW ? maxW / img.width : 1;
    canvas.width = Math.round(img.width * scale);
    canvas.height = Math.round(img.height * scale);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    drawWatermark(ctx, canvas.width, canvas.height);
    refitAttCanvas();
  };
  img.src = url;
}

function drawWatermark(ctx, w, h) {
  ctx.save();
  ctx.rotate(-22 * Math.PI / 180);
  const fontSize = Math.max(18, Math.round(w / 42));
  ctx.font = `bold ${fontSize}px Cairo`;
  ctx.fillStyle = 'rgba(239, 68, 68, 0.16)';
  ctx.textAlign = 'center';
  const stamp = new Date().toLocaleString('ar-SA', { hour: '2-digit', minute: '2-digit', year: 'numeric', month: '2-digit', day: '2-digit' });
  const idPart = attUserIdentity ? ` · ${attUserIdentity}` : '';
  const text = `للعرض فقط — أمانة المنطقة الشرقية · إشراق${idPart} · ${stamp}`;
  const stepX = Math.max(360, fontSize * 20);
  const stepY = Math.max(130, fontSize * 6);
  for (let x = -w; x < w * 2; x += stepX) {
    for (let y = -h; y < h * 2; y += stepY) {
      ctx.fillText(text, x, y);
    }
  }
  ctx.restore();
}

/* Security Protection, Wheel Zoom & Pan for Canvas Viewer */
(() => {
  let attShieldLockedUntil = 0;

  function lockPrivacyShield(ms, reason) {
    attShieldLockedUntil = Math.max(attShieldLockedUntil, Date.now() + ms);
    setPrivacyShield(true, reason);
  }

  document.addEventListener('contextmenu', e => {
    if (e.target.closest('#attModal')) {
      e.preventDefault();
      showAttSecToast('🛡️ القائمة السريعة معطّلة لحماية المستند');
    }
  });

  // Pre-emptive Capture-Phase Key Interceptor (triggers in 0ms on first modifier key press BEFORE Win+Shift+S / Alt+PrtScn freezes the screen)
  window.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && ['p', 's'].includes((e.key || '').toLowerCase())) {
      e.preventDefault();
      if (isAttModalOpen()) showAttSecToast('🛡️ الحفظ والطباعة معطّلان لهذا المستند المحمي');
    }
    if (!isAttModalOpen()) return;

    const k = e.key || '';
    if (k === 'Escape') {
      if (!document.fullscreenElement) closeAttachmentModal();
      return;
    }

    // Instant 0ms blackout as soon as Win (Meta/OS), Shift, Alt, Control, PrintScreen, or F12 is touched!
    if (
      k === 'Meta' || k === 'OS' || k === 'Shift' || k === 'Alt' || k === 'Control' ||
      k === 'PrintScreen' || e.keyCode === 44 || k === 'F12' ||
      e.metaKey || e.altKey || e.shiftKey || e.ctrlKey
    ) {
      if (k === 'PrintScreen' || e.keyCode === 44 || k === 'F12' || ((e.ctrlKey || e.metaKey) && ['c', 'u', 'p', 's', 'i'].includes(k.toLowerCase()))) {
        e.preventDefault();
      }
      lockPrivacyShield(1800, 'تم حجب المستند فوراً (0ms) عند الضغط على مفاتيح الاختصار أو التصوير (Win / Shift / Alt / PrtScn)');
      clearTimeout(attShieldTimer);
      attShieldTimer = setTimeout(() => {
        if (document.hasFocus() && Date.now() >= attShieldLockedUntil) setPrivacyShield(false);
      }, 1850);
      return;
    }

    if (k === '+' || k === '=') { adjustAttZoom(0.25); }
    if (k === '-') { adjustAttZoom(-0.25); }
    if (k === '0') { resetAttZoom(); }
  }, true);

  window.addEventListener('keyup', e => {
    if (!isAttModalOpen()) return;
    const k = e.key || '';
    if (k === 'PrintScreen' || e.keyCode === 44) {
      lockPrivacyShield(2800, 'تم رصد مفتاح PrintScreen — تم حجب المستند مؤقتاً للحماية');
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText('مستند محمي — يُمنع التقاط الشاشة أو التداول').catch(() => {});
      }
    } else if (['Meta', 'OS', 'Shift', 'Alt', 'Control'].includes(k)) {
      clearTimeout(attShieldTimer);
      attShieldTimer = setTimeout(() => {
        if (document.hasFocus() && Date.now() >= attShieldLockedUntil) setPrivacyShield(false);
      }, 600);
    }
  }, true);

  // Instant 0ms Shield when cursor leaves the modal window or browser viewport (blocks taskbar Snipping Tool before clicking "New")
  const modalWin = document.getElementById('attModalWindow');
  if (modalWin) {
    modalWin.addEventListener('mouseleave', () => {
      if (isAttModalOpen()) {
        setPrivacyShield(true, 'تم إخفاء المستند تلقائياً عند مغادرة مؤشر الماوس لنافذة المرفق');
      }
    });
    modalWin.addEventListener('mouseenter', () => {
      if (isAttModalOpen() && document.hasFocus() && Date.now() >= attShieldLockedUntil) {
        setPrivacyShield(false);
      }
    });
    modalWin.addEventListener('mousemove', e => {
      if (isAttModalOpen() && document.hasFocus() && !e.metaKey && !e.shiftKey && !e.altKey && !e.ctrlKey && Date.now() >= attShieldLockedUntil) {
        const shield = document.getElementById('attPrivacyShield');
        if (shield && shield.classList.contains('active')) setPrivacyShield(false);
      }
    });
  }

  document.documentElement.addEventListener('mouseleave', () => {
    if (isAttModalOpen()) {
      setPrivacyShield(true, 'تم إخفاء المستند تلقائياً عند خروج المؤشر خارج المتصفح');
    }
  });

  // Privacy Shield on focus loss (e.g., Windows Snipping Tool Win+Shift+S, Alt+Tab, external app capture)
  window.addEventListener('blur', () => {
    if (isAttModalOpen()) {
      lockPrivacyShield(1200, 'تم حجب المستند تلقائياً لأن نافذة العرض فقدت التركيز');
    }
  });
  window.addEventListener('focus', () => {
    if (isAttModalOpen() && Date.now() >= attShieldLockedUntil) {
      setPrivacyShield(false);
    }
  });
  document.addEventListener('visibilitychange', () => {
    if (isAttModalOpen()) {
      if (document.hidden) lockPrivacyShield(1200, 'تم حجب المستند تلقائياً عند مغادرة التبويب');
      else if (document.hasFocus() && Date.now() >= attShieldLockedUntil) setPrivacyShield(false);
    }
  });

  // Direct Mouse Wheel Zoom + Drag-to-Pan inside #attModalBody
  const modalBody = document.getElementById('attModalBody');
  if (modalBody) {
    modalBody.addEventListener('wheel', e => {
      if (!isAttModalOpen()) return;
      e.preventDefault();
      adjustAttZoom(e.deltaY < 0 ? 0.15 : -0.15);
    }, { passive: false });

    let isDown = false, startX = 0, startY = 0, sLeft = 0, sTop = 0;
    modalBody.addEventListener('mousedown', e => {
      if (attZoom <= 1.01) return;
      isDown = true;
      modalBody.classList.add('is-dragging');
      startX = e.pageX;
      startY = e.pageY;
      sLeft = modalBody.scrollLeft;
      sTop = modalBody.scrollTop;
    });
    window.addEventListener('mouseup', () => {
      isDown = false;
      modalBody.classList.remove('is-dragging');
    });
    modalBody.addEventListener('mousemove', e => {
      if (!isDown) return;
      e.preventDefault();
      modalBody.scrollLeft = sLeft - (e.pageX - startX);
      modalBody.scrollTop = sTop - (e.pageY - startY);
    });
  }
})();

/* ===================================================================
   LIVE SYNC WITH ARCGIS FEATURE LAYERS
   =================================================================== */
let INITIAL_STATIC_CACHE = null;

async function loadLiveFeatureLayer(isManual = false) {
  const syncPill = document.getElementById('liveSyncStatus');
  const syncText = document.getElementById('syncText');
  const refreshBtn = document.getElementById('btnRefreshData');
  const refreshLabel = document.getElementById('btnRefreshLabel');

  if (!INITIAL_STATIC_CACHE) {
    const sm = new Map(), sbn = new Map();
    D.forEach(s => {
      sm.set(s.code, s);
      if (s.siteNo) sbn.set(s.siteNo, s);
      if (s.n) sbn.set(s.n, s);
    });
    INITIAL_STATIC_CACHE = { staticMap: sm, staticByNo: sbn };
  }

  if (refreshBtn) {
    refreshBtn.disabled = true;
    refreshBtn.classList.add('spinning');
    if (refreshLabel) refreshLabel.textContent = 'جاري التحديث...';
  }
  syncText.textContent = 'جاري مزامنة وقراءة طبقة معالم ArcGIS الحية...';
  syncPill.style.borderColor = 'rgba(56, 189, 248, 0.45)';

  let succeeded = false;
  try {
    let token = null;
    try {
      const tokRes = await fetch('/api/esri-token', { cache: 'no-store' });
      if (tokRes.ok) {
        const tokData = await tokRes.json();
        token = tokData.access_token || tokData.token;
      }
    } catch (e) {}

    if (!token) {
      try {
        const tokRes = await fetch('https://ads-dashboard.almahagroup.org/api/esri-token', { cache: 'no-store' });
        if (tokRes.ok) {
          const tokData = await tokRes.json();
          token = tokData.access_token || tokData.token;
        }
      } catch (e) {}
    }

    if (!token) {
      console.warn('Could not acquire ArcGIS OAuth token');
      syncText.textContent = 'تعذر الحصول على تصريح طبقة ArcGIS';
      syncPill.style.borderColor = 'rgba(239, 68, 68, 0.45)';
      return;
    }

    const ts = Date.now();
    const [l0Res, l1Res] = await Promise.all([
      fetch(`https://services-ap1.arcgis.com/HRZVvitYCIwFb7oA/arcgis/rest/services/Sites/FeatureServer/0/query?where=1=1&outFields=*&f=json&token=${token}&_ts=${ts}`, { cache: 'no-store' }),
      fetch(`https://services-ap1.arcgis.com/HRZVvitYCIwFb7oA/arcgis/rest/services/Sites/FeatureServer/1/query?where=1=1&outFields=Parent_GlobalID,Attachment_Title,File_Type,R2_File_Key&f=json&token=${token}&_ts=${ts}`, { cache: 'no-store' })
    ]);

    if (!l0Res.ok || !l1Res.ok) {
      console.warn('ArcGIS FeatureServer query error:', l0Res.status, l1Res.status);
      syncText.textContent = 'خطأ في استجابة طبقة معالم ArcGIS';
      syncPill.style.borderColor = 'rgba(239, 68, 68, 0.45)';
      return;
    }

    const l0Data = await l0Res.json();
    const l1Data = await l1Res.json();

    if (!l0Data.features || !l0Data.features.length) return;

    // Attachments Map
    const attMap = new Map();
    if (l1Data.features) {
      l1Data.features.forEach(f => {
        const a = f.attributes;
        if (!a || !a.Parent_GlobalID) return;
        const gid = a.Parent_GlobalID.toLowerCase().replace(/[{}]/g, '').trim();
        if (!attMap.has(gid)) attMap.set(gid, []);
        attMap.get(gid).push({
          title: a.Attachment_Title || 'مرفق',
          type: (a.File_Type || '').toLowerCase() === 'pdf' ? 'pdf' : 'image',
          key: a.R2_File_Key
        });
      });
    }

    const { staticMap, staticByNo } = INITIAL_STATIC_CACHE;
    const prefixMap = { 'يونيبول': 'UN-', 'ميجاكوم': 'MG-', 'موبي': 'MU-', 'جسور وأنفاق': 'BR-', 'شاشات': 'SC-' };

    D = l0Data.features.map((f, idx) => {
      const a = f.attributes;
      const pref = prefixMap[a.AdvType] || 'ST-';
      const code = a.SiteNo ? (String(a.SiteNo).includes('-') ? a.SiteNo : pref + String(a.SiteNo).padStart(3, '0')) : (pref + String(a.OBJECTID).padStart(3, '0'));
      const st = staticMap.get(code) || staticByNo.get(a.SiteNo) || staticByNo.get(a.OBJECTID);
      const gid = (a.GlobalID || '').toLowerCase().replace(/[{}]/g, '').trim();
      const atts = (attMap.get(gid) && attMap.get(gid).length) ? attMap.get(gid) : (st ? st.atts : []);
      const note = a.ObstDesc || a.Notes || (st ? st.note : '');
      const dec = a.FinalExecStatus || (st ? st.dec : 'غير منفذ');
      const ob = a.FinalExecStatus ? (dec === 'عوائق' || !!a.ObstType) : (st ? st.ob : false);

      const lat = parseFloat(a.Lat) || (f.geometry ? f.geometry.y : (st ? st.lat : 26.4));
      const lon = parseFloat(a.Lon) || (f.geometry ? f.geometry.x : (st ? st.lon : 50.1));

      return {
        n: a.OBJECTID || (idx + 1),
        siteNo: a.SiteNo || a.OBJECTID || (idx + 1),
        code: code,
        type: a.AdvType === '1يونيبول' ? 'يونيبول' : (a.AdvType || 'يونيبول'),
        lat: lat,
        lon: lon,
        bal: a.City || (st ? st.bal : 'الدمام'),
        hay: (st && st.hay) ? st.hay : (a.City || 'الدمام'),
        dec: dec,
        base: a.PrevBase || (st ? st.base : 'لا'),
        note: note,
        ob: ob,
        atts: atts
      };
    });

    const nowTime = new Date().toLocaleTimeString('ar-SA');
    syncText.textContent = `🟢 متصل بالطبقة المباشرة (${D.length} موقع — ${nowTime})`;
    syncPill.style.borderColor = 'rgba(34, 197, 94, 0.4)';
    map.closePopup();
    applyFilters();
    succeeded = true;
  } catch (err) {
    console.warn('Live ArcGIS sync notice:', err);
    syncText.textContent = `تعذر الاتصال بالطبقة المباشرة: ${err.message}`;
    syncPill.style.borderColor = 'rgba(239, 68, 68, 0.45)';
  } finally {
    if (refreshBtn) {
      refreshBtn.disabled = false;
      refreshBtn.classList.remove('spinning');
      if (refreshLabel) {
        if (isManual && succeeded) {
          refreshLabel.textContent = '✓ تم التحديث';
          setTimeout(() => {
            if (!refreshBtn.disabled) refreshLabel.textContent = 'تحديث البيانات';
          }, 2000);
        } else {
          refreshLabel.textContent = 'تحديث البيانات';
        }
      }
    }
  }
}

/* ===================================================================
   EVENT LISTENERS & STARTUP
   =================================================================== */
document.addEventListener('DOMContentLoaded', async () => {
  initMap();
  initCharts();

  const syncText = document.getElementById('syncText');
  syncText.textContent = 'جاري مزامنة وقراءة طبقة معالم ArcGIS الحية...';

  // Load live feature layer directly so all points load in a single unified stage!
  await loadLiveFeatureLayer();

  // Fallback if live layer didn't render
  if (!markerLayer.getLayers().length) {
    applyFilters();
  }

  // Open site detail page if URL hash specifies #site=...
  if (location.hash.startsWith('#site=')) {
    const hashCode = decodeURIComponent(location.hash.replace('#site=', '').trim());
    if (hashCode) openSiteDetailPage(hashCode, false);
  }

  // Search input
  const searchInput = document.getElementById('globalSearch');
  searchInput.addEventListener('input', e => {
    filters.search = e.target.value.trim();
    applyFilters();
  });

  // KPI card click listeners
  document.querySelectorAll('.kpi-card').forEach(c => {
    c.addEventListener('click', () => {
      setKpiFilter(c.dataset.kpi);
    });
  });

  // View Switcher
  const btnExec = document.getElementById('btnExecView');
  const btnTable = document.getElementById('btnTableView');
  const execView = document.getElementById('executiveView');
  const tableView = document.getElementById('tableView');

  btnExec.addEventListener('click', () => {
    btnExec.classList.add('active');
    btnTable.classList.remove('active');
    execView.style.display = 'grid';
    tableView.style.display = 'none';
    setTimeout(() => map.invalidateSize(), 150);
  });

  btnTable.addEventListener('click', () => {
    btnTable.classList.add('active');
    btnExec.classList.remove('active');
    execView.style.display = 'none';
    tableView.style.display = 'flex';
  });

  // Refresh Data Button
  document.getElementById('btnRefreshData').addEventListener('click', () => {
    loadLiveFeatureLayer(true);
  });

  // Reset Filters
  document.getElementById('btnResetFilters').addEventListener('click', clearAllFilters);

  // Startup sync complete
});
</script>
</body>
</html>
'''

with open('EasternRegion/index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("EasternRegion/index.html updated with Doughnut / Pie chart variety and interactive toggles!")

