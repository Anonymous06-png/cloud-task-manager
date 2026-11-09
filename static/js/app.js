(() => {
  const root = document.documentElement;
  const sidebar = document.getElementById('workspace-sidebar');
  const mobileButton = document.querySelector('[data-mobile-toggle]');
  const content = document.querySelector('.app-content');
  const skipLink = document.querySelector('.skip-link');
  const mobile = window.matchMedia('(max-width: 760px)');
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch (_) {} };

  const syncSidebarState = () => {
    const state = root.dataset.sidebar === 'collapsed' ? 'collapsed' : 'expanded';
    const isCollapsed = state === 'collapsed';
    document.querySelectorAll('[data-sidebar-toggle]').forEach(btn => {
      btn.setAttribute('aria-expanded', String(!isCollapsed));
      const collapseLabel = btn.dataset.labelCollapse;
      const expandLabel = btn.dataset.labelExpand;
      if (collapseLabel && expandLabel) {
        const nextLabel = isCollapsed ? expandLabel : collapseLabel;
        btn.setAttribute('title', nextLabel);
        btn.setAttribute('data-tooltip', nextLabel);
        btn.setAttribute('aria-label', nextLabel);
      }
    });
  };

  const syncChoices = () => {
    const theme = root.dataset.theme === 'dark' ? 'dark' : 'light';
    const sidebarState = root.dataset.sidebar === 'collapsed' ? 'collapsed' : 'expanded';
    document.querySelectorAll('[data-theme-choice]').forEach(input => {
      input.checked = input.value === theme;
    });
    document.querySelectorAll('[data-sidebar-choice]').forEach(input => {
      input.checked = input.value === sidebarState;
    });
    syncSidebarState();
  };

  document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
    btn.addEventListener('click', () => {
      root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      save('ctm-theme', root.dataset.theme);
      syncChoices();
    });
  });

  document.querySelectorAll('[data-sidebar-toggle]').forEach(btn => {
    btn.addEventListener('click', () => {
      root.dataset.sidebar = root.dataset.sidebar === 'collapsed' ? 'expanded' : 'collapsed';
      save('ctm-sidebar', root.dataset.sidebar);
      syncChoices();
    });
  });

  document.querySelectorAll('[data-theme-choice]').forEach(input => {
    input.addEventListener('change', () => {
      root.dataset.theme = input.value;
      save('ctm-theme', input.value);
      syncChoices();
    });
  });

  document.querySelectorAll('[data-sidebar-choice]').forEach(input => {
    input.addEventListener('change', () => {
      root.dataset.sidebar = input.value;
      save('ctm-sidebar', input.value);
      syncChoices();
    });
  });

  const syncMobileState = () => {
    const open = mobile.matches && document.body.classList.contains('mobile-nav-open');
    if (sidebar) sidebar.inert = mobile.matches && !open;
    if (content) content.inert = open;
    if (skipLink) skipLink.inert = open;
  };

  const closeMobile = (restoreFocus = false) => {
    const wasOpen = document.body.classList.contains('mobile-nav-open');
    document.body.classList.remove('mobile-nav-open');
    mobileButton?.setAttribute('aria-expanded', 'false');
    sidebar?.removeAttribute('role');
    sidebar?.removeAttribute('aria-modal');
    syncMobileState();
    if (restoreFocus && wasOpen) mobileButton?.focus();
  };

  mobileButton?.addEventListener('click', () => {
    const open = document.body.classList.toggle('mobile-nav-open');
    mobileButton.setAttribute('aria-expanded', String(open));
    if (open) {
      sidebar?.setAttribute('role', 'dialog');
      sidebar?.setAttribute('aria-modal', 'true');
      syncMobileState();
      sidebar?.querySelector('[data-mobile-close]')?.focus();
    } else {
      sidebar?.removeAttribute('role');
      sidebar?.removeAttribute('aria-modal');
      syncMobileState();
    }
  });

  document.querySelectorAll('[data-mobile-close]').forEach(button => {
    button.addEventListener('click', () => closeMobile(true));
  });
  mobile.addEventListener('change', () => closeMobile(false));

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      closeMobile(true);
      document.querySelectorAll('details.task-menu[open]').forEach(menu => {
        if (menu.contains(document.activeElement)) menu.querySelector('summary')?.focus();
        menu.removeAttribute('open');
      });
    }
    if (event.key === 'Tab' && document.body.classList.contains('mobile-nav-open') && sidebar) {
      const focusable = [...sidebar.querySelectorAll('a[href], button:not([disabled])')].filter(el => el.offsetParent !== null);
      if (focusable.length) {
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (!sidebar.contains(document.activeElement)) {
          event.preventDefault();
          first.focus();
        } else if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    }
  });

  document.addEventListener('click', event => {
    document.querySelectorAll('details.task-menu[open]').forEach(menu => {
      if (!menu.contains(event.target)) menu.removeAttribute('open');
    });
  });

  document.querySelectorAll('.side-nav a, .sidebar-settings').forEach(link => {
    link.addEventListener('click', () => closeMobile(false));
  });

  document.querySelectorAll('details.task-menu').forEach(menu => {
    menu.addEventListener('toggle', () => {
      if (!menu.open) return;
      document.querySelectorAll('details.task-menu[open]').forEach(other => {
        if (other !== menu) other.removeAttribute('open');
      });
    });
  });

  document.querySelectorAll('[data-submit-form]').forEach(form => {
    const button = form.querySelector('[data-submit-label]');
    const label = button?.querySelector('span');
    const original = label?.textContent;
    const reset = () => {
      if (!button) return;
      button.disabled = false;
      form.removeAttribute('aria-busy');
      if (label) label.textContent = original;
    };
    form.addEventListener('submit', () => {
      if (!button) return;
      button.disabled = true;
      form.setAttribute('aria-busy', 'true');
      if (label) label.textContent = button.dataset.submitLabel;
      window.setTimeout(reset, 10000);
    });
    window.addEventListener('pageshow', reset);
  });

  const invalidField = document.querySelector('.form-field [aria-invalid="true"]');
  if (invalidField) invalidField.focus();

  root.dataset.theme = root.dataset.theme === 'dark' ? 'dark' : 'light';
  root.dataset.sidebar = root.dataset.sidebar === 'collapsed' ? 'collapsed' : 'expanded';
  const activeNavigation = sidebar?.querySelector('a[aria-current="page"]');
  if (activeNavigation) save('ctm-active-navigation', activeNavigation.getAttribute('href'));
  syncChoices();
  syncMobileState();
})();
