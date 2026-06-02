import React, { useState, useEffect } from 'react';
import ModeTabs from './components/ModeTabs';
import SearchBar from './components/SearchBar';
import FilterPanel from './components/FilterPanel';
import MetricsDisplay from './components/MetricsDisplay';
import SearchResults from './components/SearchResults';
import ComparisonPanel from './components/ComparisonPanel';
import AnswerPanel from './components/AnswerPanel';
import ExampleQuestions from './components/ExampleQuestions';
import searchAPI from './services/api';
import './App.css';

// Her modun arama çubuğu metinleri
const TAB_CONFIG = {
  ask: {
    submit: 'Soru Sor',
    loading: 'Cevaplaniyor...',
    placeholder: 'Bir soru sorun... (orn: Bitcoin fiyatinda son durum ne?)',
  },
  search: {
    submit: 'Ara',
    loading: 'Araniyor...',
    placeholder: 'Arama yapin... (orn: merkez bankasi faiz karari)',
  },
  compare: {
    submit: 'Karsilastir',
    loading: 'Karsilastiriliyor...',
    placeholder: 'Karsilastirilacak sorgu... (orn: ekonomik buyume)',
  },
};

function App() {
  const [activeTab, setActiveTab] = useState('ask'); // 'ask' | 'search' | 'compare'
  const [query, setQuery] = useState('');
  const [method, setMethod] = useState('hybrid');
  const [topK, setTopK] = useState(10);
  const [threshold, setThreshold] = useState(0.2);
  const [category, setCategory] = useState('all');
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [searchResponse, setSearchResponse] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [statsData, catData] = await Promise.all([
        searchAPI.getStats(),
        searchAPI.getCategories(),
      ]);
      setStats(statsData);
      setCategories(catData.categories);
    } catch (err) {
      setError('Backend bağlantısı kurulamadı. Backend çalışıyor mu?');
    }
  };

  // Mod değiştiğinde önceki sonuçları temizle (karışıklığı önler)
  const switchTab = (key) => {
    if (key === activeTab) return;
    setActiveTab(key);
    setAnswer(null);
    setSearchResponse(null);
    setComparison(null);
    setError(null);
  };

  const handleAsk = async (presetQuery) => {
    // Buton tıklamasında olay nesnesi, hazır soruda string gelir
    const q = typeof presetQuery === 'string' ? presetQuery : query;
    if (!q.trim()) return;
    if (typeof presetQuery === 'string') setQuery(presetQuery);

    setLoading(true);
    setError(null);
    setAnswer(null);

    try {
      const result = await searchAPI.ask(q, topK, category === 'all' ? null : category);
      setAnswer(result);
    } catch (err) {
      setError('Soru cevaplanırken hata oluştu: ' + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setSearchResponse(null);

    try {
      const result = await searchAPI.search(query, method, topK, threshold,
                                            category === 'all' ? null : category);
      setSearchResponse(result);
    } catch (err) {
      setError('Arama sırasında hata oluştu: ' + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  };

  const handleCompare = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setComparison(null);

    try {
      const result = await searchAPI.compare(query, topK, threshold,
                                             category === 'all' ? null : category);
      setComparison(result);
    } catch (err) {
      setError('Karşılaştırma sırasında hata oluştu: ' + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  };

  const handleSubmit = () => {
    if (activeTab === 'ask') handleAsk();
    else if (activeTab === 'search') handleSearch();
    else handleCompare();
  };

  const cfg = TAB_CONFIG[activeTab];

  return (
    <div className="app">
      <header className="app-header">
        <h1>SemanticSearch</h1>
        <p>Türkçe Doküman Soru-Cevap ve Hibrit Arama Sistemi</p>
      </header>

      <main className="app-main">
        <MetricsDisplay stats={stats} />

        <ModeTabs active={activeTab} onChange={switchTab} />

        <SearchBar
          query={query}
          setQuery={setQuery}
          onSubmit={handleSubmit}
          submitLabel={cfg.submit}
          loadingLabel={cfg.loading}
          placeholder={cfg.placeholder}
          loading={loading}
        />

        <FilterPanel
          mode={activeTab}
          method={method}
          setMethod={setMethod}
          topK={topK}
          setTopK={setTopK}
          threshold={threshold}
          setThreshold={setThreshold}
          category={category}
          setCategory={setCategory}
          categories={categories}
        />

        {error && <div className="error-message">{error}</div>}

        {/* SORU SOR */}
        {activeTab === 'ask' && answer && <AnswerPanel answer={answer} />}
        {activeTab === 'ask' && !answer && !loading && (
          <ExampleQuestions onPick={handleAsk} disabled={loading} />
        )}

        {/* ARAMA */}
        {activeTab === 'search' && searchResponse && (
          <SearchResults response={searchResponse} />
        )}

        {/* KARŞILAŞTIR */}
        {activeTab === 'compare' && comparison && (
          <ComparisonPanel comparison={comparison} />
        )}
      </main>

      <footer className="app-footer">
        <p>SemanticSearch — Zeki Sistem Uygulamaları Final Projesi — 2026</p>
      </footer>
    </div>
  );
}

export default App;
