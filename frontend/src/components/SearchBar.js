import React from 'react';

function SearchBar({ query, setQuery, onSubmit, submitLabel, loadingLabel, placeholder, loading }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') onSubmit();
  };

  return (
    <div className="search-bar">
      <div className="search-input-wrapper">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="search-input"
        />
      </div>
      <div className="search-buttons">
        <button
          onClick={onSubmit}
          disabled={loading || !query.trim()}
          className="btn btn-primary btn-block"
        >
          {loading ? loadingLabel : submitLabel}
        </button>
      </div>
    </div>
  );
}

export default SearchBar;
