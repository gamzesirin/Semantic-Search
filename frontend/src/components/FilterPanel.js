import React from 'react';

function FilterPanel({ method, setMethod, topK, setTopK, threshold, setThreshold, category, setCategory, categories }) {
  return (
    <div className="filter-panel">
      <div className="filter-group">
        <label>Yontem</label>
        <select value={method} onChange={(e) => setMethod(e.target.value)}>
          <option value="hybrid">Hibrit</option>
          <option value="bm25">BM25</option>
          <option value="vector">Vektor</option>
          <option value="chroma">ChromaDB</option>
        </select>
      </div>

      <div className="filter-group">
        <label>Kategori</label>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="all">Tumu</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Sonuc: {topK}</label>
        <input type="range" min="5" max="30" value={topK} onChange={(e) => setTopK(parseInt(e.target.value))} />
      </div>

      <div className="filter-group">
        <label>Esik: {threshold.toFixed(2)}</label>
        <input type="range" min="0" max="0.9" step="0.05" value={threshold}
               onChange={(e) => setThreshold(parseFloat(e.target.value))} />
      </div>
    </div>
  );
}

export default FilterPanel;
