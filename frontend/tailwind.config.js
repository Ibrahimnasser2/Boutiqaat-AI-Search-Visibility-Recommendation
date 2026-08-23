/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f0ff',
          100: '#ede5ff',
          500: '#7c3aed',
          600: '#6c3fc5',
          700: '#5b21b6',
        },
      },
    },
  },
  plugins: [],
}
