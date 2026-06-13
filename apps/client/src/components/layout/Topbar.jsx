import { MoonIcon, PlusIcon, SearchIcon, SunIcon } from "../shared/Icons";

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("sh-theme", next);
}

export default function Topbar({ search, onSearchChange, onAddUrl }) {
  return (
    <header className="topbar">
      <div className="srch">
        <span className="srch-ic">
          <SearchIcon />
        </span>
        <input
          type="text"
          placeholder="Search resources..."
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
        />
      </div>

      <div className="tb-right">
        <span className="kbd">⌘K</span>
        <button type="button" className="ic-btn" onClick={toggleTheme} title="Toggle theme" aria-label="Toggle theme">
          <MoonIcon />
          <SunIcon />
        </button>
        <button type="button" className="add-btn" onClick={onAddUrl}>
          <PlusIcon />
          <span>Add URL</span>
        </button>
      </div>
    </header>
  );
}
