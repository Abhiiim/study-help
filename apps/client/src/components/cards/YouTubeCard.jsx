import { Link } from "react-router-dom";

import { PlayIcon } from "../shared/Icons";
import PlatformBadge from "../shared/PlatformBadge";
import StatusPill from "../shared/StatusPill";

export default function YouTubeCard({ resource, view, index }) {
  const delay = `${index * (view === "lst" ? 28 : 38)}ms`;
  const to = `/dashboard/resources/${resource.id}`;

  if (view === "lst") {
    return (
      <Link
        className="card resource-card"
        data-t="yt"
        style={{ animationDelay: delay }}
        to={to}
      >
        <div className="lcrd">
          <PlatformBadge type="yt" />
          <span className="ctitle">{resource.title}</span>
          <span className="mono-meta">{resource.dur}</span>
          <StatusPill status={resource.status} />
          <span className="cdate">{resource.date}</span>
        </div>
      </Link>
    );
  }

  return (
    <Link
      className="card resource-card"
      data-t="yt"
      style={{ animationDelay: delay }}
      to={to}
    >
      <div className="cbody">
        <div className="ytthumb">
          <div className="ytgrad" />
          <div className="ytplay">
            <PlayIcon />
          </div>
          <span className="ytdur">{resource.dur}</span>
        </div>
        <div className="ytch">{resource.channel}</div>
        <div className="ctitle">{resource.title}</div>
        <div className="cfoot">
          <StatusPill status={resource.status} />
          <span className="cdate">{resource.date}</span>
        </div>
      </div>
    </Link>
  );
}
