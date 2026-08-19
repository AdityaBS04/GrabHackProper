/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        /* shadcn token surface, resolved from the CSS variables in index.css. */
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",

        /* The desk: a cool drafting surface. Panels sit on it, paper sits above. */
        desk: {
          DEFAULT: "#DFE5EC",
          deep: "#D5DDE5",
        },
        panel: "#EDF1F6",
        raised: "#F6F9FB",
        sunken: "#D9E0E8",
        line: {
          DEFAULT: "#CBD5DF",
          soft: "#DCE3EA",
          strong: "#B3C1CE",
        },

        /* Type */
        ink: "#14202C",
        muted: "#4F6070",
        faint: "#55636F",

        /* Records: warm stock, the brightest thing on the desk. */
        parchment: {
          DEFAULT: "#FAF5EA",
          deep: "#F0E8D6",
          edge: "#DCCFB6",
          ink: "#2A2519",
          dim: "#6E6349",
        },

        /* Signals, borrowed from transit lighting. */
        amber: {
          DEFAULT: "#E9A13B",
          bright: "#F2B457",
          deep: "#8A5407",
          wash: "#FDF3E3",
        },
        jade: {
          DEFAULT: "#26705B",
          wash: "#D6E7E0",
        },
        clay: {
          DEFAULT: "#A34526",
          wash: "#F3DDD3",
        },
      },
      fontFamily: {
        display: ["Archivo", "system-ui", "sans-serif"],
        sans: ["'Instrument Sans'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        tightest: "-0.045em",
        signage: "0.18em",
      },
      borderRadius: {
        card: "3px",
      },
      boxShadow: {
        panel: "0 1px 2px rgba(20,32,44,0.05)",
        paper:
          "0 1px 1px rgba(20,32,44,0.04), 0 10px 24px -14px rgba(20,32,44,0.28)",
        lifted: "0 18px 40px -22px rgba(20,32,44,0.45)",
      },
      keyframes: {
        "trace-sweep": {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(320%)" },
        },
        "rise-in": {
          from: { opacity: "0", transform: "translateY(6px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        blink: { "0%,100%": { opacity: "1" }, "50%": { opacity: "0.25" } },
      },
      animation: {
        "trace-sweep": "trace-sweep 1.5s ease-in-out infinite",
        "rise-in": "rise-in 0.4s cubic-bezier(0.16,1,0.3,1) both",
        blink: "blink 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
