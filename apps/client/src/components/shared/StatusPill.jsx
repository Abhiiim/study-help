const STATUS_ICON = {
  solved: "✓",
  attempted: "◎",
  unsolved: "○",
  saved: "○",
  watching: "▶",
  watched: "✓",
  unread: "○",
  reading: "▶",
  read: "✓",
};

export default function StatusPill({ status }) {
  return (
    <span className={`sp ${status}`}>
      {STATUS_ICON[status] || "○"} {status}
    </span>
  );
}
