(() => {
  const root = document.documentElement;
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch (_) {} };
  const syncChoices = () => {
    document.querySelectorAll('[data-theme-choice]').forEach(input => { input.checked = input.value === (root.dataset.theme || 'light'); });
    document.querySelectorAll('[data-sidebar-choice]').forEach(input => { input.checked = input.value === (root.dataset.sidebar || 'expanded'); });
  };
  document.querySelector('[data-theme-toggle]')?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    save('ctm-theme', root.dataset.theme);
    syncChoices();
  });
  document.querySelector('[data-sidebar-toggle]')?.addEventListener('click', () => {
    root.dataset.sidebar = root.dataset.sidebar === 'collapsed' ? 'expanded' : 'collapsed';
    save('ctm-sidebar', root.dataset.sidebar);
    syncChoices();
  });
  document.querySelectorAll('[data-theme-choice]').forEach(input => input.addEventListener('change', () => {
    root.dataset.theme = input.value; save('ctm-theme', input.value); syncChoices();
  }));
  document.querySelectorAll('[data-sidebar-choice]').forEach(input => input.addEventListener('change', () => {
    root.dataset.sidebar = input.value; save('ctm-sidebar', input.value); syncChoices();
  }));
  const mobileButton = document.querySelector('[data-mobile-toggle]');
  const closeMobile = () => { document.body.classList.remove('mobile-nav-open'); mobileButton?.setAttribute('aria-expanded', 'false'); };
  mobileButton?.addEventListener('click', () => {
    const open = document.body.classList.toggle('mobile-nav-open');
    mobileButton.setAttribute('aria-expanded', String(open));
  });
  document.querySelector('[data-mobile-close]')?.addEventListener('click', closeMobile);
  document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMobile(); });
  document.querySelectorAll('.side-nav a, .sidebar-settings').forEach(link => link.addEventListener('click', closeMobile));
  syncChoices();
})();
