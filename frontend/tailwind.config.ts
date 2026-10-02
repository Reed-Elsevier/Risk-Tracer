import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#15221f",
        paper: "#f7f5ef",
        mist: "#e8ebe4",
        moss: "#1f6a50",
        ember: "#c35636",
        gold: "#bb8b2c"
      },
      boxShadow: {
        card: "0 14px 40px rgba(21, 34, 31, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
