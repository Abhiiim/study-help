function SiteRow({ site, count }) {
  return (
    <li>
      <span>{site}</span>
      <strong>{count}</strong>
    </li>
  );
}

export default function StatsPanel({ stats }) {
  return (
    <section className="card stats-card">
      <div className="card-headline">
        <h2>Stats</h2>
      </div>

      <div className="stats-grid">
        <article>
          <p>Saved</p>
          <strong>{stats.savedCount}</strong>
        </article>

        <article>
          <p>Favorites</p>
          <strong>{stats.favoriteCount}</strong>
        </article>

        <article>
          <p>Unique sites</p>
          <strong>{stats.sourceCount}</strong>
        </article>
      </div>

      <div className="stats-sites">
        <h3>Top sources</h3>
        {stats.topSites.length ? (
          <ul>
            {stats.topSites.map((source) => (
              <SiteRow key={source.site} site={source.site} count={source.count} />
            ))}
          </ul>
        ) : (
          <p className="muted">No saved links yet.</p>
        )}
      </div>
    </section>
  );
}
