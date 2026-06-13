import { useEffect } from "react";
import { useMatch, useNavigate } from "react-router-dom";

import AddURLModal from "../components/AddURLModal";
import BlogCard from "../components/cards/BlogCard";
import ProblemCard from "../components/cards/ProblemCard";
import YouTubeCard from "../components/cards/YouTubeCard";
import Sidebar from "../components/layout/Sidebar";
import ResourceDetailView from "../components/ResourceDetailView";
import Topbar from "../components/layout/Topbar";
import { GridIcon, ListIcon } from "../components/shared/Icons";
import { useResources } from "../hooks/useResources";

const FILTER_LABELS = {
  all: "All Resources",
  problem: "Problems",
  yt: "Videos",
  bl: "Blogs",
};

const FILTERS = [
  { key: "all", label: "All" },
  { key: "problem", label: "Problems" },
  { key: "yt", label: "Videos" },
  { key: "bl", label: "Blogs" },
];

function ResourceCard({ resource, view, index }) {
  if (resource.t === "yt") {
    return <YouTubeCard resource={resource} view={view} index={index} />;
  }
  if (resource.t === "bl") {
    return <BlogCard resource={resource} view={view} index={index} />;
  }
  return <ProblemCard resource={resource} view={view} index={index} />;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const resourceMatch = useMatch("/dashboard/resources/:resourceId");
  const resources = useResources();
  const { modalOpen, setModalOpen } = resources;
  const routeResourceId = resourceMatch?.params.resourceId || null;
  const routeResource = routeResourceId
    ? resources.resources.find((resource) => String(resource.id) === routeResourceId) || null
    : null;
  const isResourceRoute = Boolean(routeResourceId);

  useEffect(() => {
    const onKeyDown = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setModalOpen(true);
      }

      if (event.key === "Escape") {
        if (modalOpen) {
          setModalOpen(false);
        }
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [modalOpen, setModalOpen]);

  const handleFilterChange = (filter) => {
    resources.setFilter(filter);
    if (isResourceRoute) {
      navigate("/dashboard");
    }
  };

  const handleSaveResource = (resource) => {
    resources.addResource(resource);
    resources.setFilter("all");
    if (isResourceRoute) {
      navigate("/dashboard");
    }
  };

  return (
    <div className="sh-app">
      <Sidebar
        counts={resources.counts}
        activeFilter={resources.filter}
        onFilterChange={handleFilterChange}
        onAddUrl={() => resources.setModalOpen(true)}
      />

      <main className="main">
        <Topbar
          search={resources.search}
          onSearchChange={resources.setSearch}
          onAddUrl={() => resources.setModalOpen(true)}
        />

        <div className="dashboard-workspace">
          <div className="content">
            {isResourceRoute ? (
              <ResourceDetailView
                resource={routeResource}
                onStatusChange={resources.updateStatus}
                onNotesChange={resources.updateNotes}
              />
            ) : (
              <>
                <div className="sec-hdr">
                  <span className="sec-title">{FILTER_LABELS[resources.filter]}</span>
                  <span className="sec-ct">{resources.filtered.length} saved</span>
                </div>

                <div className="fbar">
                  <div className="ftabs" role="tablist" aria-label="Resource filters">
                    {FILTERS.map((filter) => (
                      <button
                        type="button"
                        key={filter.key}
                        className={`ftab ${resources.filter === filter.key ? "on" : ""}`}
                        onClick={() => handleFilterChange(filter.key)}
                      >
                        {filter.label} <span className="tab-ct">{resources.counts[filter.key]}</span>
                      </button>
                    ))}
                  </div>

                  <div className="vtog" aria-label="View mode">
                    <button
                      type="button"
                      className={`vbtn ${resources.view === "grid" ? "on" : ""}`}
                      onClick={() => resources.setView("grid")}
                      title="Grid view"
                      aria-label="Grid view"
                    >
                      <GridIcon size={13} />
                    </button>
                    <button
                      type="button"
                      className={`vbtn ${resources.view === "lst" ? "on" : ""}`}
                      onClick={() => resources.setView("lst")}
                      title="List view"
                      aria-label="List view"
                    >
                      <ListIcon />
                    </button>
                  </div>
                </div>

                <div className={`resource-collection ${resources.view}`}>
                  {resources.filtered.length ? (
                    resources.filtered.map((resource, index) => (
                      <ResourceCard key={resource.id} resource={resource} view={resources.view} index={index} />
                    ))
                  ) : (
                    <div className="empty">
                      <div className="empty-ico">+</div>
                      <div className="empty-t">Nothing here yet</div>
                      <div className="empty-s">Paste a URL above to save your first resource.</div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
          <aside className="future-rail" aria-hidden="true" />
        </div>
      </main>

      <AddURLModal
        open={resources.modalOpen}
        onClose={() => resources.setModalOpen(false)}
        onSave={handleSaveResource}
      />
    </div>
  );
}
