import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClearFinance — Begrijp je documenten",
  description: "Een begrijpelijke documentanalyse met interactieve bronverwijzingen.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="nl"><body>{children}</body></html>;
}
