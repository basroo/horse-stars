import type { Locale } from './index';
export function localizedPath(path: string, locale: Locale): string {
  return locale === 'en' ? path : `/cs${path}`;
}
export function alternatePath(path: string, locale: Locale): string {
  return localizedPath(path.replace(/^\/cs(?=\/|$)/, '') || '/', locale);
}
