/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sage: {
          green: '#B2AC88', // Sage green
          dark: '#065F46', // Dark green for text (emerald-900)
          light: '#ECFDF5', // Very light green (emerald-50)
        },
      },
    },
  },
  plugins: [],
}

