import React from 'react';

function MetricsDisplay({ stats }) {
  if (!stats) return null;

  const metrics = [
    { value: stats.total_documents?.toLocaleString() || '-', label: 'Dokuman' },
    { value: stats.index_status?.total_chunks?.toLocaleString() || '-', label: 'Parca (Chunk)' },
    { value: stats.index_status?.embedding_dimension || '-', label: 'Vektor Boyutu' },
    { value: stats.index_status?.faiss_vectors?.toLocaleString() || '-', label: 'FAISS Vektor' },
  ];

  return (
    <div className="metrics-display">
      {metrics.map((m, i) => (
        <div key={i} className="metric-card">
          <span className="metric-value">{m.value}</span>
          <span className="metric-label">{m.label}</span>
        </div>
      ))}
    </div>
  );
}

export default MetricsDisplay;
