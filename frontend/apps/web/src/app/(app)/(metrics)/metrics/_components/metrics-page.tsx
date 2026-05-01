'use client';

import { useEffect, useMemo, useRef, useState } from 'react';

import { Button } from '@workspace/ui/components/ui/button';
import { cn } from '@workspace/ui/lib/utils';
import { BarChart3, Plus, Trash2 } from 'lucide-react';

import {
  useCreateCustomMetric,
  useCustomMetrics,
  useDeleteCustomMetric,
  useUpdateCustomMetric,
} from '@/app/(app)/(metrics)/_hooks/use-custom-metrics';

import { DeleteConfirmDialog } from './delete-confirm-dialog';
import { FilterPill } from './filter-pill';
import {
  MetricDetail,
  newDraft,
  metricToDraft,
  type MetricDraft,
} from './metric-detail';
import {
  SCORE_TYPE_META,
  TIERS,
  TIER_META,
  type ScoreFilter,
  type TierFilter,
} from './metric-meta';
import { MetricRow } from './metric-row';

import type { CustomMetricPublic } from '@/client/types.gen';

export function MetricsPage() {
  const { rows, isLoading, error } = useCustomMetrics();
  const createMutation = useCreateCustomMetric();
  const updateMutation = useUpdateCustomMetric();
  const deleteMutation = useDeleteCustomMetric();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [draftOpen, setDraftOpen] = useState(false);
  const [checkedIds, setCheckedIds] = useState<Set<string>>(new Set());
  const [tierFilter, setTierFilter] = useState<TierFilter>('all');
  const [scoreFilter, setScoreFilter] = useState<ScoreFilter>('all');
  const [deleteTarget, setDeleteTarget] = useState<CustomMetricPublic[] | null>(null);
  const [savedFlash, setSavedFlash] = useState(false);

  const selectAllRef = useRef<HTMLInputElement>(null);

  const filtered = useMemo(
    () =>
      rows.filter((m) => {
        if (tierFilter !== 'all' && m.tier !== tierFilter) return false;
        if (scoreFilter !== 'all' && m.score_type !== scoreFilter) return false;
        return true;
      }),
    [rows, tierFilter, scoreFilter]
  );

  const selectedMetric = useMemo(
    () => rows.find((m) => m.id === selectedId) ?? null,
    [rows, selectedId]
  );

  const detailSource: MetricDraft | null = draftOpen
    ? newDraft()
    : selectedMetric
      ? metricToDraft(selectedMetric)
      : null;

  const allChecked =
    filtered.length > 0 && filtered.every((m) => checkedIds.has(m.id));
  const someChecked = !allChecked && filtered.some((m) => checkedIds.has(m.id));

  useEffect(() => {
    if (selectAllRef.current) {
      selectAllRef.current.indeterminate = someChecked;
    }
  }, [someChecked]);

  const handleSelectAll = (checked: boolean) => {
    setCheckedIds((prev) => {
      const next = new Set(prev);
      if (checked) {
        filtered.forEach((m) => next.add(m.id));
      } else {
        filtered.forEach((m) => next.delete(m.id));
      }
      return next;
    });
  };

  const handleCheck = (id: string, checked: boolean) => {
    setCheckedIds((prev) => {
      const next = new Set(prev);
      if (checked) next.add(id);
      else next.delete(id);
      return next;
    });
  };

  const handleToggleActive = (id: string, active: boolean) => {
    updateMutation.mutate({
      metricId: id,
      body: { include_in_defaults: active },
    });
  };

  const handleAddMetric = () => {
    setSelectedId(null);
    setDraftOpen(true);
  };

  const flashSaved = () => {
    setSavedFlash(true);
    setTimeout(() => setSavedFlash(false), 2000);
  };

  const handleSave: React.ComponentProps<typeof MetricDetail>['onSave'] = (
    patch,
    draft
  ) => {
    if (draft.id === null) {
      createMutation.mutate(
        {
          name: draft.name,
          display_name: draft.display_name,
          description: draft.description,
          tier: draft.tier,
          default_weight: 1.0,
          score_type: draft.score_type,
          rubric: draft.rubric,
          include_in_defaults: draft.active,
        },
        {
          onSuccess: (created) => {
            setDraftOpen(false);
            setSelectedId(created.id);
            flashSaved();
          },
        }
      );
    } else {
      updateMutation.mutate(
        { metricId: draft.id, body: patch },
        { onSuccess: () => flashSaved() }
      );
    }
  };

  const handleDeleteFromDetail = () => {
    if (!selectedMetric) return;
    setDeleteTarget([selectedMetric]);
  };

  const handleBulkDelete = () => {
    const targets = rows.filter((m) => checkedIds.has(m.id));
    if (targets.length > 0) setDeleteTarget(targets);
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    const ids = deleteTarget.map((m) => m.id);
    await Promise.all(ids.map((id) => deleteMutation.mutateAsync(id).catch(() => null)));
    setCheckedIds((prev) => {
      const next = new Set(prev);
      ids.forEach((id) => next.delete(id));
      return next;
    });
    if (selectedId && ids.includes(selectedId)) setSelectedId(null);
    setDeleteTarget(null);
  };

  const closeDetail = () => {
    setSelectedId(null);
    setDraftOpen(false);
  };

  const showDetail = detailSource !== null;

  return (
    <div className="flex h-full overflow-hidden bg-background">
      <div
        className={cn(
          'flex flex-col min-h-0 transition-all',
          showDetail ? 'w-1/3' : 'flex-1'
        )}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-border shrink-0">
          <div className="flex items-center gap-2.5">
            <BarChart3 className="w-4 h-4 text-muted-foreground" />
            <h1 className="text-sm text-foreground">Metrics</h1>
          </div>
          <Button
            size="sm"
            variant="outline"
            className="gap-1.5 h-7 text-xs"
            onClick={handleAddMetric}
          >
            <Plus className="w-3 h-3" />
            New metric
          </Button>
        </div>

        <div className="flex items-center justify-between px-5 py-2 border-b border-border shrink-0">
          {checkedIds.size > 0 ? (
            <div className="flex items-center gap-3">
              <span className="text-xs text-foreground">
                <span className="tabular-nums">{checkedIds.size}</span> selected
              </span>
              <button
                onClick={handleBulkDelete}
                className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 transition-colors"
                type="button"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Delete selected
              </button>
              <button
                onClick={() => setCheckedIds(new Set())}
                className="text-xs text-muted-foreground/50 hover:text-muted-foreground transition-colors"
                type="button"
              >
                Clear
              </button>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">
              {isLoading
                ? 'Loading…'
                : error
                  ? error
                  : `${filtered.length}${filtered.length !== rows.length ? ` of ${rows.length}` : ''} metric${rows.length === 1 ? '' : 's'}`}
            </p>
          )}
        </div>

        <div className="flex items-center px-4 py-2 border-b border-border shrink-0 gap-2 flex-wrap">
          <div className="flex items-center gap-0.5 bg-accent/40 rounded-md p-0.5 shrink-0">
            {(['all', ...TIERS] as TierFilter[]).map((t) => (
              <FilterPill
                key={t}
                active={tierFilter === t}
                onClick={() => setTierFilter(t)}
              >
                {t === 'all' ? 'All tiers' : TIER_META[t].label}
              </FilterPill>
            ))}
          </div>

          <div className="w-px h-4 bg-border shrink-0" />

          <div className="flex items-center gap-0.5 bg-accent/40 rounded-md p-0.5 shrink-0">
            {(['all', 'scored', 'binary'] as ScoreFilter[]).map((s) => (
              <FilterPill
                key={s}
                active={scoreFilter === s}
                onClick={() => setScoreFilter(s)}
              >
                {s === 'all' ? 'All types' : SCORE_TYPE_META[s].label}
              </FilterPill>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-[32px_2fr_1fr_1fr_72px] border-b border-border shrink-0 px-5 items-center">
          <div className="py-2 flex items-center">
            <input
              ref={selectAllRef}
              type="checkbox"
              checked={allChecked}
              onChange={(e) => handleSelectAll(e.target.checked)}
              className="w-3.5 h-3.5 rounded border-border accent-foreground cursor-pointer"
              title={allChecked ? 'Deselect all' : 'Select all'}
            />
          </div>
          <div className="py-2 text-[10px] text-muted-foreground/50 uppercase tracking-wider">
            Name
          </div>
          <div className="py-2 text-[10px] text-muted-foreground/50 uppercase tracking-wider">
            Tier
          </div>
          <div className="py-2 text-[10px] text-muted-foreground/50 uppercase tracking-wider">
            Score type
          </div>
          <div className="py-2 text-[10px] text-muted-foreground/50 uppercase tracking-wider">
            Active
          </div>
        </div>

        <div className="flex-1 overflow-auto">
          {filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full gap-3 text-muted-foreground/40">
              <BarChart3 className="w-8 h-8" />
              <p className="text-sm">
                {isLoading
                  ? 'Loading metrics…'
                  : rows.length === 0
                    ? 'No metrics yet — create your first one.'
                    : 'No metrics match the current filters'}
              </p>
            </div>
          ) : (
            filtered.map((m) => (
              <MetricRow
                key={m.id}
                metric={m}
                isSelected={selectedId === m.id}
                isChecked={checkedIds.has(m.id)}
                onSelect={(id) => {
                  setDraftOpen(false);
                  setSelectedId(selectedId === id ? null : id);
                }}
                onCheck={handleCheck}
                onToggleActive={handleToggleActive}
              />
            ))
          )}
        </div>
      </div>

      {detailSource && (
        <div className="flex-1 min-w-0 overflow-hidden">
          <MetricDetail
            key={detailSource.id ?? 'draft'}
            source={detailSource}
            saved={savedFlash}
            saving={createMutation.isPending || updateMutation.isPending}
            onSave={handleSave}
            onDelete={handleDeleteFromDetail}
            onClose={closeDetail}
          />
        </div>
      )}

      <DeleteConfirmDialog
        items={deleteTarget}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
        isPending={deleteMutation.isPending}
      />
    </div>
  );
}
