import React from 'react';

// Veride sonuç döndüğü doğrulanmış, kategoriye göre örnek sorular
const EXAMPLES = [
  { cat: 'Ekonomi', q: 'Bitcoin fiyatinda son durum ne?' },
  { cat: 'Spor', q: 'Fenerbahce hangi oyuncuyla sozlesme imzaladi?' },
  { cat: 'Teknoloji', q: "iPhone X'in Face ID ozelligi nedir?" },
  { cat: 'Saglik', q: 'Metabolizmayi hizlandiran besinler nelerdir?' },
  { cat: 'Siyaset', q: 'Kadir Topbas neden istifa etti?' },
  { cat: 'Magazin', q: 'Survivor yarismacilari hakkinda ne var?' },
  { cat: 'Yasam', q: 'Meksika depremi hakkinda ne biliniyor?' },
];

function ExampleQuestions({ onPick, disabled }) {
  return (
    <div className="example-questions">
      <h4 className="example-title">Ornek sorular — tiklayip deneyin</h4>
      <div className="example-chips">
        {EXAMPLES.map((e, i) => (
          <button
            key={i}
            className="example-chip"
            onClick={() => onPick(e.q)}
            disabled={disabled}
          >
            <span className="example-cat">{e.cat}</span>
            <span className="example-q">{e.q}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default ExampleQuestions;
