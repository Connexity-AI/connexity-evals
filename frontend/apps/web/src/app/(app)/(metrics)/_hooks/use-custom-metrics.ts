'use client';

import { useMutation, useQueryClient, useSuspenseQuery } from '@tanstack/react-query';

import { CustomMetricService } from '@/app/(app)/(metrics)/_service';
import {
  createCustomMetric,
  deleteCustomMetric,
  updateCustomMetric,
} from '@/actions/custom-metrics';
import { isErrorApiResult } from '@/utils/api';
import { getApiErrorMessage } from '@/utils/error';
import { customMetricKeys, metricKeys } from '@/constants/query-keys';

import type { CustomMetricCreate, CustomMetricUpdate } from '@/client/types.gen';

export function useCustomMetrics() {
  return useSuspenseQuery(CustomMetricService.getCustomMetricsQuery());
}

export function useCreateCustomMetric() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (body: CustomMetricCreate) => {
      const result = await createCustomMetric(body);
      if (isErrorApiResult(result)) {
        throw new Error(getApiErrorMessage(result.error));
      }
      return result.data;
    },

    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: customMetricKeys.all });
      // The create-eval judge picker reads /config/available-metrics, which
      // mirrors the same active set; keep it in sync after any mutation.
      void queryClient.invalidateQueries({ queryKey: metricKeys.list() });
    },
  });

  return {
    mutate: mutation.mutate,
    mutateAsync: mutation.mutateAsync,
    isPending: mutation.isPending,
    error: mutation.error?.message ?? null,
  };
}

export function useUpdateCustomMetric() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async ({ metricId, body }: { metricId: string; body: CustomMetricUpdate }) => {
      const result = await updateCustomMetric(metricId, body);

      if (isErrorApiResult(result)) {
        throw new Error(getApiErrorMessage(result.error));
      }
      return result.data;
    },

    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: customMetricKeys.all });
      // The create-eval judge picker reads /config/available-metrics, which
      // mirrors the same active set; keep it in sync after any mutation.
      void queryClient.invalidateQueries({ queryKey: metricKeys.list() });
    },
  });

  return {
    mutate: mutation.mutate,
    mutateAsync: mutation.mutateAsync,
    isPending: mutation.isPending,
    error: mutation.error?.message ?? null,
  };
}

export function useDeleteCustomMetric() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (metricId: string) => {
      const result = await deleteCustomMetric(metricId);
      if (isErrorApiResult(result)) {
        throw new Error(getApiErrorMessage(result.error));
      }
      return result.data;
    },

    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: customMetricKeys.all });
      // The create-eval judge picker reads /config/available-metrics, which
      // mirrors the same active set; keep it in sync after any mutation.
      void queryClient.invalidateQueries({ queryKey: metricKeys.list() });
    },
  });

  return {
    mutate: mutation.mutate,
    mutateAsync: mutation.mutateAsync,
    isPending: mutation.isPending,
    error: mutation.error?.message ?? null,
  };
}
