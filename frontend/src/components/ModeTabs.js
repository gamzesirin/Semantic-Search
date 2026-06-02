import React from 'react';

const TABS = [
  { key: 'ask', label: 'Soru Sor', desc: 'Dokümanlara dayalı yapay zeka cevabı' },
  { key: 'search', label: 'Arama', desc: 'İlgili dokümanları bul' },
  { key: 'compare', label: 'Karşılaştır', desc: 'BM25 / Vektör / Hibrit analizi' },
];

function ModeTabs({ active, onChange }) {
  return (
    <div className="mode-tabs">
      {TABS.map((t) => (
        <button
          key={t.key}
          className={`mode-tab ${active === t.key ? 'active' : ''}`}
          onClick={() => onChange(t.key)}
        >
          <span className="mode-tab-label">{t.label}</span>
          <span className="mode-tab-desc">{t.desc}</span>
        </button>
      ))}
    </div>
  );
}

export default ModeTabs;
