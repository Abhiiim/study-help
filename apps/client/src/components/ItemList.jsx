function TypeBadge({ contentType }) {
  return <span className={`type-badge ${contentType}`}>{contentType}</span>;
}

function ItemCard({ item, selected, onSelect }) {
  return (
    <button type="button" className={`item-card ${selected ? "selected" : ""}`} onClick={() => onSelect(item)}>
      <div className="item-card-top">
        <TypeBadge contentType={item.content_type} />
        {item.is_favorite ? <span className="favorite-pill">Favorite</span> : null}
      </div>

      <h3>{item.title}</h3>

      <p className="item-snippet">{item.snippet || "No snippet available"}</p>

      <div className="item-meta">
        <span>{item.source_site}</span>
        <span>{new Date(item.created_at).toLocaleDateString()}</span>
      </div>

      {item.tags.length ? (
        <div className="tags-row">
          {item.tags.map((tag) => (
            <span key={tag}>#{tag}</span>
          ))}
        </div>
      ) : null}
    </button>
  );
}

export default function ItemList({ items, total, loading, error, selectedItemId, onSelect }) {
  if (loading) {
    return (
      <section className="card list-card">
        <p className="muted">Loading items...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="card list-card">
        <p className="form-error">{error}</p>
      </section>
    );
  }

  if (!items.length) {
    return (
      <section className="card list-card">
        <p className="muted">No items found.</p>
      </section>
    );
  }

  return (
    <section className="card list-card">
      <div className="list-header">
        <h2>Saved items</h2>
        <p>{total} total</p>
      </div>

      <div className="item-list">
        {items.map((item) => (
          <ItemCard
            key={item.id}
            item={item}
            selected={selectedItemId === item.id}
            onSelect={onSelect}
          />
        ))}
      </div>
    </section>
  );
}
