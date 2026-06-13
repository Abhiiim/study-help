export default function DifficultyBadge({ resource }) {
  if (resource.t === "lc") {
    return <span className={`db ${resource.diff}`}>{resource.diff}</span>;
  }

  return <span className="cfr">{resource.diff}</span>;
}
