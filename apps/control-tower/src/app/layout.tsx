import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "TaxFlow 360 Control Tower",
  description: "Visão tributária, financeira e operacional por tenant",
};

const navigation = ["Visão geral", "Readiness", "Simulador", "Digital Twin", "Shadow Tax"];

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", background: "#f4f7f8", color: "#17333b" }}>
        <header style={{ padding: "1rem 2rem", background: "#073b4c", color: "white", display: "flex", justifyContent: "space-between" }}>
          <strong>TaxFlow 360</strong><span>Control Tower · Empresa</span>
        </header>
        <div style={{ display: "grid", gridTemplateColumns: "220px 1fr", minHeight: "calc(100vh - 56px)" }}>
          <nav aria-label="Navegação principal" style={{ padding: "1.5rem", background: "white" }}>
            {navigation.map((item) => <div key={item} style={{ padding: ".65rem 0" }}>{item}</div>)}
          </nav>
          <main style={{ padding: "2rem", maxWidth: 1200 }}>{children}</main>
        </div>
      </body>
    </html>
  );
}

