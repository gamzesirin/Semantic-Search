import React from 'react';

function SearchResults({ response, title }) {
  if (!response) return null;

  const methodLabels = {
    bm25: 'BM25',
    vector: 'FAISS',
    faiss: 'FAISS',
    chroma: 'ChromaDB',
    hybrid: 'Hibrit',
  };

  const methodColors = {
    bm25: { background: '#fff7ed', color: '#ea580c' },
    vector: { background: '#eff6ff', color: '#2563eb' },
    faiss: { background: '#eff6ff', color: '#2563eb' },
    chroma: { background: '#faf5ff', color: '#9333ea' },
    hybrid: { background: '#f0fdf4', color: '#16a34a' },
  };

  const style = methodColors[response.method] || { background: '#f4f4f5', color: '#52525b' };

  return (
    <div className="search-results">
      <div className="results-header">
        <h3>{title || methodLabels[response.method] || response.method}</h3>
        <div className="results-meta">
          <span className="meta-badge" style={style}>
            {response.total_found} sonuc
          </span>
          <span className="meta-time">{response.query_time_ms} ms</span>
        </div>
      </div>

      {response.results.length === 0 ? (
        <p className="no-results">Sonuc bulunamadi.</p>
      ) : (
        <div className="results-list">
          {response.results.map((result, index) => (
            <div key={`${result.id}-${index}`} className="result-card">
              <div className="result-rank">{index + 1}</div>
              <div className="result-content">
                <h4 className="result-title">{result.title}</h4>
                <p className="result-text">{result.content}</p>
                <div className="result-footer">
                  <span className="category-badge">{result.category}</span>
                  <span className="score-badge">{result.score}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchResults;
