import { useEffect, useState } from "react";

export default function ItemDetailPanel({ item, saving, deleting, onSave, onDelete }) {
  const [isFavorite, setIsFavorite] = useState(false);
  const [note, setNote] = useState("");
  const [tags, setTags] = useState("");

  useEffect(() => {
    if (!item) {
      setIsFavorite(false);
      setNote("");
      setTags("");
      return;
    }

    setIsFavorite(item.is_favorite);
    setNote(item.note || "");
    setTags(item.tags.join(", "));
  }, [item]);

  if (!item) {
    return (
      <aside className="card detail-card empty">
        <h2>Item details</h2>
        <p className="muted">Select an item from the list to edit notes, tags, or favorite status.</p>
      </aside>
    );
  }

  const handleSave = async (event) => {
    event.preventDefault();

    const nextTags = tags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);

    await onSave({
      is_favorite: isFavorite,
      note: note || null,
      tags: nextTags,
    });
  };

  return (
    <aside className="card detail-card">
      <h2>{item.title}</h2>
      <p className="muted">{item.source_site}</p>

      <a href={item.url} target="_blank" rel="noreferrer" className="inline-link">
        Open original link
      </a>

      <form className="detail-form" onSubmit={handleSave}>
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={isFavorite}
            onChange={(event) => setIsFavorite(event.target.checked)}
          />
          Mark as favorite
        </label>

        <label>
          Note
          <textarea
            rows={6}
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="Write personal notes"
          />
        </label>

        <label>
          Tags
          <input
            type="text"
            value={tags}
            onChange={(event) => setTags(event.target.value)}
            placeholder="dp, trees"
          />
        </label>

        <div className="detail-actions">
          <button type="submit" className="primary-btn" disabled={saving || deleting}>
            {saving ? "Saving..." : "Save changes"}
          </button>

          <button
            type="button"
            className="danger-btn"
            disabled={saving || deleting}
            onClick={() => onDelete(item)}
          >
            {deleting ? "Deleting..." : "Delete"}
          </button>
        </div>
      </form>
    </aside>
  );
}
