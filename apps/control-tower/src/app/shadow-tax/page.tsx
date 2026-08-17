const officialSources = [
  { label: "Portal da Reforma Tributária", href: "https://www.gov.br/fazenda/pt-br/acesso-a-informacao/acoes-e-programas/reforma-tributaria" },
];
export default function ShadowTaxPage() {
  return <main aria-labelledby="title">
    <h1 id="title">Shadow Tax e conciliação</h1>
    <p>Fila tenant-scoped de divergências entre documento fiscal, ERP, pagamento, split e simulação tributária.</p>
    <section aria-labelledby="queue"><h2 id="queue">Revisão humana</h2>
      <p>Casos críticos permanecem pendentes até decisão autorizada com justificativa e evidência.</p></section>
    <section aria-labelledby="sources"><h2 id="sources">Fontes oficiais</h2><ul>
      {officialSources.map(source => <li key={source.href}><a href={source.href} rel="noreferrer">{source.label}</a></li>)}
    </ul></section>
  </main>;
}
