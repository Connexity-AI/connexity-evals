'use client';

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@workspace/ui/components/ui/alert-dialog';

import { TierBadge } from './metric-badges';

import type { CustomMetricPublic } from '@/client/types.gen';

export function DeleteConfirmDialog({
  items,
  onConfirm,
  onCancel,
  isPending,
}: {
  items: CustomMetricPublic[] | null;
  onConfirm: () => void;
  onCancel: () => void;
  isPending?: boolean;
}) {
  const open = items !== null && items.length > 0;
  const list = items ?? [];

  return (
    <AlertDialog open={open} onOpenChange={(o) => !o && onCancel()}>
      <AlertDialogContent className="max-w-[480px]">
        <AlertDialogHeader>
          <AlertDialogTitle className="text-sm">
            Delete {list.length} metric{list.length !== 1 ? 's' : ''}?
          </AlertDialogTitle>
          <AlertDialogDescription>
            Soft-deleted metrics are hidden from the list and excluded from eval runs. This
            cannot be undone from the UI.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <div className="max-h-60 overflow-auto space-y-1 -mx-6 px-6">
          {list.map((m) => (
            <div key={m.id} className="flex items-center gap-2 py-1">
              <TierBadge tier={m.tier} />
              <span className="text-xs font-mono text-foreground">
                {m.display_name || m.name || (
                  <span className="text-muted-foreground italic">unnamed</span>
                )}
              </span>
            </div>
          ))}
        </div>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isPending}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            disabled={isPending}
            className="bg-red-500/90 hover:bg-red-500 text-white"
          >
            {isPending ? 'Deleting…' : 'Delete'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
