import { useEffect, useRef, useState } from "react";

import { fetchMetadataPreview } from "../api/metadataApi";
import { detectType } from "../utils/detectType";
import DifficultyBadge from "./shared/DifficultyBadge";
import { CheckIcon, LinkIcon } from "./shared/Icons";
import PlatformBadge from "./shared/PlatformBadge";

function PreviewSkeleton({ type }) {
  return (
    <div className="prev" data-t={type}>
      <div className="shim sh-t" />
      <div className="shim sh-s" />
      <div className="shim sh-g" />
    </div>
  );
}

function PreviewCard({ preview }) {
  return (
    <div className="prev" data-t={preview.t}>
      <div className="prev-head">
        <PlatformBadge type={preview.t} />
        {preview.t === "lc" || preview.t === "cf" ? <span className="pnum">#{preview.num}</span> : null}
      </div>
      <div className="prev-title">{preview.title}</div>
      <div className="prev-meta">
        {preview.t === "lc" || preview.t === "cf" ? <DifficultyBadge resource={preview} /> : null}
        {preview.t === "lc" || preview.t === "cf"
          ? preview.tags.slice(0, 2).map((tag) => (
              <span className="itag" key={tag}>
                {tag}
              </span>
            ))
          : null}
        {preview.t === "yt" ? (
          <>
            <span className="ytch prev-channel">{preview.channel}</span>
            <span className="cdate">{preview.dur}</span>
          </>
        ) : null}
        {preview.t === "bl" ? <span className="cdate">{preview.domain} - {preview.readTime}</span> : null}
      </div>
    </div>
  );
}

export default function AddURLModal({ open, onClose, onSave }) {
  const [url, setUrl] = useState("");
  const [detectedType, setDetectedType] = useState(null);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    if (!open) {
      return;
    }

    setUrl("");
    setDetectedType(null);
    setPreview(null);
    setStatus("idle");
    setError("");
    window.setTimeout(() => inputRef.current?.focus(), 80);
  }, [open]);

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    const cleanUrl = url.trim();
    const type = detectType(cleanUrl);
    setDetectedType(type);
    setPreview(null);
    setError("");

    if (!cleanUrl || cleanUrl.length < 6) {
      setStatus("idle");
      return undefined;
    }

    if (!type) {
      setStatus("error");
      setError("Could not detect URL type. Check the URL and try again.");
      return undefined;
    }

    setStatus("typing");

    let cancelled = false;
    const timer = window.setTimeout(async () => {
      setStatus("loading");

      try {
        const metadataPreview = await fetchMetadataPreview(cleanUrl, type);
        if (!cancelled) {
          setPreview(metadataPreview);
          setStatus("success");
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(nextError.message || "Could not fetch metadata. Try another URL.");
          setStatus("error");
        }
      }
    }, 300);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [open, url]);

  const handleSave = () => {
    if (!preview) {
      return;
    }

    onSave(preview);
    onClose();
  };

  return (
    <div className={`ov ${open ? "open" : ""}`} onClick={(event) => event.target === event.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="add-url-title">
        <div className="m-title" id="add-url-title">
          Add to your library
        </div>
        <div className="m-sub">Paste a URL - LeetCode, Codeforces, YouTube, any blog, and more</div>

        <div className="url-wrap">
          <span className="url-ico">
            <LinkIcon />
          </span>
          <input
            ref={inputRef}
            type="text"
            className="url-in"
            placeholder="https://leetcode.com/problems/..."
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            autoComplete="off"
            spellCheck={false}
          />
          <div className={`type-dot ${detectedType ? `vis ${detectedType}` : ""}`} />
        </div>

        <div className="prev-area">
          {status === "loading" || status === "typing" ? <PreviewSkeleton type={detectedType} /> : null}
          {status === "success" && preview ? <PreviewCard preview={preview} /> : null}
          {status === "error" ? <div className="prev-error">{error}</div> : null}
        </div>

        <div className="mfoot">
          <button type="button" className="btn-c" onClick={onClose}>
            Cancel
          </button>
          <button type="button" className="btn-s" onClick={handleSave} disabled={status !== "success" || !preview}>
            <CheckIcon />
            Save to library
          </button>
        </div>
      </div>
    </div>
  );
}
