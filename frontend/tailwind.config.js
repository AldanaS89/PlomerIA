/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#eef6ff',
          100: '#d9eaff',
          200: '#bcd8ff',
          300: '#8ebdff',
          400: '#5a97f8',
          500: '#3574ee',
          600: '#2457e3',
          700: '#1c43d0',
          800: '#1d38a8',
          900: '#1c3285',
          950: '#151f52',
        },
        navy: '#0f1b35',
        emerald: {
          500: '#10b981',
          600: '#059669',
        },
      },
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        display: ['Sora', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
