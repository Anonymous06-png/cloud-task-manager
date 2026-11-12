// Node-only behavior harness for the real sidebar JS. No browser/layout simulation.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/js/app.js'), 'utf8');

function fixture({ mobile = false, collapsed = false, theme = 'light', storageFails = false } = {}) {
  let document;
  class Element {
    constructor(attrs = {}) {
      this.attrs = { ...attrs };
      this.dataset = {};
      this.style = {};
      this.listeners = {};
      this.queries = {};
      this.children = [];
      this.parent = null;
      this.inert = false;
      this.hidden = false;
      this.offsetParent = {};
      const classes = new Set();
      this.classList = {
        contains: key => classes.has(key),
        add: key => classes.add(key),
        remove: key => classes.delete(key),
        toggle: key => { if (classes.has(key)) { classes.delete(key); return false; } classes.add(key); return true; },
      };
    }
    append(...children) { children.forEach(child => { child.parent = this; this.children.push(child); }); }
    contains(other) { return other === this || this.children.some(child => child.contains(other)); }
    setAttribute(key, value) { this.attrs[key] = value; }
    getAttribute(key) { return this.attrs[key] ?? null; }
    removeAttribute(key) { delete this.attrs[key]; }
    addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
    fire(type, props = {}) {
      const event = { target: this, button: 0, defaultPrevented: false,
        preventDefault() { this.defaultPrevented = true; }, ...props };
      (this.listeners[type] || []).forEach(fn => fn(event));
      return event;
    }
    querySelectorAll(selector) { return this.queries[selector] || []; }
    querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
    closest(selector) {
      if (selector !== '[inert]') throw Error(`Unexpected closest: ${selector}`);
      return this.inert ? this : this.parent?.closest(selector) || null;
    }
    focus() { document.activeElement = this; }
    getBoundingClientRect() { return this.rect; }
  }
  const root = new Element();
  root.dataset = { sidebar: collapsed ? 'collapsed' : 'expanded', theme };
  const sidebar = new Element();
  const account = new Element();
  const trigger = new Element({ 'aria-expanded': 'false' });
  trigger.hidden = true;
  const panel = new Element();
  panel.hidden = panel.inert = true;
  const settings = new Element({ href: '/settings/' });
  const profile = new Element({ href: '/profile/' });
  const logoutForm = new Element();
  const logout = new Element();
  const outside = new Element();
  const mobileButton = new Element();
  const drawerClose = new Element();
  const scrim = new Element();
  const collapse = new Element();
  collapse.dataset = { labelCollapse: 'Collapse sidebar', labelExpand: 'Expand sidebar' };
  const expand = new Element();
  expand.dataset = { ...collapse.dataset };
  const expandedBrand = new Element();
  expandedBrand.dataset = { ...collapse.dataset };
  const themeToggle = new Element();
  const themeChoice = new Element();
  themeChoice.value = 'dark';
  const sidebarChoice = new Element();
  sidebarChoice.value = 'collapsed';
  const dashboard = new Element({ href: '/dashboard/' });
  const content = new Element();
  const skip = new Element();
  sidebar.append(account, drawerClose, collapse, expand, expandedBrand, dashboard);
  account.append(trigger, panel);
  panel.append(profile, settings, logoutForm);
  logoutForm.append(logout);
  sidebar.rect = { left: 0, bottom: 800, width: mobile ? 280 : collapsed ? 72 : 248 };
  trigger.rect = { left: 12, top: 732, width: mobile ? 255 : collapsed ? 44 : 223 };
  sidebar.queries['[data-account]'] = [account];
  sidebar.queries['[data-mobile-close]'] = [drawerClose];
  sidebar.queries['a[aria-current="page"]'] = [dashboard];
  sidebar.queries['a[href], button:not([disabled])'] = [drawerClose, dashboard, trigger, profile, settings, logout];
  account.queries['.account-trigger'] = [trigger];
  account.queries['.account-dropdown'] = [panel];
  panel.queries['a[href], button:not([disabled])'] = [profile, settings, logout];
  panel.queries.form = [logoutForm];
  document = new Element();
  document.documentElement = root;
  document.body = new Element();
  document.activeElement = outside;
  document.getElementById = id => id === 'workspace-sidebar' ? sidebar : null;
  Object.assign(document.queries, {
    '[data-mobile-toggle]': [mobileButton], '.app-content': [content], '.skip-link': [skip],
    '[data-sidebar-toggle]': [collapse, expand, expandedBrand],
    '[data-theme-toggle]': [themeToggle], '[data-theme-choice]': [themeChoice],
    '[data-sidebar-choice]': [sidebarChoice], '[data-mobile-close]': [drawerClose, scrim],
    '.sidebar-brand-toggle': [expand], '.sidebar-collapse-toggle': [collapse],
    '.side-nav a, .sidebar-settings, .account-dropdown a': [dashboard, profile, settings],
  });
  const media = new Element();
  media.matches = mobile;
  const window = new Element();
  window.innerHeight = 800;
  window.innerWidth = mobile ? 320 : 1280;
  window.matchMedia = () => media;
  const saved = {};
  const localStorage = { setItem(key, value) { if (storageFails) throw Error('Unavailable'); saved[key] = value; } };
  vm.runInNewContext(source, { document, window, localStorage });
  const open = () => trigger.fire('click');
  const isOpen = () => trigger.getAttribute('aria-expanded') === 'true';
  return { document, window, root, sidebar, account, trigger, panel, profile, settings, logoutForm, logout,
    outside, mobileButton, drawerClose, scrim, collapse, expand, themeToggle, themeChoice,
    sidebarChoice, dashboard, content, skip, media, saved, open, isOpen };
}

