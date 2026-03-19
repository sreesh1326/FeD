/* ═══════════════════════════════════════════════════════
   FeD — ui.js
   UI Utilities: tab switching, toast, IST clock, helpers
   ═══════════════════════════════════════════════════════ */

const UI = (() => {

  /* ── IST clock ──────────────────────────────────────── */
  function getIST() {
    return new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
  }

  function formatIST(dateISOString) {
    return new Date(dateISOString).toLocaleString('en-IN', {
      timeZone:  'Asia/Kolkata',
      year:      'numeric',
      month:     'short',
      day:       '2-digit',
      hour:      '2-digit',
      minute:    '2-digit',
      second:    '2-digit',
      hour12:    true
    });
  }

  function startClock() {
    const el = document.getElementById('liveTime');
    const tick = () => {
      const t = getIST();
      const h = String(t.getHours()).padStart(2,'0');
      const m = String(t.getMinutes()).padStart(2,'0');
      const s = String(t.getSeconds()).padStart(2,'0');
      if (el) el.textContent = `${h}:${m}:${s}`;
    };
    tick();
    setInterval(tick, 1000);
  }

  /* ── Tab switching ──────────────────────────────────── */
  function switchTab(tabId) {
    // Deactivate all
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => {
      b.classList.remove('active');
      b.setAttribute('aria-selected', 'false');
    });

    // Activate target
    const panel = document.getElementById(`panel-${tabId}`);
    const btn   = document.getElementById(`tab-${tabId}`);
    if (panel) panel.classList.add('active');
    if (btn)   { btn.classList.add('active'); btn.setAttribute('aria-selected', 'true'); }

    // Side-effects
    if (tabId === 'records') App.updateRecords();
    if (tabId !== 'attendance') Camera.stopAttendanceCamera();
  }

  /* ── Toast notifications ────────────────────────────── */
  let toastTimer = null;
  function toast(message, type = 'info') {
    const el = document.getElementById('toast');
    if (!el) return;
    el.textContent = message;
    el.className = `toast ${type} show`;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 3600);
  }

  /* ── System status badge ────────────────────────────── */
  function setStatus(state, label) {
    const badge = document.getElementById('statusBadge');
    const text  = document.getElementById('statusText');
    if (!badge || !text) return;
    badge.className = `status-badge ${state}`;
    text.textContent = label;
  }

  /* ── Initials from full name ─────────────────────────── */
  function initials(name) {
    return name.trim().split(/\s+/).map(w => w[0] || '').join('').slice(0, 2).toUpperCase();
  }

  /* ── Public API ─────────────────────────────────────── */
  return { getIST, formatIST, startClock, switchTab, toast, setStatus, initials };

})();
