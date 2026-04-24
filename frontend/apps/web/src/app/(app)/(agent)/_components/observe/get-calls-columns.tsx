'use client';

import { Clock, FlaskConical } from 'lucide-react';

import type { ColumnDef } from '@tanstack/react-table';

import type { CallRow } from '@/actions/calls';

function formatCallDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined) return '—';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export const getCallsColumns = (): ColumnDef<CallRow>[] => [
  {
    accessorKey: 'started_at',
    header: 'Date',
    enableSorting: false,
    cell: ({ row }) => (
      <div className="flex min-w-0 items-center gap-2">
        <span className="truncate text-sm text-foreground tabular-nums">
          {formatCallDate(row.original.started_at)}
        </span>
        {row.original.is_new ? (
          <span className="inline-flex items-center rounded border border-violet-500/25 bg-violet-500/15 px-1.5 py-px align-middle text-[9px] text-violet-300">
            New
          </span>
        ) : null}
      </div>
    ),
  },
  {
    accessorKey: 'duration_seconds',
    header: 'Duration',
    enableSorting: false,
    cell: ({ row }) => (
      <div className="flex items-center gap-1.5 text-xs tabular-nums text-muted-foreground">
        <Clock className="h-3 w-3" />
        {formatDuration(row.original.duration_seconds)}
      </div>
    ),
  },
  {
    accessorKey: 'test_case_count',
    header: 'Test Cases',
    enableSorting: false,
    cell: ({ row }) => {
      const count = row.original.test_case_count ?? 0;
      return (
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <FlaskConical className="h-3 w-3" />
          <span className="tabular-nums text-foreground">{count}</span>
          <span className="text-muted-foreground/60">
            {count === 1 ? 'test case' : 'test cases'}
          </span>
        </div>
      );
    },
  },
];
