export function LogoMark() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <rect x="2" y="2" width="12" height="5.5" rx="1.5" fill="white" opacity=".92" />
      <rect x="2" y="9.5" width="7.5" height="4.5" rx="1.5" fill="white" opacity=".65" />
      <circle cx="13.5" cy="11.5" r="2.2" fill="white" opacity=".82" />
    </svg>
  );
}

export function GridIcon({ size = 15, className = "" }) {
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
      <rect x="1" y="1" width="6" height="6" rx="1.2" />
      <rect x="9" y="1" width="6" height="6" rx="1.2" />
      <rect x="1" y="9" width="6" height="6" rx="1.2" />
      <rect x="9" y="9" width="6" height="6" rx="1.2" />
    </svg>
  );
}

export function CodeIcon() {
  return (
    <svg className="nav-ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
      <polyline points="5,4 2,8 5,12" />
      <polyline points="11,4 14,8 11,12" />
    </svg>
  );
}

export function VideoIcon() {
  return (
    <svg className="nav-ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
      <rect x="1" y="3" width="14" height="10" rx="2" />
      <path d="M6.5 6l4 2.5-4 2.5V6z" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function BlogIcon() {
  return (
    <svg className="nav-ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
      <rect x="2" y="2" width="12" height="12" rx="1.5" />
      <path d="M5 6h6M5 9.5h4" />
    </svg>
  );
}

export function SearchIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <circle cx="7" cy="7" r="5" />
      <path d="M12 12l-2.5-2.5" />
    </svg>
  );
}

export function PlusIcon({ size = 13 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
      <path d="M7 1v12M1 7h12" />
    </svg>
  );
}

export function ListIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 12 12" fill="currentColor" aria-hidden="true">
      <rect x="0" y="1" width="12" height="2.2" rx=".8" />
      <rect x="0" y="4.9" width="12" height="2.2" rx=".8" />
      <rect x="0" y="8.8" width="12" height="2.2" rx=".8" />
    </svg>
  );
}

export function MoonIcon() {
  return (
    <svg className="theme-moon" width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M14 10.7A7 7 0 0 1 5.3 2a7 7 0 1 0 8.7 8.7z" fill="currentColor" />
    </svg>
  );
}

export function SunIcon() {
  return (
    <svg className="theme-sun" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
      <circle cx="8" cy="8" r="3.5" />
      <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.41 1.41M11.54 11.54l1.41 1.41M3.05 12.95l1.41-1.41M11.54 4.46l1.41-1.41" />
    </svg>
  );
}

export function LinkIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
      <path d="M8.5 3.5a3.5 3.5 0 0 1 4.95 4.95l-1.5 1.5M7.5 12.5a3.5 3.5 0 0 1-4.95-4.95l1.5-1.5M5.5 10.5l5-5" />
    </svg>
  );
}

export function CheckIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2.3" aria-hidden="true">
      <path d="M2 7l3.5 3.5L12 3" />
    </svg>
  );
}

export function PlayIcon({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 14 14" fill="white" aria-hidden="true">
      <path d="M4 2l9 5-9 5V2z" />
    </svg>
  );
}

export function GlobeIcon() {
  return (
    <svg width="11" height="11" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true">
      <circle cx="8" cy="8" r="6.5" />
      <path d="M8 1.5c-1.5 2-2.5 4-2.5 6.5s1 4.5 2.5 6.5M8 1.5c1.5 2 2.5 4 2.5 6.5S9.5 13 8 15M1.5 8h13" />
    </svg>
  );
}

export function CloseIcon() {
  return (
    <svg width="11" height="11" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden="true">
      <path d="M1 1l10 10M11 1L1 11" />
    </svg>
  );
}

export function ExternalLinkIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="M6 2H3a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-3M10 2h4v4M14 2L8 8" />
    </svg>
  );
}

export function UserIcon({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
      <circle cx="8" cy="5.2" r="3" />
      <path d="M2.8 14c.8-2.7 2.6-4 5.2-4s4.4 1.3 5.2 4" />
    </svg>
  );
}

export function SettingsIcon({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
      <circle cx="8" cy="8" r="2.2" />
      <path d="M8 1.5v2M8 12.5v2M2.35 4.75l1.75 1M11.9 10.25l1.75 1M2.35 11.25l1.75-1M11.9 5.75l1.75-1" />
    </svg>
  );
}

export function LogoutIcon({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
      <path d="M6.5 2.5H3.8A1.3 1.3 0 0 0 2.5 3.8v8.4a1.3 1.3 0 0 0 1.3 1.3h2.7" />
      <path d="M7.5 8h6M11.5 5.8 13.7 8l-2.2 2.2" />
    </svg>
  );
}

export function ChevronUpIcon({ size = 13 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="m4 10 4-4 4 4" />
    </svg>
  );
}
