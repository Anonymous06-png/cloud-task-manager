/* CSS owns the motion; these ephemeral markers prevent disclosure replay. */
(() => {
  const list = document.querySelector('.flowspace-task-list');
  if (!list || !window.matchMedia('(prefers-reduced-motion: no-preference)').matches) return;

  const entering = new Set();
  const finish = (row) => {
    row.removeAttribute('data-list-enter');
    entering.delete(row);
  };
  const onAnimation = (event) => {
    if (event.animationName === 'flowspace-list-row-enter' && entering.has(event.target)) finish(event.target);
  };
  list.addEventListener('animationend', onAnimation);
  list.addEventListener('animationcancel', onAnimation);
  // Interrupting an entrance must never hide a focused control or replay a group.
  list.addEventListener('focusin', () => entering.forEach(finish), { once: true });
  list.querySelectorAll('.list-group').forEach((group) => {
    group.addEventListener('toggle', () => {
      if (!group.open) group.querySelectorAll('[data-list-enter]').forEach(finish);
    });
  });

  list.querySelectorAll('.full-task-list > .task-row').forEach((row) => {
    if (row.closest('.list-group:not([open])')) return;
    row.setAttribute('data-list-enter', String(Math.min(entering.size, 2)));
    entering.add(row);
  });
})();
