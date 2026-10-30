import source from './horses.json';
import { statKeys, type Horse } from './horse-types';
export type { Horse } from './horse-types';

// Validate at build time so bad imports cannot silently create broken pages.
const ids = new Set<string>();
const slugs = new Set<string>();
const records = source.horses;
export const horses: Horse[] = records.map(record => {
  if (ids.has(record.id) || slugs.has(record.slug)) throw new Error(`Duplicate horse ID or slug: ${record.id}`);
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(record.slug)) throw new Error(`Invalid horse slug: ${record.slug}`);
  if (!['normal', 'elite', 'epic', 'legend'].includes(record.rarity)) throw new Error(`Unknown rarity: ${record.id}`);
  if (!record.images.card.startsWith('/images/')) throw new Error(`Invalid card path: ${record.id}`);
  for (const value of [record.number, record.total, ...statKeys.map(stat => record.stats[stat])]) {
    if (!Number.isInteger(value) || value < 0) throw new Error(`Invalid statistic: ${record.id}`);
  }
  ids.add(record.id);
  slugs.add(record.slug);
  return record as Horse;
});
export const collection = { total: source.collection.totalHorses, edition: 'base' };
export const featuredHorses = horses.filter(horse => horse.rarity !== 'normal');
export const battleHorses = featuredHorses.slice(0, 2);
export const orderedHorses = [...horses].sort((a, b) => a.edition.localeCompare(b.edition) || a.number - b.number || a.id.localeCompare(b.id));
