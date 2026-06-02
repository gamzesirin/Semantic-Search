import React from 'react';

function FilterPanel({ mode, method, setMethod, topK, setTopK, threshold, setThreshold, category, setCategory, categories }) {
  return (
    <div className="filter-panel">
      {/* Arama yöntemi yalnızca "Arama" modunda anlamlı (Soru Sor ve Karşılaştır sabit yöntem kullanır) */}
      {mode === 'search' && (
        <div className="filter-group">
          <label>Yontem</label>
          <select value={method} onChange={(e) => setMethod(e.target.value)}>
            <option value="hybrid">Hibrit</option>
            <option value="bm25">BM25 (Sozcuksel)</option>
            <option value="vector">Vektor (Anlamsal)</option>
            <option value="chroma">ChromaDB</option>
          </select>
        </div>
      )}

      <div className="filter-group">
        <label>Kategori</label>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="all">Tumu</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>{mode === 'ask' ? 'Kaynak sayisi' : 'Sonuc sayisi'}: {topK}</label>
        <input type="range" min="3" max="30" value={topK}
               onChange={(e) => setTopK(parseInt(e.target.value))} />
      </div>

      {/* Benzerlik eşiği Soru Sor modunda gizli (her zaman tüm ilgili kaynaklar kullanılır) */}
      {mode !== 'ask' && (
        <div className="filter-group">
          <label>Esik: {threshold.toFixed(2)}</label>
          <input type="range" min="0" max="0.9" step="0.05" value={threshold}
                 onChange={(e) => setThreshold(parseFloat(e.target.value))} />
        </div>
      )}
    </div>
  );
}

export default FilterPanel;
