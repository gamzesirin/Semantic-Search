import React, { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import FilterPanel from './components/FilterPanel';
import MetricsDisplay from './components/MetricsDisplay';
import SearchResults from './components/SearchResults';
import ComparisonPanel from './components/ComparisonPanel';
import AnswerPanel from './components/AnswerPanel';
import searchAPI from './services/api';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [method, setMethod] = useState('hybrid');
  const [topK, setTopK] = useState(10);
  const [threshold, setThreshold] = useState(0.3);
  const [category, setCategory] = useState('all');
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [searchResponse, setSearchResponse] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('search'); // 'search' | 'compare' | 'ask'

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

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setComparison(null);
    setAnswer(null);
    setMode('search');

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
    setSearchResponse(null);
    setAnswer(null);
    setMode('compare');

    try {
      const result = await searchAPI.compare(query, topK, threshold,
                                             category === 'all' ? null : category);
      setComparison(result);
    } catch (err) {
      setError('Karşılaştırma sırasında hata oluştu: ' + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  };

  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setSearchResponse(null);
    setComparison(null);
    setMode('ask');

    try {
      const result = await searchAPI.ask(query, topK,
                                         category === 'all' ? null : category);
      setAnswer(result);
    } catch (err) {
      setError('Soru cevaplanırken hata oluştu: ' + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>SemanticSearch</h1>
        <p>Türkçe Hibrit Doküman Arama Sistemi — BM25 + FAISS + ChromaDB + RRF</p>
      </header>

      <main className="app-main">
        <MetricsDisplay stats={stats} />

        <SearchBar
          query={query}
          setQuery={setQuery}
          onSearch={handleSearch}
          onCompare={handleCompare}
          onAsk={handleAsk}
          loading={loading}
        />

        <FilterPanel
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

        {mode === 'ask' && answer && (
          <AnswerPanel answer={answer} />
        )}

        {mode === 'search' && searchResponse && (
          <SearchResults response={searchResponse} />
        )}

        {mode === 'compare' && comparison && (
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
