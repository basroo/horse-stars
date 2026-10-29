import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://playhorsestars.com',
  output: 'static',
  vite: { plugins: [tailwindcss()] },
  image: { responsiveStyles: true },
});
