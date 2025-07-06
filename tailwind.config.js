/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",  // 🗂️ Scan all your Jinja templates!
    "./static/js/**/*.js"     // If you use Tailwind classes in JS
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}