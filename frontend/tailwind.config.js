/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        sentinel: {
          bg: '#0b1220',
          panel: '#111a2e',
          border: '#1f2b45',
          accent: '#38bdf8',
        },
      },
    },
  },
  plugins: [],
}
