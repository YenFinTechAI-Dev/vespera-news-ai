import { LanguageSwitch } from "@/components/ui/Language";

import { T } from "@/components/ui/Language";
import { ReactNode } from "react";
import Link from "next/link";
import { Logo } from "@/components/ui/Logo";

export function AuthShell({
  children,
  panelTitle,
  panelBody,
}: {
  children: ReactNode;
  panelTitle: string;
  panelBody: string;
}) {
  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <div className="relative hidden flex-col justify-between overflow-hidden border-r border-stroke bg-surface p-10 bg-grid-fade md:flex">
        <Link href="/">
          <Logo />
        </Link>
        <div className="max-w-sm">
          <p className="font-mono text-xs text-brand"><T>{"verdict · 12ms"}</T></p>
          <h2 className="mt-3 font-display text-2xl font-semibold leading-snug text-ink">
            <T>{panelTitle}</T>
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-ink-muted"><T>{panelBody}</T></p>
        </div>
        <p className="text-xs text-ink-faint"><T>{"VesperSignal · Local demo"}</T></p>
      </div>

      <div className="flex items-center justify-center px-6 py-16">
        <div className="w-full max-w-sm">
          <Link href="/" className="mb-10 flex md:hidden">
            <Logo />
          </Link>
          <div className="mb-6 flex justify-end"><LanguageSwitch /></div><T>{children}</T>
        </div>
      </div>
    </div>
  );
}
