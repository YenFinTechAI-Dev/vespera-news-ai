"use client";
import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

type Theme = "dark" | "light";

// Reads the theme the inline script in layout.tsx already applied to <html>,
// so there's no flash and no mismatch between server/client render.
function readInitialTheme(): Theme {
  if (typeof document === "undefined") return "dark";
  const attr = document.documentElement.getAttribute("data-theme");
  return attr === "light" ? "light" : "dark";
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("dark");

  useEffect(() => {
    setTheme(readInitialTheme());
  }, []);

  const apply = (value: Theme) => {
    setTheme(value);
    document.documentElement.setAttribute("data-theme", value);
    try {
      localStorage.setItem("theme", value);
    } catch {
      // Storage can be unavailable (private mode, etc.) — theme still
      // applies for this page view, it just won't persist.
    }
  };

  return (
    <div
      role="group"
      aria-label="Giao diện sáng / tối"
      className="inline-flex shrink-0 rounded-lg border border-stroke p-1 text-xs"
    >
      {([
        { value: "dark" as const, label: "Tối", Icon: Moon },
        { value: "light" as const, label: "Sáng", Icon: Sun },
      ]).map(({ value, label, Icon }) => (
        <button
          key={value}
          type="button"
          aria-label={label}
          aria-pressed={theme === value}
          onClick={() => apply(value)}
          className={
            "flex items-center justify-center rounded px-2 py-1.5 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand " +
            (theme === value ? "bg-brand text-base" : "text-ink-muted hover:text-ink")
          }
        >
          <Icon size={14} strokeWidth={2} />
        </button>
      ))}
    </div>
  );
}
