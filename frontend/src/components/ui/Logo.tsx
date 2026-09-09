
import { T } from "@/components/ui/Language";
import { cn } from "@/lib/utils";

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2 font-display font-semibold", className)}>
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true">
        <path
          d="M11 1.5 19.5 5v5.4c0 5.1-3.5 8.6-8.5 10.1-5-1.5-8.5-5-8.5-10.1V5L11 1.5Z"
          stroke="#00D9A3"
          strokeWidth="1.4"
          strokeLinejoin="round"
        />
        <path
          d="M7.5 11.2 9.8 13.5 14.6 8.3"
          stroke="#00D9A3"
          strokeWidth="1.4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg><T>{" VesperSignal "}</T></span>
  );
}
