import React from 'react';

function AnswerPanel({ answer }) {
  if (!answer) return null;

  return (
    <div className="answer-panel">
      <div className="answer-card">
        <div className="answer-head">
          <h3 className="answer-label">Cevap</h3>
          <span className="answer-time">{answer.query_time_ms} ms</span>
        </div>
        <p className="answer-text">{answer.answer}</p>
      </div>

      {answer.sources && answer.sources.length > 0 && (
        <div className="answer-sources">
          <h4 className="sources-title">Kaynaklar ({answer.sources.length})</h4>
          <div className="sources-list">
            {answer.sources.map((s, i) => (
              <div key={i} className="source-card">
                <div className="source-index">Kaynak {i + 1}</div>
                <div className="source-body">
                  <h5 className="source-title">{s.title}</h5>
                  <p className="source-text">{s.content}</p>
                  <div className="source-footer">
                    <span className="category-badge">{s.category}</span>
                    <span className="score-badge">{s.score}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AnswerPanel;
