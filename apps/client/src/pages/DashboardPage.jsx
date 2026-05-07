import { useCallback, useEffect, useMemo, useState } from "react";

import ItemDetailPanel from "../components/ItemDetailPanel";
import ItemFilters from "../components/ItemFilters";
import ItemList from "../components/ItemList";
import SaveItemForm from "../components/SaveItemForm";
import StatsPanel from "../components/StatsPanel";
import { createItem, deleteItem, listItems, updateItem } from "../api/itemsApi";
import { useAuth } from "../contexts/AuthContext";
import { useDebouncedValue } from "../hooks/useDebouncedValue";

const INITIAL_STATS = {
  savedCount: 0,
  favoriteCount: 0,
  sourceCount: 0,
  topSites: [],
};

function toErrorMessage(error) {
  return error?.message || "Something went wrong. Please try again.";
}

export default function DashboardPage() {
  const { user, logout, withAuth } = useAuth();

  const [filters, setFilters] = useState({
    q: "",
    source_site: "",
    content_type: "",
    favorite: "all",
    sort: "recent",
    page: 1,
    limit: 20,
  });

  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [listLoading, setListLoading] = useState(false);
  const [listError, setListError] = useState("");

  const [stats, setStats] = useState(INITIAL_STATS);

  const [selectedItem, setSelectedItem] = useState(null);
  const [globalError, setGlobalError] = useState("");

  const [creating, setCreating] = useState(false);
  const [savingItem, setSavingItem] = useState(false);
  const [deletingItem, setDeletingItem] = useState(false);

  const debouncedQuery = useDebouncedValue(filters.q, 350);

  const listRequestFilters = useMemo(
    () => ({
      q: debouncedQuery || undefined,
      source_site: filters.source_site || undefined,
      content_type: filters.content_type || undefined,
      is_favorite:
        filters.favorite === "all"
          ? undefined
          : filters.favorite === "true",
      page: filters.page,
      limit: filters.limit,
      sort: filters.sort,
    }),
    [debouncedQuery, filters.content_type, filters.favorite, filters.limit, filters.page, filters.sort, filters.source_site],
  );

  const totalPages = Math.max(1, Math.ceil(total / filters.limit));

  const loadItems = useCallback(async () => {
    setListLoading(true);
    setListError("");

    try {
      const payload = await withAuth((accessToken) => listItems(accessToken, listRequestFilters));
      setItems(payload.items);
      setTotal(payload.total);
      setSelectedItem((previous) => {
        if (!previous) {
          return null;
        }
        return payload.items.find((item) => item.id === previous.id) || null;
      });
    } catch (error) {
      setListError(toErrorMessage(error));
    } finally {
      setListLoading(false);
    }
  }, [listRequestFilters, withAuth]);

  const loadStats = useCallback(async () => {
    try {
      const payload = await withAuth((accessToken) =>
        listItems(accessToken, {
          page: 1,
          limit: 100,
          sort: "recent",
        }),
      );

      const bySite = {};
      let favoriteCount = 0;

      payload.items.forEach((item) => {
        bySite[item.source_site] = (bySite[item.source_site] || 0) + 1;
        if (item.is_favorite) {
          favoriteCount += 1;
        }
      });

      const topSites = Object.entries(bySite)
        .map(([site, count]) => ({ site, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

      setStats({
        savedCount: payload.total,
        favoriteCount,
        sourceCount: Object.keys(bySite).length,
        topSites,
      });
    } catch (error) {
      setGlobalError(toErrorMessage(error));
    }
  }, [withAuth]);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  const handleFilterChange = (field, value) => {
    setFilters((previous) => ({
      ...previous,
      [field]: value,
      page: field === "page" ? value : 1,
    }));
  };

  const handleResetFilters = () => {
    setFilters((previous) => ({
      ...previous,
      q: "",
      source_site: "",
      content_type: "",
      favorite: "all",
      sort: "recent",
      page: 1,
    }));
  };

  const handleCreate = async (payload) => {
    setCreating(true);
    setGlobalError("");

    try {
      await withAuth((accessToken) => createItem(accessToken, payload));
      await Promise.all([loadItems(), loadStats()]);
    } catch (error) {
      setGlobalError(toErrorMessage(error));
      throw error;
    } finally {
      setCreating(false);
    }
  };

  const handleSaveItem = async (payload) => {
    if (!selectedItem) {
      return;
    }

    setSavingItem(true);
    setGlobalError("");

    try {
      const updated = await withAuth((accessToken) => updateItem(accessToken, selectedItem.id, payload));
      setSelectedItem(updated);
      setItems((previous) => previous.map((item) => (item.id === updated.id ? updated : item)));
      await loadStats();
    } catch (error) {
      setGlobalError(toErrorMessage(error));
    } finally {
      setSavingItem(false);
    }
  };

  const handleDeleteItem = async (item) => {
    const confirmed = window.confirm("Delete this saved item?");
    if (!confirmed) {
      return;
    }

    setDeletingItem(true);
    setGlobalError("");

    try {
      await withAuth((accessToken) => deleteItem(accessToken, item.id));
      setSelectedItem(null);
      await Promise.all([loadItems(), loadStats()]);
    } catch (error) {
      setGlobalError(toErrorMessage(error));
    } finally {
      setDeletingItem(false);
    }
  };

  return (
    <main className="dashboard-shell">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Study Saver Dashboard</p>
          <h1>Welcome, {user?.email}</h1>
        </div>

        <button type="button" className="secondary-btn" onClick={() => logout()}>
          Logout
        </button>
      </header>

      {globalError ? <p className="form-error banner-error">{globalError}</p> : null}

      <section className="dashboard-top-grid">
        <StatsPanel stats={stats} />
        <SaveItemForm loading={creating} onSave={handleCreate} />
      </section>

      <ItemFilters filters={filters} onFieldChange={handleFilterChange} onReset={handleResetFilters} />

      <section className="dashboard-content-grid">
        <div className="content-main">
          <ItemList
            items={items}
            total={total}
            loading={listLoading}
            error={listError}
            selectedItemId={selectedItem?.id || null}
            onSelect={setSelectedItem}
          />

          <div className="pagination-row">
            <button
              type="button"
              className="ghost-btn"
              onClick={() => handleFilterChange("page", Math.max(1, filters.page - 1))}
              disabled={filters.page <= 1 || listLoading}
            >
              Previous
            </button>

            <p>
              Page {filters.page} of {totalPages}
            </p>

            <button
              type="button"
              className="ghost-btn"
              onClick={() => handleFilterChange("page", Math.min(totalPages, filters.page + 1))}
              disabled={filters.page >= totalPages || listLoading}
            >
              Next
            </button>
          </div>
        </div>

        <ItemDetailPanel
          item={selectedItem}
          saving={savingItem}
          deleting={deletingItem}
          onSave={handleSaveItem}
          onDelete={handleDeleteItem}
        />
      </section>
    </main>
  );
}
