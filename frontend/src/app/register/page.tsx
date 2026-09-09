import type { Metadata } from "next";
import { AuthShell } from "@/components/layout/AuthShell";
import { RegisterForm } from "@/components/auth/RegisterForm";

export const metadata: Metadata = {
  title: "Create account · VesperSignal",
};

export default function RegisterPage() {
  return (
    <AuthShell
      panelTitle="Live in your stack within a day."
      panelBody="Drop in one API call, send us your first batch of transactions, and start seeing risk scores immediately."
    >
      <RegisterForm />
    </AuthShell>
  );
}
