import { useEffect, useRef, useState } from "react";

import { useAuth } from "../../contexts/AuthContext";
import {
  BlogIcon,
  ChevronUpIcon,
  CodeIcon,
  GridIcon,
  LogoMark,
  LogoutIcon,
  PlusIcon,
  SettingsIcon,
  UserIcon,
  VideoIcon,
} from "../shared/Icons";

const NAV_ITEMS = [
  { key: "all", label: "All Resources", icon: <GridIcon className="nav-ic" /> },
  { key: "problem", label: "Problems", icon: <CodeIcon /> },
  { key: "yt", label: "Videos", icon: <VideoIcon /> },
  { key: "bl", label: "Blogs", icon: <BlogIcon /> },
];

const TAGS = [
  { label: "Dynamic Programming", color: "#818CF8" },
  { label: "Graph Theory", color: "#F59E0B" },
  { label: "System Design", color: "#0DA87A" },
];

function getProfileInitial(user) {
  return (user?.name || user?.email || "S").trim().charAt(0).toUpperCase();
}

function getProfileLabel(user) {
  return user?.name || user?.email || "StudyHelp user";
}

export default function Sidebar({ counts, activeFilter, onFilterChange, onAddUrl }) {
  const { logout, user } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const profileRef = useRef(null);

  useEffect(() => {
    const onPointerDown = (event) => {
      if (!profileRef.current?.contains(event.target)) {
        setMenuOpen(false);
      }
    };

    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, []);

  return (
    <aside className="sidebar" aria-label="StudyHelp library">
      <div className="s-logo">
        <div className="s-logo-icon">
          <LogoMark />
        </div>
        <span className="s-logo-text">
          study<em>help</em>
        </span>
      </div>

      <div className="s-sec">
        <span className="s-label">Library</span>
        {NAV_ITEMS.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`nav ${activeFilter === item.key ? "on" : ""}`}
            onClick={() => onFilterChange(item.key)}
            title={item.label}
          >
            {item.icon}
            <span className="nav-text">{item.label}</span>
            <span className="nav-ct">{counts[item.key]}</span>
          </button>
        ))}
      </div>

      <div className="s-div" />

      <div className="s-sec s-tags">
        <span className="s-label">Tags</span>
        {TAGS.map((tag) => (
          <button type="button" className="nav tag-nav" key={tag.label}>
            <span className="tag-dot" style={{ background: tag.color }} />
            <span className="nav-text">{tag.label}</span>
          </button>
        ))}
      </div>

      <button type="button" className="s-add" onClick={onAddUrl}>
        <PlusIcon />
        <span>Add URL</span>
      </button>

      <div className="profile-slot" ref={profileRef}>
        {menuOpen ? (
          <div className="profile-menu" role="menu">
            <button type="button" className="profile-menu-item" role="menuitem">
              <UserIcon />
              <span>Profile</span>
            </button>
            <button type="button" className="profile-menu-item" role="menuitem">
              <SettingsIcon />
              <span>Settings</span>
            </button>
            <button type="button" className="profile-menu-item danger" role="menuitem" onClick={() => logout()}>
              <LogoutIcon />
              <span>Logout</span>
            </button>
          </div>
        ) : null}

        <button
          type="button"
          className={`profile-trigger ${menuOpen ? "on" : ""}`}
          onClick={() => setMenuOpen((open) => !open)}
          aria-haspopup="menu"
          aria-expanded={menuOpen}
        >
          <span className="profile-avatar">{getProfileInitial(user)}</span>
          <span className="profile-meta">
            <span className="profile-name">{getProfileLabel(user)}</span>
            <span className="profile-sub">Account</span>
          </span>
          <ChevronUpIcon />
        </button>
      </div>
    </aside>
  );
}
