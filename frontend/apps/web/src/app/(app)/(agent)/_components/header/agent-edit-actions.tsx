'use client';

import { GitBranch, Loader2, Upload } from 'lucide-react';

import { Button } from '@workspace/ui/components/ui/button';

import { useAgentEditFormActions } from '@/app/(app)/(agent)/_context/agent-edit-form-context';
import { useVersions } from '@/app/(app)/(agent)/_context/versions-context';
import { useDelayedFlag } from '@/app/(app)/(agent)/_hooks/use-delayed-flag';

export function AgentEditActions() {
  const { onSubmit, isPending, isReadOnly, isDraftSaving } =
    useAgentEditFormActions();
  const { openDrawer } = useVersions();
  const showSaving = useDelayedFlag(isDraftSaving, 300);

  return (
    <div className="flex items-center gap-2">
      {showSaving && (
        <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Loader2 size={14} className="animate-spin" />
          Saving...
        </span>
      )}

      <Button
        variant="outline"
        icon={GitBranch}
        size="sm"
        className="gap-1.5"
        onClick={openDrawer}
      />

      <Button
        size="sm"
        className="gap-1.5"
        onClick={onSubmit}
        disabled={isPending || isReadOnly}
      >
        <Upload className="w-3.5 h-3.5" />
        {isPending ? 'Publishing...' : 'Publish'}
      </Button>
    </div>
  );
}
