import { getPlatformLabel } from "../../utils/detectType";

export default function PlatformBadge({ type }) {
  return (
    <span className="pb" data-t={type}>
      {getPlatformLabel(type)}
    </span>
  );
}