let passed = 0;
function test(label, fn) { fn(); passed++; console.log(`PASS ${label}`); }

test('expanded/rail/mobile x Light/Dark: initialize, open above trigger, second click closes', () => {
  for (const theme of ['light', 'dark']) for (const state of [{}, { collapsed: true }, { mobile: true, collapsed: true }]) {
    const f = fixture({ theme, ...state });
    assert.equal(f.trigger.hidden, false);
    assert.equal(f.panel.hidden, false);
    assert.equal(f.panel.inert, true);
    f.open();
    assert.equal(f.isOpen(), true);
    assert.equal(f.panel.inert, false);
    assert.equal(f.panel.dataset.open, 'true');
    assert.equal(f.panel.style.bottom, '76px');
    assert.equal(f.panel.style.maxHeight, '712px');
    assert.equal(f.panel.style.left, '12px');
    assert.equal(f.panel.style.width, state.mobile ? '256px' : '260px');
    f.open();
    assert.equal(f.isOpen(), false);
    assert.equal(f.panel.inert, true);
    assert.equal(f.root.dataset.theme, theme);
  }
});
test('inside click stays open; outside click closes and rescues focus', () => {
  const f = fixture(); f.open(); f.settings.focus();
  f.document.fire('click', { target: f.panel });
  assert.equal(f.isOpen(), true);
  f.document.fire('click', { target: f.outside });
  assert.equal(f.isOpen(), false);
  assert.equal(f.document.activeElement, f.trigger);
});
test('ArrowDown/Up focus real actions; Escape restores trigger', () => {
  const f = fixture();
  assert.equal(f.trigger.fire('keydown', { key: 'ArrowDown' }).defaultPrevented, true);
  assert.equal(f.document.activeElement, f.profile);
  assert.equal(f.document.fire('keydown', { key: 'Escape' }).defaultPrevented, true);
  assert.equal(f.document.activeElement, f.trigger);
  assert.equal(f.isOpen(), false);
  f.trigger.fire('keydown', { key: 'ArrowUp' });
  assert.equal(f.document.activeElement, f.logout);
});
test('Tab focus leaving account closes without stealing focus', () => {
  const f = fixture(); f.open(); f.outside.focus();
  f.account.fire('focusout', { relatedTarget: f.outside });
  assert.equal(f.isOpen(), false);
  assert.equal(f.document.activeElement, f.outside);
});
test('Profile, Settings and dashboard navigation close; modified/cancelled clicks remain open', () => {
  const f = fixture();
  for (const props of [{ ctrlKey: true }, { metaKey: true }, { defaultPrevented: true }]) {
    if (!f.isOpen()) f.open();
    f.settings.fire('click', props);
    assert.equal(f.isOpen(), true);
  }
  f.settings.fire('click'); assert.equal(f.isOpen(), false);
  f.open(); f.profile.fire('click'); assert.equal(f.isOpen(), false);
  f.open(); f.dashboard.fire('click'); assert.equal(f.isOpen(), false);
});
test('logout submits without interception; cancelled submit remains open', () => {
  const f = fixture(); f.open();
  f.logoutForm.fire('submit', { defaultPrevented: true }); assert.equal(f.isOpen(), true);
  const event = f.logoutForm.fire('submit');
  assert.equal(event.defaultPrevented, false);
  assert.equal(f.isOpen(), false);
});
test('mobile: first Escape closes account only, second closes drawer', () => {
  const f = fixture({ mobile: true });
  f.mobileButton.fire('click'); f.open();
  assert.equal(f.sidebar.inert, false); assert.equal(f.content.inert, true);
  f.document.fire('keydown', { key: 'Escape' });
  assert.equal(f.isOpen(), false);
  assert.equal(f.document.body.classList.contains('mobile-nav-open'), true);
  assert.equal(f.document.activeElement, f.trigger);
  f.document.fire('keydown', { key: 'Escape' });
  assert.equal(f.document.body.classList.contains('mobile-nav-open'), false);
  assert.equal(f.document.activeElement, f.mobileButton);
});
test('mobile focus trap excludes closed/inert dropdown actions', () => {
  const f = fixture({ mobile: true }); f.mobileButton.fire('click');
  f.trigger.focus(); f.document.fire('keydown', { key: 'Tab' });
  assert.equal(f.document.activeElement, f.drawerClose);
  f.open(); f.logout.focus(); f.document.fire('keydown', { key: 'Tab' });
  assert.equal(f.document.activeElement, f.drawerClose);
  f.drawerClose.focus(); f.document.fire('keydown', { key: 'Tab', shiftKey: true });
  assert.equal(f.document.activeElement, f.logout);
});
test('mobile scrim, close button, navigation, logout and breakpoint clear disclosure', () => {
  for (const action of ['scrim', 'drawerClose', 'settings', 'logoutForm', 'media']) {
    const f = fixture({ mobile: true }); f.mobileButton.fire('click'); f.open();
    f[action].fire(action === 'logoutForm' ? 'submit' : action === 'media' ? 'change' : 'click');
    assert.equal(f.isOpen(), false);
    assert.equal(f.document.body.classList.contains('mobile-nav-open'), false);
  }
});
test('collapse and expand preserve storage, aria state and focused toggle', () => {
  const f = fixture(); f.open(); f.collapse.focus(); f.collapse.fire('click');
  assert.equal(f.isOpen(), false); assert.equal(f.root.dataset.sidebar, 'collapsed');
  assert.equal(f.saved['ctm-sidebar'], 'collapsed');
  assert.equal(f.document.activeElement, f.expand);
  assert.equal(f.expand.getAttribute('aria-expanded'), 'false');
  f.expand.fire('click');
  assert.equal(f.root.dataset.sidebar, 'expanded');
  assert.equal(f.document.activeElement, f.collapse);
  f.open(); f.sidebarChoice.fire('change'); assert.equal(f.isOpen(), false);
});
test('theme choices/storage failure do not break account or sidebar', () => {
  const f = fixture({ storageFails: true }); f.open(); f.themeToggle.fire('click');
  assert.equal(f.root.dataset.theme, 'dark'); assert.equal(f.isOpen(), true);
  f.themeChoice.fire('change'); assert.equal(f.root.dataset.theme, 'dark');
  f.collapse.fire('click'); assert.equal(f.root.dataset.sidebar, 'collapsed');
});
test('resize, sidebar scroll, pagehide/pageshow reset stale popup', () => {
  for (const [target, event] of [['window', 'resize'], ['sidebar', 'scroll'], ['window', 'pagehide'], ['window', 'pageshow']]) {
    const f = fixture(); f.open(); f[target].fire(event);
    assert.equal(f.isOpen(), false); assert.equal(f.panel.inert, true);
  }
});
test('short viewport and right edge positioning remain bounded above trigger', () => {
  const f = fixture(); f.window.innerWidth = 320; f.window.innerHeight = 360;
  f.trigger.rect = { left: 240, top: 280, width: 44 }; f.open();
  assert.equal(f.panel.style.left, '48px');
  assert.equal(f.panel.style.bottom, '88px');
  assert.equal(f.panel.style.maxHeight, '260px');
});
test('source: shared click/Escape handlers, scoped motion and preserved rail selectors', () => {
  assert.equal((source.match(/document\.addEventListener\('keydown'/g) || []).length, 1);
  assert.equal((source.match(/document\.addEventListener\('click'/g) || []).length, 1);
  const css = fs.readFileSync(path.join(__dirname, '../static/css/app.css'), 'utf8');
  assert.match(css, /transition: opacity 160ms .*transform 160ms/);
  assert.match(css, /@media \(prefers-reduced-motion: reduce\)\s*\{\s*\.account-dropdown, \.account-trigger \.profile-chevron \{ transition: none; transform: none; \}/);
  assert.match(css, /:root\[data-sidebar="collapsed"\] \.sidebar :is\([^\n]+\.profile,/);
});
console.log(`${passed} focused sidebar JS/source checks passed (no browser automation).`);
