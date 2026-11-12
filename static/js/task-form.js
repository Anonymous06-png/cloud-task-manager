(() => {
  document.querySelectorAll('.task-editor [data-task-date-presets]').forEach(presets => {
    const input = document.getElementById(presets.dataset.taskDatePresets);
    if (!input || input.type !== 'date' || input.form !== presets.closest('form')) return;

    presets.querySelectorAll('button').forEach(button => {
      button.addEventListener('click', () => {
        if (button.hasAttribute('data-task-date-clear')) {
          input.value = '';
        } else {
          // Calculate at click time and format locally, never through UTC ISO dates.
          const date = new Date();
          date.setDate(date.getDate() + Number(button.dataset.taskDateOffset));
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');
          input.value = `${year}-${month}-${day}`;
        }
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
      });
    });
    presets.hidden = false;
  });
})();
