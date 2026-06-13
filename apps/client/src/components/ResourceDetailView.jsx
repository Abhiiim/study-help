import { Link } from "react-router-dom";

import DifficultyBadge from "./shared/DifficultyBadge";
import { ExternalLinkIcon, PlayIcon } from "./shared/Icons";
import PlatformBadge from "./shared/PlatformBadge";

const STATUS_OPTIONS = {
  lc: ["unsolved", "attempted", "solved"],
  cf: ["unsolved", "attempted", "solved"],
  yt: ["saved", "watching", "watched"],
  bl: ["unread", "reading", "read"],
};

function titleCase(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function DetailMetaCell({ label, children, wide = false }) {
  return (
    <div className="detail-meta-cell" style={wide ? { gridColumn: "1 / -1" } : undefined}>
      <span className="detail-meta-label">{label}</span>
      <span className="detail-meta-value">{children}</span>
    </div>
  );
}

function ResourceMetaGrid({ resource }) {
  if (resource.t === "lc") {
    return (
      <div className="detail-meta-grid">
        <DetailMetaCell label="Problem">
          <span className="mono-meta">#{resource.num}</span>
        </DetailMetaCell>
        <DetailMetaCell label="Difficulty">
          <DifficultyBadge resource={resource} />
        </DetailMetaCell>
        <DetailMetaCell label="Platform">
          <span className="meta-lc">{resource.platform}</span>
        </DetailMetaCell>
        <DetailMetaCell label="Saved">{resource.date}</DetailMetaCell>
      </div>
    );
  }

  if (resource.t === "cf") {
    return (
      <div className="detail-meta-grid">
        <DetailMetaCell label="Problem">
          <span className="mono-meta">{resource.num}</span>
        </DetailMetaCell>
        <DetailMetaCell label="CF Rating">
          <span className="meta-cf">{resource.diff}</span>
        </DetailMetaCell>
        <DetailMetaCell label="Platform">
          <span className="meta-cf">{resource.platform}</span>
        </DetailMetaCell>
        <DetailMetaCell label="Saved">{resource.date}</DetailMetaCell>
      </div>
    );
  }

  if (resource.t === "yt") {
    return (
      <div className="detail-meta-grid">
        <DetailMetaCell label="Channel">{resource.channel}</DetailMetaCell>
        <DetailMetaCell label="Duration">
          <span className="mono-meta">{resource.dur}</span>
        </DetailMetaCell>
        <DetailMetaCell label="Saved" wide>
          {resource.date}
        </DetailMetaCell>
      </div>
    );
  }

  return (
    <div className="detail-meta-grid">
      <DetailMetaCell label="Author">{resource.author}</DetailMetaCell>
      <DetailMetaCell label="Read Time">{resource.readTime}</DetailMetaCell>
      <DetailMetaCell label="Domain">
        <span className="meta-bl">{resource.domain}</span>
      </DetailMetaCell>
      <DetailMetaCell label="Saved">{resource.date}</DetailMetaCell>
    </div>
  );
}

function DetailTags({ resource }) {
  const tags = resource.tags?.length ? resource.tags : resource.t === "bl" ? ["Web Dev", "React"] : [];

  if (!tags.length) {
    return null;
  }

  return (
    <section className="detail-section">
      <span className="ds-lbl">{resource.t === "bl" ? "Topics" : "Tags"}</span>
      <div className="d-tags">
        {tags.map((tag) => (
          <span className="d-tag" key={tag}>
            {tag}
          </span>
        ))}
      </div>
    </section>
  );
}

export default function ResourceDetailView({ resource, onNotesChange, onStatusChange }) {
  if (!resource) {
    return (
      <div className="detail-route empty-detail-route">
        <Link className="detail-back" to="/dashboard">
          Back to library
        </Link>
        <h1>Resource not found</h1>
        <p>The selected resource is not available in the current library state.</p>
      </div>
    );
  }

  return (
    <article className="detail-route">
      <div className="detail-route-top">
        <Link className="detail-back" to="/dashboard">
          Back to library
        </Link>
        <div className="detail-title-row">
          <div className="detail-title-main">
            <div className="detail-badges">
              <PlatformBadge type={resource.t} />
              {resource.t === "lc" || resource.t === "cf" ? <span className="pnum">#{resource.num}</span> : null}
            </div>
            <h1>{resource.title}</h1>
          </div>
          <a className="d-open detail-open" href={resource.url} target="_blank" rel="noreferrer">
            <ExternalLinkIcon />
            Open original link
          </a>
        </div>
      </div>

      {resource.t === "yt" ? (
        <div className="ytthumb detail-video-thumb">
          <div className="ytgrad" />
          <div className="ytplay detail-play">
            <PlayIcon size={18} />
          </div>
          <span className="ytdur">{resource.dur}</span>
        </div>
      ) : null}

      <section className="detail-section detail-status-section">
        <div>
          <span className="ds-lbl">Status</span>
          <select className="d-sel" value={resource.status} onChange={(event) => onStatusChange(resource.id, event.target.value)}>
            {STATUS_OPTIONS[resource.t].map((status) => (
              <option key={status} value={status}>
                {titleCase(status)}
              </option>
            ))}
          </select>
        </div>
      </section>

      <ResourceMetaGrid resource={resource} />

      <section className="detail-section">
        <span className="ds-lbl">Description</span>
        <p className="d-desc">{resource.desc}</p>
      </section>

      <DetailTags resource={resource} />

      <section className="detail-section">
        <span className="ds-lbl">Notes</span>
        <textarea
          key={resource.id}
          className="d-notes detail-notes"
          placeholder="Add notes, hints, observations..."
          defaultValue={resource.notes}
          onBlur={(event) => onNotesChange(resource.id, event.target.value)}
        />
      </section>
    </article>
  );
}
