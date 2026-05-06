/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#09111f",
        panel: "#101b2d",
        accent: "#f59e0b",
        mint: "#6ee7b7",
        skyline: "#8ec5ff"
      },
      fontFamily: {
        sans: ["'Segoe UI'", "system-ui", "sans-serif"]
      },
      boxShadow: {
        soft: "0 20px 60px rgba(8, 15, 30, 0.45)"
      }
    }
  },
  plugins: []
}
