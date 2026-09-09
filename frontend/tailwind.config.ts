import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // These resolve via CSS custom properties defined per [data-theme]
        // in globals.css, so bg-base/text-ink/etc. work in both themes.
        base: "var(--color-base)",
        surface: {
          DEFAULT: "var(--color-surface)",
          2: "var(--color-surface-2)",
          3: "var(--color-surface-3)",
        },
        stroke: "var(--color-stroke)",
        ink: {
          DEFAULT: "var(--color-ink)",
          muted: "var(--color-ink-muted)",
          faint: "var(--color-ink-faint)",
        },
        brand: {
          DEFAULT: "#00D9A3",
          dim: "#0BA57E",
          soft: "#0B2E27",
        },
        risk: {
          low: "#00D9A3",
          medium: "#FFB020",
          high: "#FF5C6C",
          critical: "#FF3B4E",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        sans: ["Inter", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      backgroundImage: {
        "grid-fade":
          "radial-gradient(circle at 20% 0%, rgba(0,217,163,0.12), transparent 45%)",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(0,217,163,0.25), 0 0 32px rgba(0,217,163,0.12)",
      },
      borderRadius: {
        xl: "0.875rem",
      },
      keyframes: {
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" },
        },
        rise: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        blink: "blink 1s step-start infinite",
        rise: "rise 0.5s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
