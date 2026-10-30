import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const dataPath = fileURLToPath(new URL('../src/data/horses.json', import.meta.url));
const { horses } = JSON.parse(await readFile(dataPath, 'utf8'));
const validRarities = new Set(['normal', 'elite', 'epic', 'legend']);
const statKeys = ['speed', 'power', 'jump', 'brains'];
const errors = [];

for (const key of ['id', 'number', 'slug']) {
  const seen = new Map();
  horses.forEach((horse, index) => {
    const value = horse[key];
    if (!seen.has(value)) seen.set(value, []);
    seen.get(value).push(index + 1);
  });
  for (const [value, records] of seen) {
    if (records.length > 1) errors.push(`duplicate ${key} ${JSON.stringify(value)} at records ${records.join(', ')}`);
  }
}

horses.forEach((horse, index) => {
  const record = index + 1;
  if (!horse.name) errors.push(`record ${record} (${horse.id ?? 'unknown'}): missing name`);
  if (!horse.breed) errors.push(`record ${record} (${horse.id ?? 'unknown'}): missing breed`);
  if (!horse.stats || statKeys.some(stat => horse.stats[stat] === undefined)) {
    errors.push(`record ${record} (${horse.id ?? 'unknown'}): missing stats`);
  }
  if (horse.stats && statKeys.every(stat => typeof horse.stats[stat] === 'number')) {
    const sum = statKeys.reduce((total, stat) => total + horse.stats[stat], 0);
    if (horse.total !== sum) errors.push(`record ${record} (${horse.id ?? 'unknown'}): total ${horse.total} !== stats sum ${sum}`);
  }
  if (!validRarities.has(horse.rarity)) errors.push(`record ${record} (${horse.id ?? 'unknown'}): invalid rarity ${JSON.stringify(horse.rarity)}`);
});

if (errors.length) {
  console.error(`HorseDex validation failed with ${errors.length} error${errors.length === 1 ? '' : 's'}:`);
  errors.forEach(error => console.error(`- ${error}`));
  process.exitCode = 1;
} else {
  console.log(`HorseDex validation passed: ${horses.length} records checked.`);
}
