import React from 'react';
import SearchResults from './SearchResults';

function ComparisonPanel({ comparison }) {
  if (!comparison) return null;

  return (
    <div className="comparison-panel">
      <h2 className="comparison-title">Yontem Karsilastirmasi</h2>

      <div className="comparison-summary">
        <div className="summary-card bm25">
          <h4>BM25</h4>
          <p>{comparison.bm25.total_found} sonuc &middot; {comparison.bm25.query_time_ms} ms</p>
        </div>
        <div className="summary-card vector">
          <h4>FAISS</h4>
          <p>{comparison.vector.total_found} sonuc &middot; {comparison.vector.query_time_ms} ms</p>
        </div>
        <div className="summary-card hybrid">
          <h4>Hibrit</h4>
          <p>{comparison.hybrid.total_found} sonuc &middot; {comparison.hybrid.query_time_ms} ms</p>
        </div>
      </div>

      <div className="comparison-grid">
        <SearchResults response={comparison.bm25} title="BM25 (Sozcuksel)" />
        <SearchResults response={comparison.vector} title="FAISS (Vektor)" />
        <SearchResults response={comparison.hybrid} title="Hibrit (RRF)" />
      </div>
    </div>
  );
}

export default ComparisonPanel;
