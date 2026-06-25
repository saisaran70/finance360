// ── Modal helpers ──────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.add('open'); document.body.style.overflow = 'hidden'; }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.remove('open'); document.body.style.overflow = ''; }
}
function closeModalOnOverlay(event, id) {
  if (event.target.classList.contains('modal-overlay')) closeModal(id);
}

// ── Mobile sidebar ─────────────────────────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const isOpen = sidebar.classList.contains('open');
  sidebar.classList.toggle('open', !isOpen);
  overlay.classList.toggle('open', !isOpen);
  document.body.style.overflow = isOpen ? '' : 'hidden';
}

// ── Flash auto-dismiss ─────────────────────────────────────
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.animation = 'slideIn 250ms ease reverse';
    setTimeout(() => el.remove(), 250);
  }, 4000);
});

// ── Keyboard: Escape ───────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    // Close modals
    document.querySelectorAll('.modal-overlay.open').forEach(m => {
      m.classList.remove('open');
      document.body.style.overflow = '';
    });
    // Close mobile sidebar
    const sidebar = document.getElementById('sidebar');
    if (sidebar && sidebar.classList.contains('open')) toggleSidebar();
  }
});

// ── Form submit loading state ──────────────────────────────
document.addEventListener('submit', e => {
  const form = e.target;
  const btn = form.querySelector('button[type="submit"]');
  if (btn && !btn.dataset.noLoad) {
    const orig = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>';
    // Restore after 8s safety fallback
    setTimeout(() => { btn.disabled = false; btn.innerHTML = orig; }, 8000);
  }
});

// ── Confirm delete helper ──────────────────────────────────
function confirmDelete(message) {
  return confirm(message || 'Are you sure you want to delete this?');
}
