/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        mufg: {
          red: "#ED1B24",
          darkred: "#C2131B",
          gray: "#2B2B2B",
          lightgray: "#F4F6F8"
        }
      }
    },
  },
  plugins: [],
};
