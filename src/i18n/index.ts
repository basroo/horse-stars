import en from './en.json';
import cs from './cs.json';
export const languages = { en, cs };
export type Locale = keyof typeof languages;
export type Copy = typeof en;
export function getCopy(locale: Locale = 'en'): Copy { return languages[locale]; }
export function breedLabel(breed: string, copy: Copy): string {
  const key = breed.toLowerCase().replaceAll(' ', '') as keyof Copy['breeds'];
  return copy.breeds[key] ?? breed;
}
export function editionLabel(edition: string, copy: Copy): string {
  return copy.editions[edition as keyof Copy['editions']] ?? edition;
}
