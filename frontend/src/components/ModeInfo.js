import React, { useState } from 'react';

// Her mod için açıklayıcı bilgi: ne işe yarar, ne zaman, nasıl kullanılır.
const INFO = {
  ask: {
    icon: '💬',
    title: 'Soru Sor — nedir, nasıl çalışır?',
    what:
      'Sorduğunuz soruyu sistemdeki Türkçe haber dokümanlarında arar ve yapay zekanın (Gemini) ' +
      'yalnızca bu kaynaklara dayanarak ürettiği, kaynak gösteren bir cevap verir.',
    when: 'Bir sorunun doğrudan cevabını istiyorsanız bu modu kullanın.',
    how: [
      'Sorunuzu yazın (ör. "Bitcoin fiyatında son durum ne?").',
      'İsterseniz kategori veya kaynak sayısını ayarlayın.',
      '"Soru Sor" düğmesine basın.',
      'Cevabın altında, cevabın dayandığı kaynak dokümanları görürsünüz.',
    ],
    note:
      'Cevap yalnızca dokümanlardaki bilgiden üretilir; bilgi yoksa "bulunamadı" der, uydurmaz.',
    terms: null,
  },
  search: {
    icon: '🔍',
    title: 'Arama — nedir, nasıl çalışır?',
    what:
      'Sorgunuzla en alakalı dokümanları puanlarıyla birlikte listeler. Cevap üretmez; ' +
      'belgelerin kendisini bulup taramanızı sağlar.',
    when: 'Dokümanların kendisini görmek, kaynakları taramak istediğinizde kullanın.',
    how: [
      'Aramak istediğiniz ifadeyi yazın.',
      'Bir "Yöntem" seçin (öneri: Hibrit).',
      'İsterseniz kategori, sonuç sayısı ve eşiği ayarlayın.',
      '"Ara" düğmesine basın.',
    ],
    note: null,
    terms: [
      ['BM25 (Sözcüksel)', 'Kelime eşleşmesine bakar — birebir geçen kelimeleri bulur.'],
      ['Vektör (Anlamsal)', 'Anlam benzerliğine bakar — farklı kelimelerle aynı konuyu bulur.'],
      ['Hibrit', 'BM25 + Vektör birleşimi. Genelde en iyi sonuç; varsayılan budur.'],
      ['ChromaDB', 'Alternatif bir anlamsal arama motoru (vektör tabanlı).'],
      ['Eşik', 'Sonuçların minimum benzerlik puanı. Yükseltirseniz daha az ama daha alakalı sonuç gelir.'],
    ],
  },
  compare: {
    icon: '📊',
    title: 'Karşılaştır — nedir, nasıl çalışır?',
    what:
      'Aynı sorguyu BM25, Vektör ve Hibrit yöntemleriyle aynı anda çalıştırır ve sonuçları ' +
      'yan yana, süre ve sonuç sayısıyla birlikte gösterir.',
    when: 'Yöntemler arasındaki farkı görmek veya analiz/sunum yapmak istediğinizde kullanın.',
    how: [
      'Bir sorgu yazın (ör. "ekonomik büyüme").',
      'İsterseniz kategori, sonuç sayısı ve eşiği ayarlayın.',
      '"Karşılaştır" düğmesine basın.',
      'Üç yöntemin sonuçlarını ve hızını karşılaştırın.',
    ],
    note:
      'Hangi yöntemin ne tür sorgularda daha iyi çalıştığını görmek için idealdir.',
    terms: null,
  },
};

function ModeInfo({ mode }) {
  const [open, setOpen] = useState(false);
  const info = INFO[mode];
  if (!info) return null;

  return (
    <div className={`mode-info ${open ? 'open' : ''}`}>
      <button className="mode-info-head" onClick={() => setOpen((o) => !o)}>
        <span className="mode-info-icon">{info.icon}</span>
        <span className="mode-info-title">{info.title}</span>
        <span className="mode-info-toggle">{open ? 'Gizle ▲' : 'Nasıl kullanılır? ▼'}</span>
      </button>

      {open && (
        <div className="mode-info-body">
          <p className="mode-info-what">{info.what}</p>

          <p className="mode-info-when"><strong>Ne zaman?</strong> {info.when}</p>

          <div className="mode-info-how">
            <strong>Nasıl kullanılır?</strong>
            <ol>
              {info.how.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          </div>

          {info.terms && (
            <div className="mode-info-terms">
              <strong>Terimler</strong>
              <ul>
                {info.terms.map(([term, desc], i) => (
                  <li key={i}>
                    <span className="term-name">{term}:</span> {desc}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {info.note && <p className="mode-info-note">ℹ️ {info.note}</p>}
        </div>
      )}
    </div>
  );
}

export default ModeInfo;
