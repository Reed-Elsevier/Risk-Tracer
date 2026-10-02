import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#000000",
        paper: "#ffffff",
        mist: "#f5f5f5",
        moss: "#f48529",
        ember: "#f48529",
        gold: "#000000"
      },
      boxShadow: {
        card: "0 14px 40px rgba(0, 0, 0, 0.08)"
      },
      fontFamily: {
        sans: ["var(--font-plex-sans)", "Segoe UI", "sans-serif"],
        mono: ["var(--font-plex-mono)", "ui-monospace", "monospace"]
      }
    }
  },
  plugins: []
};

export default config;
