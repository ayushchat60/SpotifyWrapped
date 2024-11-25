/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        spotifyGreen: "#1DB954",
        spotifyDark: "#121212",
        spotifyBlack: "#191414",
      },
    },
  },
  plugins: [],
};
