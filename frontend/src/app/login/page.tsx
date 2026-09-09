import type { Metadata } from "next";
import { AuthShell } from "@/components/layout/AuthShell";
import { LoginForm } from "@/components/auth/LoginForm";

export const metadata: Metadata = {
  title: "Log in · VesperSignal",
};

export default function LoginPage() {
  return (
    <AuthShell
      panelTitle="Every decision, explained."
      panelBody="VesperSignal shows the exact signals behind every score, so your team never has to guess why a transaction was flagged."
    >
      <LoginForm />
    </AuthShell>
  );
}
