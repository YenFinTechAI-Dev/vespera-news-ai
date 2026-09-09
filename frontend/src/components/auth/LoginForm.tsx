"use client";


import { SocialLogin } from "./SocialLogin";
import { T } from "@/components/ui/Language";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError("Enter your email and password to continue.");
      return;
    }

    setSubmitting(true);
    try {
      const response=await fetch('/api/account/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})});
      const data=await response.json();
      if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Thông tin tài khoản không hợp lệ.');
      router.push("/news");
    } catch (e) {
      setError(e instanceof Error?e.message:"Không thể đăng nhập.");
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink"><T>{"Welcome back"}</T></h1>
        <p className="mt-1.5 text-sm text-ink-muted"><T>{"Log in to your VesperSignal workspace."}</T></p>
      </div>

      <SocialLogin />

      {error ? (
        <p className="rounded-lg border border-risk-critical/30 bg-risk-critical/10 px-3.5 py-2.5 text-sm text-risk-critical">
          <T>{error}</T>
        </p>
      ) : null}

      <Input
        label="Work email"
        type="email"
        autoComplete="email"
        placeholder="you@company.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <div>
        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <div className="mt-2 flex justify-end">
          <span className="text-xs text-ink-muted">Bản local chưa hỗ trợ khôi phục mật khẩu qua email.</span>
        </div>
      </div>

      <Button type="submit" disabled={submitting} className="w-full">
        <T>{submitting ? "Logging in…" : "Log in"}</T>
      </Button>

      <p className="text-center text-sm text-ink-muted"><T>{" Don't have a workspace?"}</T><T>{" "}</T>
        <a href="/register" className="text-ink transition-colors hover:text-brand"><T>{" Create an account "}</T></a>
      </p>
    </form>
  );
}
