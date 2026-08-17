type Metric = Readonly<{ label: string; value: string; detail: string }>;

const metrics: Metric[] = [
  { label: "Tax Readiness Score", value: "91,8", detail: "Pronto · 66 evidências" },
  { label: "Impacto CBS/IBS", value: "+5,0%", detail: "Cenário de transição" },
  { label: "Capital de giro", value: "-R$ 6.250", detail: "Projeção em 12 meses" },
  { label: "Conciliação", value: "99,94%", detail: "3 divergências abertas" },
];

export default function DashboardPage() {
  return (
    <>
      <p style={{ color: "#52717a", marginBottom: ".25rem" }}>Empresa sintética · Atualizado agora</p>
      <h1 style={{ marginTop: 0 }}>Visão executiva</h1>
      <section aria-label="Indicadores" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: "1rem" }}>
        {metrics.map((metric) => (
          <article key={metric.label} style={{ background: "white", borderRadius: 12, padding: "1.25rem", boxShadow: "0 2px 10px #15343e12" }}>
            <div style={{ color: "#52717a" }}>{metric.label}</div>
            <strong style={{ display: "block", fontSize: "1.8rem", margin: ".5rem 0" }}>{metric.value}</strong>
            <small>{metric.detail}</small>
          </article>
        ))}
      </section>
      <section style={{ background: "white", borderRadius: 12, padding: "1.25rem", marginTop: "1rem" }}>
        <h2>Prioridades</h2>
        <ol>
          <li>Revisar regras sem evidência legal vinculada.</li>
          <li>Tratar divergências entre documento fiscal e liquidação.</li>
          <li>Validar o cenário de split payment com Tesouraria.</li>
        </ol>
      </section>
    </>
  );
}

