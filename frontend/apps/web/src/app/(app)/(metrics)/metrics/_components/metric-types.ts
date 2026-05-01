import type { CustomMetricPublic, CustomMetricUpdate } from '@/client/types.gen';

/**
 * The generated client (Hey API) is regenerated from the backend OpenAPI
 * schema by `bash scripts/generate-client.sh`. Until that script runs, the
 * generated types do not yet expose ``is_predefined`` and ``is_draft`` even
 * though the backend now returns / accepts them.
 *
 * These augmenting aliases let the UI consume those fields safely; once the
 * client is regenerated, the intersection becomes a no-op and these aliases
 * can be replaced with the bare generated types.
 */
export type MetricFlags = {
  is_predefined?: boolean;
  is_draft?: boolean;
};

export type MetricRecord = CustomMetricPublic & MetricFlags;

export type MetricUpdatePatch = CustomMetricUpdate & {
  is_draft?: boolean | null;
};
