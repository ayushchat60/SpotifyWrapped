/**
 * TailwindCSS Configuration
 *
 * This configuration file customizes the TailwindCSS framework for the project.
 * It defines the content paths to scan for class names, extends the default theme,
 * and optionally includes plugins for additional functionality.
 *
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
