export const statKeys = ['speed', 'power', 'jump', 'brains'] as const;
export type Stat = typeof statKeys[number];
export type Rarity = 'normal' | 'elite' | 'epic' | 'legend';
export interface HorseStory {
  title: string;
  hook: string;
  raw: string;
}
export interface Horse {
  id: string;
  number: number;
  name: string;
  slug: string;
  breed: string;
  edition: string;
  rarity: Rarity;
  isFoal: boolean;
  stats: Record<Stat, number>;
  total: number;
  story: HorseStory | null;
  images: { card: string; hero?: string | null };
}
