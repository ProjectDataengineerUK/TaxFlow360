const dimensions = [
  ["Fiscal", 88], ["Financeiro", 86], ["ERP e integrações", 94], ["Cadastro", 91],
  ["Meios de pagamento", 90], ["Conciliação", 96], ["Split readiness", 84], ["Capital de giro", 93],
] as const;

export default function ReadinessPage() {
  return <>
    <p style={{ color: "#52717a", marginBottom: 4 }}>Diagnóstico publicado · Metodologia 1.0.0</p>
    <h1 style={{ marginTop: 0 }}>Tax Readiness</h1>
    <section style={{ display: "grid", gridTemplateColumns: "220px 1fr", gap: 24 }}>
      <article style={{ background: "#073b4c", color: "white", borderRadius: 16, padding: 24 }}>
        <span>Score geral</span><strong style={{ display: "block", fontSize: 56 }}>90,4</strong><span>Pronto</span>
      </article>
      <article style={{ background: "white", borderRadius: 16, padding: 24 }}>
        <h2 style={{ marginTop: 0 }}>Oito dimensões</h2>
        {dimensions.map(([name, score]) => <div key={name} style={{ display: "grid", gridTemplateColumns: "150px 1fr 40px", gap: 12, margin: "10px 0" }}>
          <span>{name}</span><progress value={score} max="100" aria-label={`${name}: ${score}`} /><strong>{score}</strong>
        </div>)}
      </article>
    </section>
    <section style={{ background: "white", borderRadius: 16, padding: 24, marginTop: 24 }}>
      <h2>Ações prioritárias</h2>
      <ol><li>Vincular evidências legais às regras pendentes.</li><li>Completar a conciliação de pagamentos.</li><li>Revisar papéis de aprovação da metodologia.</li></ol>
    </section>
  </>;
}
