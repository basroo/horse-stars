export const site = {
  email: 'info@playhorsestars.com',
  website: 'https://playhorsestars.com',
  // Set verified destinations here; unset links are presented as upcoming.
  youtube: null as string | null,
  instagram: null as string | null,
};

export const featuredVideo = {
  youtubeId: null as string | null,
  // Replace with a commissioned 1920 × 1080 episode thumbnail.
  poster: '/images/video/horse-stars-news-placeholder.webp',
};

export interface Retailer {
  id: string;
  name: string;
  country: string; // ISO 3166-1 alpha-2, for future country filtering.
  city: string;
  url?: string;
}
export const retailers: Retailer[] = [];

export const championEdition = {
  id: 'champion',
  total: 20,
  cards: [
    { image: '/images/specials/champion-silver.png', finish: 'silver' },
    { image: '/images/specials/champion-gold.png', finish: 'gold' },
    { image: '/images/specials/champion-bronze.png', finish: 'bronze' },
  ],
};
