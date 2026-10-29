import type { ImageMetadata } from 'astro';
// Discover new local artwork automatically; JSON paths remain the source of truth.
const assets = import.meta.glob<{ default: ImageMetadata }>(
  '../../public/images/**/*.{png,jpg,jpeg,webp,avif}', { eager: true },
);
export const cardImages: Record<string, ImageMetadata> = Object.fromEntries(
  Object.entries(assets).map(([path, asset]) => [path.replace('../../public', ''), asset.default]),
);
