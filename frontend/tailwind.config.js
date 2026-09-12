/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0b1220",
          900: "#0f172a",
          800: "#1e293b",
          700: "#334155",
          600: "#475569",
          400: "#94a3b8",
          200: "#e2e8f0",
          100: "#f1f5f9",
          50: "#f8fafc",
        },
        brand: {
          700: "#0e5f5a",
          600: "#137a73",
          500: "#18948b",
          400: "#3fb0a7",
        },
        risk: {
          critical: "#b91c1c",
          high: "#c2410c",
          moderate: "#b45309",
          low: "#15803d",
        },
      },
      fontFamily: {
        sans: ["Inter", "Segoe UI", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
