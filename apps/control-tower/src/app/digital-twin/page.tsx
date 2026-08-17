const stresses = [
  ["Receita -10%", "-R$ 42 mil"], ["Recebíveis +15 dias", "-R$ 31 mil"],
  ["Custos +8%", "-R$ 28 mil"], ["Pagamentos -10 dias", "-R$ 19 mil"],
  ["Split +5%", "-R$ 14 mil"], ["Juros +200 bps", "-R$ 8 mil"],
] as const;

export default function DigitalTwinPage() {
  return <>
    <p style={{ color: "#52717a", marginBottom: 4 }}>Projeção determinística · Horizonte de 90 dias</p>
    <h1 style={{ marginTop: 0 }}>Digital Twin financeiro</h1>
    <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))", gap: 16 }}>
      {[['Saldo mínimo', 'R$ 118 mil'], ['Maior gap', 'R$ 0'], ['Float tributário', '-R$ 24 mil'], ['Dias abaixo do piso', '0']].map(([label, value]) =>
        <article key={label} style={{ background: "white", borderRadius: 12, padding: 20 }}><span>{label}</span><strong style={{ display: "block", fontSize: 28 }}>{value}</strong></article>)}
    </section>
    <section style={{ background: "white", borderRadius: 12, padding: 20, marginTop: 18 }}>
      <h2>Curva diária de caixa</h2>
      <div role="img" aria-label="Curva de caixa positiva com redução gradual pelo split tributário" style={{ height: 180, background: "linear-gradient(170deg,transparent 49%,#06a77d 50%,transparent 51%),linear-gradient(#edf5f3 1px,transparent 1px)", backgroundSize: "100% 100%,100% 36px" }} />
      <small>Modo: baseline determinístico · Premissas 1.0.0</small>
    </section>
    <section style={{ background: "white", borderRadius: 12, padding: 20, marginTop: 18 }}><h2>Stress tests independentes</h2>
      <ul>{stresses.map(([name, impact]) => <li key={name} style={{ margin: "8px 0" }}>{name}: <strong>{impact}</strong></li>)}</ul>
      <p>Fontes tributárias herdadas da simulação publicada: <a href="https://www.gov.br/receitafederal/" rel="noreferrer">Receita Federal</a>.</p>
    </section>
  </>;
}
