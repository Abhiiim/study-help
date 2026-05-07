export default function ItemFilters({ filters, onFieldChange, onReset }) {
  return (
    <section className="card filters-card">
      <div className="card-headline">
        <h2>Filters</h2>
      </div>

      <div className="filters-grid">
        <label>
          Search
          <input
            type="text"
            placeholder="Title, note, URL"
            value={filters.q}
            onChange={(event) => onFieldChange("q", event.target.value)}
          />
        </label>

        <label>
          Source site
          <input
            type="text"
            placeholder="leetcode.com"
            value={filters.source_site}
            onChange={(event) => onFieldChange("source_site", event.target.value)}
          />
        </label>

        <label>
          Content type
          <select
            value={filters.content_type}
            onChange={(event) => onFieldChange("content_type", event.target.value)}
          >
            <option value="">All</option>
            <option value="problem">Problem</option>
            <option value="blog">Blog</option>
            <option value="other">Other</option>
          </select>
        </label>

        <label>
          Favorite
          <select
            value={filters.favorite}
            onChange={(event) => onFieldChange("favorite", event.target.value)}
          >
            <option value="all">All</option>
            <option value="true">Favorites only</option>
            <option value="false">Not favorite</option>
          </select>
        </label>

        <label>
          Sort
          <select
            value={filters.sort}
            onChange={(event) => onFieldChange("sort", event.target.value)}
          >
            <option value="recent">Most recent</option>
            <option value="oldest">Oldest first</option>
          </select>
        </label>

        <button type="button" className="ghost-btn" onClick={onReset}>
          Reset
        </button>
      </div>
    </section>
  );
}
