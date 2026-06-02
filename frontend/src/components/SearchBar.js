import React from 'react';

function SearchBar({ query, setQuery, onSearch, onCompare, onAsk, loading }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') onAsk();
  };

  return (
    <div className="search-bar">
      <div className="search-input-wrapper">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Bir soru sorun veya arama yapın... (örn: Merkez Bankası faiz kararı ne oldu?)"
          className="search-input"
        />
      </div>
      <div className="search-buttons">
        <button onClick={onAsk} disabled={loading || !query.trim()} className="btn btn-ask">
          {loading ? 'Cevaplaniyor...' : 'Soru Sor'}
        </button>
        <button onClick={onSearch} disabled={loading || !query.trim()} className="btn btn-primary">
          {loading ? 'Araniyor...' : 'Ara'}
        </button>
        <button onClick={onCompare} disabled={loading || !query.trim()} className="btn btn-compare">
          {loading ? 'Karsilastiriliyor...' : 'Karsilastir'}
        </button>
      </div>
    </div>
  );
}

export default SearchBar;
