import { Link } from "react-router-dom";

import DifficultyBadge from "../shared/DifficultyBadge";
import PlatformBadge from "../shared/PlatformBadge";
import StatusPill from "../shared/StatusPill";

export default function ProblemCard({ resource, view, index }) {
  const delay = `${index * (view === "lst" ? 28 : 38)}ms`;
  const to = `/dashboard/resources/${resource.id}`;

  if (view === "lst") {
    return (
      <Link
        className="card resource-card"
        data-t={resource.t}
        style={{ animationDelay: delay }}
        to={to}
      >
        <div className="lcrd">
          <PlatformBadge type={resource.t} />
          <span className="ctitle">{resource.title}</span>
          <DifficultyBadge resource={resource} />
          <StatusPill status={resource.status} />
          <span className="cdate">{resource.date}</span>
        </div>
      </Link>
    );
  }

  return (
    <Link
      className="card resource-card"
      data-t={resource.t}
      style={{ animationDelay: delay }}
      to={to}
    >
      <div className="cbody">
        <div className="chead">
          <PlatformBadge type={resource.t} />
          <span className="pnum">#{resource.num}</span>
        </div>
        <div className="ctitle">{resource.title}</div>
        <div className="cmeta">
          <DifficultyBadge resource={resource} />
          {resource.tags.slice(0, 2).map((tag) => (
            <span className="itag" key={tag}>
              {tag}
            </span>
          ))}
        </div>
        <div className="cfoot">
          <StatusPill status={resource.status} />
          <span className="cdate">{resource.date}</span>
        </div>
      </div>
    </Link>
  );
}
