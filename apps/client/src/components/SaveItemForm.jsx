import { useState } from "react";

export default function SaveItemForm({ loading, onSave }) {
  const [url, setUrl] = useState("");
  const [note, setNote] = useState("");
  const [tags, setTags] = useState("");
  const [isFavorite, setIsFavorite] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const nextTags = tags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);

    await onSave({
      url,
      note: note || null,
      tags: nextTags,
      is_favorite: isFavorite,
    });

    setUrl("");
    setNote("");
    setTags("");
    setIsFavorite(false);
  };

  return (
    <form className="card save-form" onSubmit={handleSubmit}>
      <div className="card-headline">
        <h2>Save a new link</h2>
        <p>Paste any coding problem or blog URL.</p>
      </div>

      <label>
        URL
        <input
          type="url"
          placeholder="https://..."
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          required
        />
      </label>

      <label>
        Note
        <textarea
          rows={2}
          placeholder="Optional note"
          value={note}
          onChange={(event) => setNote(event.target.value)}
        />
      </label>

      <label>
        Tags (comma separated)
        <input
          type="text"
          placeholder="graphs, dp"
          value={tags}
          onChange={(event) => setTags(event.target.value)}
        />
      </label>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={isFavorite}
          onChange={(event) => setIsFavorite(event.target.checked)}
        />
        Mark as favorite
      </label>

      <button type="submit" className="primary-btn" disabled={loading}>
        {loading ? "Saving..." : "Save item"}
      </button>
    </form>
  );
}
