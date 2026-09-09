"use client";


import { T } from "@/components/ui/Language";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export function RegisterForm() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [company, setCompany] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!fullName || !email || !password) {
      setError("Fill in your name, email, and a password to continue.");
      return;
    }
    if (password.length < 8) {
      setError("Password needs to be at least 8 characters.");
      return;
    }

    setSubmitting(true);
    try {
      const response=await fetch('/api/account/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password,name:fullName})});
      const data=await response.json();
      if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Thông tin tài khoản không hợp lệ.');
      router.push("/news");
    } catch (e) {
      setError(e instanceof Error?e.message:"Không thể tạo tài khoản.");
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink"><T>{"Create your account"}</T></h1>
        <p className="mt-1.5 text-sm text-ink-muted"><T>{" Tạo tài khoản để lưu hội thoại và sử dụng 50 lượt AI mỗi ngày. "}</T></p>
      </div>

      {error ? (
        <p className="rounded-lg border border-risk-critical/30 bg-risk-critical/10 px-3.5 py-2.5 text-sm text-risk-critical">
          <T>{error}</T>
        </p>
      ) : null}

      <Input
        label="Full name"
        autoComplete="name"
        placeholder="Nguyen Van A"
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
      />
      <Input
        label="Company"
        autoComplete="organization"
        placeholder="Acme Payments"
        value={company}
        onChange={(e) => setCompany(e.target.value)}
      />
      <Input
        label="Work email"
        type="email"
        autoComplete="email"
        placeholder="you@company.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Input
        label="Password"
        type="password"
        autoComplete="new-password"
        placeholder="At least 8 characters"
        hint="Tối thiểu 8 ký tự. Nên dùng mật khẩu riêng cho tài khoản này."
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <Button type="submit" disabled={submitting} className="w-full">
        <T>{submitting ? "Creating account…" : "Create free account"}</T>
      </Button>

      <p className="text-center text-sm text-ink-muted"><T>{" Already have a workspace?"}</T><T>{" "}</T>
        <a href="/login" className="text-ink transition-colors hover:text-brand"><T>{" Log in "}</T></a>
      </p>
    </form>
  );
}
