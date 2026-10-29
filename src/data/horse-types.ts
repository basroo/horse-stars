export const statKeys = ['speed', 'power', 'jump', 'brains'] as const;
export type Stat = typeof statKeys[number];
export type Rarity = 'standard' | 'elite' | 'epic' | 'legend';
export interface Horse {
  id: string;
  number: number;
  name: string;
  slug: string;
  breed: string;
  edition: string;
  rarity: Rarity;
  stats: Record<Stat, number>;
  total: number;
  title?: string;
  tagline?: string;
  images: { card: string; hero?: string };
  featured?: boolean;
  battleDemo?: boolean;
  bonus?: { stat: Stat; amount: number };
}
