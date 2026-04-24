import { differenceInHours, differenceInMinutes, format } from 'date-fns';

export interface TranscriptTurn {
  role?: string;
  content?: string;
  words?: Array<{ start?: number; end?: number; word?: string }>;
  start?: number;
  timestamp?: number | string;
}

export function extractTurns(raw: unknown): TranscriptTurn[] {
  if (!Array.isArray(raw)) return [];
  return raw.filter((t): t is TranscriptTurn => typeof t === 'object' && t !== null);
}

/** Returns the message start time in seconds, or null if not derivable. */
export function turnStartSeconds(turn: TranscriptTurn): number | null {
  const firstWordStart = turn.words?.[0]?.start;
  if (typeof firstWordStart === 'number') return firstWordStart;
  if (typeof turn.start === 'number') return turn.start;
  if (typeof turn.timestamp === 'number') return turn.timestamp;
  return null;
}

/** Formats seconds as `m:ss` (e.g. 65 → "1:05"). */
export function formatTimestamp(seconds: number): string {
  const total = Math.max(0, Math.floor(seconds));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function formatRelativeDay(date: Date): string {
  const now = new Date();
  const mins = differenceInMinutes(now, date);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = differenceInHours(now, date);
  if (hrs < 24) return `${hrs}h ago`;
  return format(date, 'MMM d, yyyy');
}

function formatClockTime(date: Date): string {
  return format(date, 'h:mm a');
}

export function formatDate(iso: string): string {
  const date = new Date(iso);
  return `${formatRelativeDay(date)} · ${formatClockTime(date)}`;
}

export function formatDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined) return '—';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}
