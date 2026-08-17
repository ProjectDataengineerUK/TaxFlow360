type Source = { sourceId: string; url: string; authority: string; document: string; provision: string };
type Scenario = { name: string; total: string; split: string; delta: string; rules: readonly string[]; sources: readonly Source[] };

const officialSource: Source = {
  sourceId: "ec132-2023-art156a",
  url: "https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc132.htm",
  authority: "Presidência da República",
  document: "EC 132/2023",
  provision: "art. 156-A",
};

const scenarios: readonly Scenario[] = [
  { name: "Regime atual", total: "R$ 18.000,00", split: "R$ 0,00", delta: "—", rules: ["current-general-2026"], sources: [officialSource] },
  { name: "CBS/IBS", total: "R$ 26.500,00", split: "R$ 0,00", delta: "+ R$ 8.500,00", rules: ["cbs-general-2027", "ibs-general-2027"], sources: [officialSource] },
  { name: "Split payment", total: "R$ 26.500,00", split: "R$ 26.500,00", delta: "+ R$ 8.500,00", rules: ["split-cbs-general-2027", "split-ibs-general-2027"], sources: [officialSource] },
];

export default function SimulatorPage() {
  return <main>
    <p style={{ color: "#52717a", marginBottom: 4 }}>Snapshot sintético 1.0.0 · cálculo HALF_EVEN</p>
    <h1 style={{ marginTop: 0 }}>Simulador CBS/IBS e split payment</h1>
    <p>Compare cenários reproduzíveis. Esta demonstração não constitui orientação tributária.</p>
    <section aria-label="Comparação tributária" style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(220px, 1fr))", gap: 16 }}>
      {scenarios.map((scenario) => <article key={scenario.name} style={{ background: "white", borderRadius: 16, padding: 20 }}>
        <h2>{scenario.name}</h2>
        <strong style={{ display: "block", fontSize: 30 }}>{scenario.total}</strong>
        <p>Variação: {scenario.delta}<br />Retenção simulada: {scenario.split}</p>
        <details><summary>Memória de cálculo</summary><ul>{scenario.rules.map((rule) => <li key={rule}><code>{rule}</code></li>)}</ul></details>
        <h3>Fontes oficiais</h3>
        <ul>{scenario.sources.map((source) => <li key={source.sourceId}>
          <a href={source.url} target="_blank" rel="noopener noreferrer">{source.document}, {source.provision}</a>
          <small style={{ display: "block" }}>{source.authority}</small>
        </li>)}</ul>
      </article>)}
    </section>
  </main>;
}
