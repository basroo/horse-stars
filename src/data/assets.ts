import type { ImageMetadata } from 'astro';
import source from './horses.json';

// Only card paths declared by horses.json are eligible for Astro processing.
// The non-recursive glob avoids PDFs, reports, _unmatched/, and unrelated assets.
const assets = import.meta.glob<{ default: ImageMetadata }>(
  '../../public/images/cards/*.webp', { eager: true },
);
const expectedCardPaths = new Set(source.horses.map(horse => horse.images.card));
export const cardImages: Record<string, ImageMetadata> = Object.fromEntries(
  Object.entries(assets)
    .map(([path, asset]) => [path.replace('../../public', ''), asset.default] as const)
    .filter(([path]) => expectedCardPaths.has(path)),
);
