/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        spotifyGreen: "#1DB954",
        spotifyDark: "#121212",
        spotifyBlack: "#191414",
        spotifyWhite: "#FFFFFF",
        spotifyLight: "#FAF9F6",
      },
    },
  },
  plugins: [],
};
