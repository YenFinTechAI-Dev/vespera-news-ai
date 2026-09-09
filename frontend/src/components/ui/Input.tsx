"use client";

import { T, useTranslation } from "@/components/ui/Language";
import { InputHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, hint, id, className, ...props }, ref) => {
    const translate = useTranslation();
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");
    return (
      <div className="flex flex-col gap-1.5">
        <label htmlFor={inputId} className="text-sm font-medium text-ink-muted">
          <T>{label}</T>
        </label>
        <input
          id={inputId}
          ref={ref}
          className={cn(
            "rounded-lg border border-stroke bg-surface-2 px-3.5 py-2.5 text-sm text-ink placeholder:text-ink-faint outline-none transition-colors focus:border-brand/60",
            className
          )}
          {...props}
          placeholder={props.placeholder ? translate(props.placeholder) : undefined}
        />
        {hint ? <p className="text-xs text-ink-faint"><T>{hint}</T></p> : null}
      </div>
    );
  }
);
Input.displayName = "Input";
