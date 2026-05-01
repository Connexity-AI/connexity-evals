'use client';

import { useEffect, useState } from 'react';

import { Button } from '@workspace/ui/components/ui/button';
import { Input } from '@workspace/ui/components/ui/input';
import { Switch } from '@workspace/ui/components/ui/switch';
import { Textarea } from '@workspace/ui/components/ui/textarea';
import { cn } from '@workspace/ui/lib/utils';
import { Check, Trash2, X } from 'lucide-react';

import { ScoreTypeBadge, TierBadge } from './metric-badges';
import {
  SCORE_TYPES,
  SCORE_TYPE_META,
  TIERS,
  TIER_META,
  isValidSnakeCase,
} from './metric-meta';

import type {
  CustomMetricPublic,
  CustomMetricUpdate,
  MetricTier,
  ScoreType,
} from '@/client/types.gen';

export type MetricDraft = {
  id: string | null;
  name: string;
  display_name: string;
  description: string;
  tier: MetricTier;
  score_type: ScoreType;
  rubric: string;
  active: boolean;
};

export function metricToDraft(metric: CustomMetricPublic): MetricDraft {
  return {
    id: metric.id,
    name: metric.name,
    display_name: metric.display_name,
    description: metric.description ?? '',
    tier: metric.tier,
    score_type: metric.score_type,
    rubric: metric.rubric,
    active: !!metric.include_in_defaults,
  };
}

export function newDraft(): MetricDraft {
  return {
    id: null,
    name: '',
    display_name: '',
    description: '',
    tier: 'execution',
    score_type: 'scored',
    rubric: '',
    active: true,
  };
}

