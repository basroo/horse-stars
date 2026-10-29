const root = document.querySelector<HTMLElement>('[data-dex]');
if (root) {
  const form = root.querySelector<HTMLFormElement>('form')!;
  const grid = root.querySelector<HTMLElement>('[data-dex-grid]')!;
  const cards = [...grid.querySelectorAll<HTMLElement>('[data-horse]')];
  const output = root.querySelector<HTMLOutputElement>('[data-results]')!;
  const empty = root.querySelector<HTMLElement>('[data-empty]')!;
  const keys = ['q', 'breed', 'rarity', 'edition', 'sort'] as const;
  const fields = Object.fromEntries(keys.map(key => [key, form.elements.namedItem(key)])) as Record<typeof keys[number], HTMLInputElement | HTMLSelectElement>;
  const normalize = (value: string) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().trim();

  function readUrl() {
    const params = new URLSearchParams(location.search);
    for (const key of keys) {
      const field = fields[key];
      const value = params.get(key) ?? (key === 'sort' ? 'number' : '');
      field.value = value;
      if (field instanceof HTMLSelectElement && field.selectedIndex < 0) field.value = key === 'sort' ? 'number' : '';
    }
  }
  function update(syncUrl = true) {
    const search = normalize(fields.q.value);
    let count = 0;
    const sort = fields.sort.value;
    const sorted = [...cards].sort((a, b) => {
      const value = sort === 'number' ? Number(a.dataset.number) - Number(b.dataset.number) : Number(b.dataset[sort]) - Number(a.dataset[sort]);
      return value || Number(a.dataset.number) - Number(b.dataset.number) || a.dataset.name!.localeCompare(b.dataset.name!);
    });
    for (const card of sorted) {
      const matches = normalize(card.dataset.name!).includes(search) && (['breed', 'rarity', 'edition'] as const).every(key => !fields[key].value || card.dataset[key] === fields[key].value);
      card.hidden = !matches;
      if (matches) count++;
      grid.append(card);
    }
    output.textContent = output.dataset.template!.replace('{count}', String(count)).replace('{total}', String(cards.length));
    empty.hidden = count > 0;
    if (syncUrl) {
      const url = new URL(location.href);
      for (const key of keys) {
        const value = fields[key].value.trim();
        if (value && !(key === 'sort' && value === 'number')) url.searchParams.set(key, value);
        else url.searchParams.delete(key);
      }
      history.replaceState(null, '', url);
    }
  }
  form.hidden = false;
  readUrl(); update(false);
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', () => update());
  form.addEventListener('change', () => update());
  form.addEventListener('reset', () => queueMicrotask(() => update()));
  root.querySelector('[data-clear]')?.addEventListener('click', () => form.reset());
  window.addEventListener('popstate', () => { readUrl(); update(false); });
  window.addEventListener('pageshow', () => { readUrl(); update(false); });
}
