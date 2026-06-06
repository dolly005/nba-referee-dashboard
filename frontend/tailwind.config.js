/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: '#07111f',
        panel: '#0f1b2d',
        panel2: '#13233a',
        nbaRed: '#c9082a',
        nbaBlue: '#17408b'
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(255,255,255,0.08), 0 18px 50px rgba(0,0,0,0.35)'
      }
    }
  },
  plugins: []
}
