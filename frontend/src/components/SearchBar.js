import React from 'react';

function SearchBar({ query, setQuery, onSearch, onCompare, loading }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') onSearch();
  };

  return (
    <div className="search-bar">
      <div className="search-input-wrapper">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Arama yapın..."
          className="search-input"
        />
      </div>
      <div className="search-buttons">
        <button onClick={onSearch} disabled={loading || !query.trim()} className="btn btn-primary">
          {loading ? 'Aranıyor...' : 'Ara'}
        </button>
        <button onClick={onCompare} disabled={loading || !query.trim()} className="btn btn-compare">
          {loading ? 'Karsilastiriliyor...' : 'Karsilastir'}
        </button>
      </div>
    </div>
  );
}

export default SearchBar;
