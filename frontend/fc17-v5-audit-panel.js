/**
 * fc17-v5-audit-panel.js
 * V5 audit trail panel renderer for fieldcheck-verdict.html
 * Reads composite_v022_31.v5_corrections[] and renders raw → corrections → final flow
 *
 * Sprint B1 · V022.36-V5.2 · The moat-revealing transparency feature
 *
 * Usage:
 *   1. Include this file: <script src="/fc17-v5-audit-panel.js"></script>
 *   2. After API response renders, call:
 *      window.FCv5Audit.render(responseObj, targetContainerElement)
 *   3. Or use auto-mount mode (listens for verdictRendered event):
 *      window.FCv5Audit.autoMount('#v5-audit-mount')
 */
(function(global) {
  'use strict';

  // ─────────────────────────────────────────────────────────────────────
  // Configuration
  // ─────────────────────────────────────────────────────────────────────
  const RULE_LABELS = {
    'suffix-amateur-ceiling': {
      label: 'Family lineage detection',
      icon: '👤',
      severity: 'info'
    },
    'hs-evidence-ceiling-non-phenom': {
      label: 'HS evidence ceiling',
      icon: '🎓',
      severity: 'info'
    },
    'd1-college-amateur-ceiling': {
      label: 'D1 amateur ceiling',
      icon: '🏛',
      severity: 'info'
    },
    'active-player-ceiling': {
      label: 'Active career ceiling',
      icon: '⚡',
      severity: 'info'
    },
    'rookie-evidence-ceiling': {
      label: 'Rookie sample ceiling',
      icon: '🌱',
      severity: 'info'
    },
    'identity-classification-mismatch': {
      label: 'Identity review pending',
      icon: '⚠',
      severity: 'warn'
    }
  };

  // ─────────────────────────────────────────────────────────────────────
  // CSS injection (one-time)
  // ─────────────────────────────────────────────────────────────────────
  let cssInjected = false;
  function injectCSS() {
    if (cssInjected) return;
    cssInjected = true;
    const css = `
      .fc-v5-audit{background:#0a0a0a;border:1px solid #2a2a2a;border-radius:8px;padding:18px;margin:18px 0;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:#e8e8e8}
      .fc-v5-audit-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;cursor:pointer;user-select:none}
      .fc-v5-audit-title{font-size:12px;font-weight:600;color:#60a5fa;text-transform:uppercase;letter-spacing:0.5px}
      .fc-v5-audit-badge{padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600}
      .fc-v5-audit-badge.has-corrections{background:#1a2a3a;color:#93c5fd;border:1px solid #1e40af}
      .fc-v5-audit-badge.has-flag{background:#2a2410;color:#fcd34d;border:1px solid #854d0e}
      .fc-v5-audit-badge.no-corrections{background:#0f2417;color:#4ade80;border:1px solid #1f4a2e}
      .fc-v5-audit-chevron{color:#666;font-size:11px;margin-left:8px;transition:transform 0.15s}
      .fc-v5-audit.collapsed .fc-v5-audit-body{display:none}
      .fc-v5-audit.collapsed .fc-v5-audit-chevron{transform:rotate(-90deg)}
      .fc-v5-audit-raw{display:flex;justify-content:space-between;padding:10px 14px;background:#141414;border-radius:6px;margin-bottom:12px;align-items:center}
      .fc-v5-audit-raw-label{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:0.5px}
      .fc-v5-audit-raw-val{font-size:18px;font-weight:600;color:#cbd5e1}
      .fc-v5-audit-arrow{text-align:center;color:#666;font-size:16px;margin:4px 0;line-height:1}
      .fc-v5-correction{background:#141414;border-left:3px solid #60a5fa;padding:12px 14px;margin:6px 0;border-radius:0 6px 6px 0}
      .fc-v5-correction.warn{border-left-color:#facc15;background:#2a2410}
      .fc-v5-correction-rule{font-size:11px;color:#60a5fa;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;display:flex;align-items:center;gap:6px}
      .fc-v5-correction.warn .fc-v5-correction-rule{color:#fcd34d}
      .fc-v5-correction-flow{display:flex;align-items:center;gap:10px;margin:4px 0;font-size:14px}
      .fc-v5-from{color:#ef4444;font-weight:600}
      .fc-v5-to{color:#4ade80;font-weight:600}
      .fc-v5-flow-arrow{color:#666}
      .fc-v5-correction-reason{font-size:12px;color:#94a3b8;line-height:1.55;margin-top:6px}
      .fc-v5-correction.warn .fc-v5-correction-reason{color:#fde68a}
      .fc-v5-audit-final{display:flex;justify-content:space-between;padding:12px 14px;background:#0f2417;border:1px solid #1f4a2e;border-radius:6px;margin-top:12px;align-items:center}
      .fc-v5-audit-final.warn{background:#2a2410;border-color:#854d0e}
      .fc-v5-audit-final-label{font-size:12px;color:#86efac}
      .fc-v5-audit-final.warn .fc-v5-audit-final-label{color:#fde68a}
      .fc-v5-audit-final-val{font-size:20px;font-weight:600;color:#bbf7d0}
      .fc-v5-audit-final.warn .fc-v5-audit-final-val{color:#fde68a}
      .fc-v5-empty{text-align:center;padding:18px;color:#666;font-size:12px;font-style:italic}
    `;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
  }

  // ─────────────────────────────────────────────────────────────────────
  // Helpers
  // ─────────────────────────────────────────────────────────────────────
  function escapeHtml(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/[&<>"']/g, function(c) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }

  function fmtNum(n) {
    if (n === null || n === undefined) return '—';
    return Number(n).toFixed(2);
  }

  function fmtCompact(n) {
    if (n === null || n === undefined) return '—';
    return Number(n).toFixed(1);
  }

  // ─────────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────────
  function render(response, container, opts) {
    opts = opts || {};
    injectCSS();

    if (!response || typeof response !== 'object') {
      container.innerHTML = '';
      return;
    }

    const meta = response.composite_v022_31 || {};
    const corrections = Array.isArray(meta.v5_corrections) ? meta.v5_corrections : [];
    const raw = meta.raw;
    const final = meta.v5_corrected !== undefined ? meta.v5_corrected : response.composite;
    const hasCorrections = corrections.some(c => c.from !== undefined);
    const hasFlag = corrections.some(c => c.flag);

    // No V5 data available at all
    if (raw === undefined && !corrections.length) {
      container.innerHTML = '';
      return;
    }

    let badgeClass = 'no-corrections';
    let badgeText = 'no corrections';
    if (hasFlag && hasCorrections) {
      badgeClass = 'has-flag';
      const correctionsCount = corrections.filter(c => c.from !== undefined).length;
      badgeText = correctionsCount + ' correction' + (correctionsCount > 1 ? 's' : '') + ' · 1 flag';
    } else if (hasFlag) {
      badgeClass = 'has-flag';
      badgeText = 'flag pending review';
    } else if (hasCorrections) {
      badgeClass = 'has-corrections';
      const correctionsCount = corrections.filter(c => c.from !== undefined).length;
      badgeText = correctionsCount + ' correction' + (correctionsCount > 1 ? 's' : '') + ' applied';
    }

    const collapsedDefault = opts.collapsedDefault !== undefined ? opts.collapsedDefault : !hasCorrections;
    const collapsedClass = collapsedDefault ? ' collapsed' : '';

    let html = '<div class="fc-v5-audit' + collapsedClass + '" id="fc-v5-audit-panel">';
    html += '<div class="fc-v5-audit-header" onclick="this.parentElement.classList.toggle(\'collapsed\')">';
    html += '<div class="fc-v5-audit-title">V5 Audit Trail</div>';
    html += '<div><span class="fc-v5-audit-badge ' + badgeClass + '">' + escapeHtml(badgeText) + '</span><span class="fc-v5-audit-chevron">▾</span></div>';
    html += '</div>';
    html += '<div class="fc-v5-audit-body">';

    if (raw !== undefined) {
      html += '<div class="fc-v5-audit-raw">';
      html += '<div class="fc-v5-audit-raw-label">Raw synthesis (Sonnet 4.5 evidence eval)</div>';
      html += '<div class="fc-v5-audit-raw-val">' + fmtNum(raw) + '</div>';
      html += '</div>';
    }

    if (hasCorrections || hasFlag) {
      if (raw !== undefined) {
        html += '<div class="fc-v5-audit-arrow">↓</div>';
      }

      corrections.forEach(function(c) {
        const ruleInfo = RULE_LABELS[c.rule] || { label: c.rule, icon: '•', severity: 'info' };
        const isFlag = c.flag !== undefined;
        const cardClass = isFlag || ruleInfo.severity === 'warn' ? 'fc-v5-correction warn' : 'fc-v5-correction';

        html += '<div class="' + cardClass + '">';
        html += '<div class="fc-v5-correction-rule">' + escapeHtml(ruleInfo.icon) + ' ' + escapeHtml(ruleInfo.label) + '</div>';

        if (!isFlag && c.from !== undefined && c.to !== undefined) {
          html += '<div class="fc-v5-correction-flow">';
          html += '<span class="fc-v5-from">' + fmtNum(c.from) + '</span>';
          html += '<span class="fc-v5-flow-arrow">→</span>';
          html += '<span class="fc-v5-to">' + fmtNum(c.to) + '</span>';
          html += '</div>';
        }

        if (c.reason) {
          html += '<div class="fc-v5-correction-reason">' + escapeHtml(c.reason) + '</div>';
        }

        html += '</div>';
      });

      if (final !== undefined) {
        const finalClass = hasFlag ? 'fc-v5-audit-final warn' : 'fc-v5-audit-final';
        html += '<div class="' + finalClass + '">';
        html += '<div class="fc-v5-audit-final-label">' + (hasFlag ? 'Final composite (review pending)' : 'Final composite (after corrections)') + '</div>';
        html += '<div class="fc-v5-audit-final-val">' + fmtCompact(final) + '</div>';
        html += '</div>';
      }
    } else {
      html += '<div class="fc-v5-empty">Synthesis output passed through cleanly — no bright-line rules fired.<br>Evidence depth justifies score.</div>';
    }

    html += '</div></div>';
    container.innerHTML = html;
  }

  // ─────────────────────────────────────────────────────────────────────
  // Auto-mount mode · listens for verdict response events
  // ─────────────────────────────────────────────────────────────────────
  function autoMount(selector) {
    function attempt() {
      const container = document.querySelector(selector);
      if (!container) return false;

      // Listen for custom events
      document.addEventListener('fc-verdict-rendered', function(ev) {
        if (ev.detail && ev.detail.response) {
          render(ev.detail.response, container);
        }
      });

      // Also expose a manual hook for verdict page integration
      global.FCv5Audit._mountTarget = container;
      return true;
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', attempt);
    } else {
      attempt();
    }
  }

  // ─────────────────────────────────────────────────────────────────────
  // Convenience: try to find verdict response in window state
  // ─────────────────────────────────────────────────────────────────────
  function renderFromGlobal(globalKey, targetSelector) {
    const response = global[globalKey || 'lastVerdictResponse'];
    const container = document.querySelector(targetSelector || '#fc-v5-audit-mount');
    if (response && container) {
      render(response, container);
    }
  }

  // ─────────────────────────────────────────────────────────────────────
  // Public API
  // ─────────────────────────────────────────────────────────────────────
  global.FCv5Audit = {
    render: render,
    autoMount: autoMount,
    renderFromGlobal: renderFromGlobal,
    _injectCSS: injectCSS,
    _version: 'V022.36-V5.2'
  };

})(typeof window !== 'undefined' ? window : this);
