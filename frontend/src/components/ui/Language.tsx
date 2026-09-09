"use client";
import { createContext, useContext, useEffect, useState, ReactNode, Children } from "react";
import { vi } from "@/lib/translations";
type Locale = "vi" | "en";
const Context = createContext({ locale: "vi" as Locale, setLocale: (_: Locale) => {} });
export function LanguageProvider({children}: {children: ReactNode}) {
 const [locale, setLocale] = useState<Locale>("vi");
 useEffect(() => { try { const saved = localStorage.getItem("sentinel-language"); if(saved === "en" || saved === "vi") setLocale(saved); } catch {} }, []);
 useEffect(() => { document.documentElement.lang = locale; }, [locale]);
 useEffect(()=>{const sync=(event:StorageEvent)=>{if(event.key==='sentinel-language'&&(event.newValue==='vi'||event.newValue==='en'))setLocale(event.newValue)};window.addEventListener('storage',sync);return()=>window.removeEventListener('storage',sync)},[]);
 const change = (value: Locale) => { setLocale(value); try { localStorage.setItem("sentinel-language", value); } catch {} };
 return <Context.Provider value={{locale, setLocale: change}}>{children}</Context.Provider>;
}
export function useTranslation() {
 const {locale} = useContext(Context);
 return (text: string) => {
  if(locale === "en") return text;
  const key = text.trim().replace(/\s+/g, " ");
  if(key.startsWith("· Assigned to ")) return text.replace("Assigned to", "Phân công cho");
  const result = vi[key] ?? vi[text];
  return result === undefined ? text : text.replace(text.trim(), result);
 };
}
export function T({children}: {children: ReactNode}) {
 const t = useTranslation();
 return <>{Children.map(children, child => typeof child === "string" ? t(child) : child)}</>;
}
export function LanguageSwitch({compact: _compact = false}: {compact?: boolean} = {}) {
 const {locale, setLocale} = useContext(Context);
 return <div role="group" aria-label="Ngôn ngữ / Language" className="inline-flex shrink-0 rounded-lg border border-stroke p-1 text-xs">
 {(["vi", "en"] as const).map(value => <button key={value} type="button" lang={value} aria-label={value === "vi" ? "Tiếng Việt" : "English"} aria-pressed={locale === value} onClick={() => setLocale(value)} className={"rounded px-2 py-1.5 font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand " + (locale === value ? "bg-brand text-base" : "text-ink-muted hover:text-ink")}>{value.toUpperCase()}</button>)}
 </div>;
}

export function LocalizedDate({iso}: {iso: string}) {
 const {locale} = useContext(Context);
 return <>{new Intl.DateTimeFormat(locale === "vi" ? "vi-VN" : "en-US", {month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit", timeZone: "Asia/Ho_Chi_Minh"}).format(new Date(iso))}</>;
}

export function useLocale(){return useContext(Context).locale;}