export function MetricDetail({
  source,
  saved,
  saving,
  onSave,
  onDelete,
  onClose,
}: {
  source: MetricDraft;
  saved: boolean;
  saving: boolean;
  onSave: (patch: CustomMetricUpdate, draft: MetricDraft) => void;
  onDelete: () => void;
  onClose: () => void;
}) {
  const [name, setName] = useState(source.name);
  const [displayName, setDisplayName] = useState(source.display_name);
  const [description, setDescription] = useState(source.description);
  const [tier, setTier] = useState<MetricTier>(source.tier);
  const [scoreType, setScoreType] = useState<ScoreType>(source.score_type);
  const [rubric, setRubric] = useState(source.rubric);
  const [active, setActive] = useState(source.active);

  useEffect(() => {
    setName(source.name);
    setDisplayName(source.display_name);
    setDescription(source.description);
    setTier(source.tier);
    setScoreType(source.score_type);
    setRubric(source.rubric);
    setActive(source.active);
    // Reset only when switching to a different metric — re-syncing on every
    // field change would clobber unsaved edits.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [source.id]);

  const isDirty =
    name !== source.name ||
    displayName !== source.display_name ||
    description !== source.description ||
    tier !== source.tier ||
    scoreType !== source.score_type ||
    rubric !== source.rubric ||
    active !== source.active;

  const nameValid = isValidSnakeCase(name);
  const canSave = nameValid && (source.id === null || isDirty) && !saving;

  const discard = () => {
    setName(source.name);
    setDisplayName(source.display_name);
    setDescription(source.description);
    setTier(source.tier);
    setScoreType(source.score_type);
    setRubric(source.rubric);
    setActive(source.active);
  };

  const handleSave = () => {
    if (!canSave) return;
    onSave(
      {
        name,
        display_name: displayName,
        description,
        tier,
        score_type: scoreType,
        rubric,
        include_in_defaults: active,
      },
      { ...source, name, display_name: displayName, description, tier, score_type: scoreType, rubric, active }
    );
  };

  return (
    <div className="flex flex-col h-full border-l border-border bg-background">
      <div className="flex items-center justify-between px-5 py-3 border-b border-border shrink-0">
        <div className="flex items-center gap-2">
          <TierBadge tier={tier} />
          <ScoreTypeBadge type={scoreType} />
        </div>
        <div className="flex items-center gap-2">
          {isDirty && source.id !== null && (
            <Button
              size="sm"
              variant="ghost"
              className="h-7 text-xs text-muted-foreground hover:text-foreground"
              onClick={discard}
            >
              Discard
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            className={cn(
              'h-7 text-xs gap-1.5 transition-colors',
              saved && 'border-green-500/40 text-green-400'
            )}
            onClick={handleSave}
            disabled={!canSave}
          >
            {saved ? (
              <>
                <Check className="w-3 h-3" />
                Saved
              </>
            ) : source.id === null ? (
              'Create metric'
            ) : (
              'Save changes'
            )}
          </Button>
          {source.id !== null && (
            <button
              onClick={onDelete}
              className="text-muted-foreground/50 hover:text-red-400 transition-colors ml-1"
              title="Delete metric"
              type="button"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onClose}
            className="text-muted-foreground/50 hover:text-foreground transition-colors"
            type="button"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto px-5 py-4 space-y-5">
        <div className="flex items-center justify-between py-2 px-3 rounded-md border border-border bg-accent/20">
          <div>
            <p className="text-xs text-foreground">Active</p>
            <p className="text-[10px] text-muted-foreground/60 mt-0.5">
              {active
                ? 'This metric is included in eval runs.'
                : 'This metric is disabled globally and excluded from eval runs.'}
            </p>
          </div>
          <Switch
            checked={active}
            onCheckedChange={setActive}
            className="h-4 w-7 [&>span]:h-3 [&>span]:w-3 data-[state=checked]:bg-green-500/80"
          />
        </div>

        <div>
          <label className="block text-[10px] text-muted-foreground/60 uppercase tracking-wider mb-1.5">
            Display name
          </label>
          <Input
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="e.g. Tool Routing"
            className="h-8 text-xs bg-accent/40 border-border"
          />
        </div>

        <div>
          <label className="block text-[10px] text-muted-foreground/60 uppercase tracking-wider mb-1.5">
            Description
          </label>
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="One-line summary of what this metric measures"
            className="h-8 text-xs bg-accent/40 border-border"
          />
        </div>

        <div>
          <label className="block text-[10px] text-muted-foreground/60 uppercase tracking-wider mb-1.5">
            Internal name <span className="normal-case">(snake_case)</span>
          </label>
          <Input
            value={name}
            onChange={(e) =>
              setName(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))
            }
            placeholder="e.g. tool_routing"
            className={cn(
              'h-8 text-xs font-mono bg-accent/40 border-border',
              name && !nameValid && 'border-red-500/50 focus-visible:ring-red-500/20'
            )}
          />
          {name && !nameValid && (
            <p className="text-[10px] text-red-400 mt-1">
              Must start with a letter and contain only lowercase letters, digits, and
              underscores.
            </p>
          )}
        </div>

        <div>
          <label className="block text-[10px] text-muted-foreground/60 uppercase tracking-wider mb-1.5">
            Tier
          </label>
          <div className="grid grid-cols-2 gap-2">
            {TIERS.map((t) => {
              const m = TIER_META[t];
              return (
                <button
                  key={t}
                  type="button"
                  onClick={() => setTier(t)}
                  className={cn(
                    'flex flex-col items-start gap-0.5 px-3 py-2 rounded border text-left transition-colors',
                    tier === t
                      ? cn('border-border bg-accent/60', m.color.split(' ')[1])
                      : 'border-border bg-accent/20 text-muted-foreground hover:bg-accent/40'
                  )}
                >
                  <div className="flex items-center gap-1.5">
                    <span className={cn('w-1.5 h-1.5 rounded-full shrink-0', m.dot)} />
                    <span className="text-xs">{m.label}</span>
                  </div>
                  <span className="text-[10px] text-muted-foreground/60 leading-tight pl-3">
                    {m.description}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <label className="block text-[10px] text-muted-foreground/60 uppercase tracking-wider mb-1.5">
            Score type
          </label>
          <div className="flex gap-2">
            {SCORE_TYPES.map((st) => {
              const m = SCORE_TYPE_META[st];
              const selected = scoreType === st;
              return (
                <button
                  key={st}
                  type="button"
                  onClick={() => setScoreType(st)}
                  className={cn(
                    'flex-1 px-3 py-2 rounded border text-xs transition-colors',
                    selected
                      ? 'border-border bg-accent/60 text-foreground'
                      : 'border-border bg-accent/20 text-muted-foreground hover:bg-accent/40'
                  )}
                >
                  <div className="flex items-center gap-2">
                    <div
                      className={cn(
                        'w-3 h-3 rounded-full border-2 flex items-center justify-center shrink-0',
                        selected ? 'border-foreground' : 'border-muted-foreground/40'
                      )}
                    >
                      {selected && <div className="w-1.5 h-1.5 rounded-full bg-foreground" />}
                    </div>
                    <span>{m.label}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex flex-col flex-1">
          <label className="block text-[10px] text-muted-foreground/60 uppercase tracking-wider mb-1.5">
            Rubric
          </label>
          <Textarea
            value={rubric}
            onChange={(e) => setRubric(e.target.value)}
            placeholder={
              scoreType === 'scored'
                ? `Measures: <one-sentence summary>.\n\n5: <criterion>\n   Example: ...\n4: ...\n...`
                : `Measures: <one-sentence summary>.\n\npass: <criterion>\n   Example: ...\n\nfail: <criterion>\n   Example: ...`
            }
            className="min-h-[320px] text-xs font-mono bg-accent/40 border-border resize-none leading-relaxed"
          />
          <p className="text-[10px] text-muted-foreground/40 mt-1.5">
            {scoreType === 'scored'
              ? 'Start with “Measures: …” then list levels 5 → 0, each with an Example: line.'
              : 'Start with “Measures: …” then define pass and fail criteria, each with an Example: line.'}
          </p>
        </div>
      </div>
    </div>
  );
}
