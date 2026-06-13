import { Link } from "react-router-dom";

import { GlobeIcon } from "../shared/Icons";
import PlatformBadge from "../shared/PlatformBadge";
import StatusPill from "../shared/StatusPill";

export default function BlogCard({ resource, view, index }) {
  const delay = `${index * (view === "lst" ? 28 : 38)}ms`;
  const to = `/dashboard/resources/${resource.id}`;

  if (view === "lst") {
    return (
      <Link
        className="card resource-card"
        data-t="bl"
        style={{ animationDelay: delay }}
        to={to}
      >
        <div className="lcrd">
          <PlatformBadge type="bl" />
          <span className="ctitle">{resource.title}</span>
          <span className="cdate">{resource.readTime}</span>
          <StatusPill status={resource.status} />
          <span className="cdate">{resource.date}</span>
        </div>
      </Link>
    );
  }

  return (
    <Link
      className="card resource-card"
      data-t="bl"
      style={{ animationDelay: delay }}
      to={to}
    >
      <div className="cbody">
        <div className="blog-top">
          <div className="bdom">
            <GlobeIcon />
            {resource.domain}
          </div>
          <PlatformBadge type="bl" />
        </div>
        <div className="ctitle">{resource.title}</div>
        <div className="bdesc">{resource.desc}</div>
        <div className="cfoot">
          <StatusPill status={resource.status} />
          <span className="cdate">{resource.readTime}</span>
        </div>
      </div>
    </Link>
  );
}
