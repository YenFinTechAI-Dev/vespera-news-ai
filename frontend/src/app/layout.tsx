import { LanguageProvider } from "@/components/ui/Language";
import type { Metadata } from "next";

// Self-hosted via @fontsource so the build never depends on fetching
// fonts.googleapis.com at build or request time.
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/space-grotesk/500.css";
import "@fontsource/space-grotesk/600.css";
import "@fontsource/space-grotesk/700.css";
import "@fontsource/jetbrains-mono/400.css";
import "@fontsource/jetbrains-mono/500.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "VesperSignal News",
  description:
    "News discovery, source-based AI summaries and research notes.",
};

// Runs before React hydrates, so the correct theme is set on <html> before
// first paint (no light->dark flash). Stored choice wins; otherwise we
// follow the OS preference. Kept tiny and dependency-free on purpose.
const THEME_INIT_SCRIPT = `(function(){try{
  var stored = localStorage.getItem('theme');
  var theme = stored === 'light' || stored === 'dark'
    ? stored
    : (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  document.documentElement.setAttribute('data-theme', theme);
}catch(e){}})();`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="font-sans bg-base text-ink antialiased" suppressHydrationWarning>
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
