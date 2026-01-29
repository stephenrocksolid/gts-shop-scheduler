/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./rental_scheduler/templates/**/*.html",
        "./rental_scheduler/static/rental_scheduler/js/**/*.js",
        "!./rental_scheduler/static/rental_scheduler/js/**/*.min.js",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#1e40af',
                'primary-dark': '#1e3a8a',
                secondary: '#475569',
            }
        },
    },
    plugins: [],
}
