/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-slow2': 'pulse 5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      backgroundImage: {
        'grid-green-400/10': 'linear-gradient(rgba(74, 222, 128, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(74, 222, 128, 0.1) 1px, transparent 1px)',
      },
    },
  },
  plugins: [],
} 