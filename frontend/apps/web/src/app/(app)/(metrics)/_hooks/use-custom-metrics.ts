'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  createCustomMetric,
  deleteCustomMetric,
  updateCustomMetric,
} from '@/actions/custom-metrics';
import { CustomMetricService } from '@/app/(app)/(metrics)/_service';
import { customMetricKeys } from '@/constants/query-keys';
import { isErrorApiResult } from '@/utils/api';
import { getApiErrorMessage } from '@/utils/error';

import type {
  CustomMetricCreate,
  CustomMetricPublic,
  CustomMetricUpdate,
} from '@/client/types.gen';

export function useCustomMetrics() {
  const query = useQuery(CustomMetricService.getCustomMetricsQuery());

  const rows: CustomMetricPublic[] =
    query.data && !isErrorApiResult(query.data) ? query.data.data.data : [];

  return {
    rows,
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    error:
      query.data && isErrorApiResult(query.data)
        ? getApiErrorMessage(query.data.error)
        : null,
  };
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
    mutationFn: async ({
      metricId,
      body,
    }: {
      metricId: string;
      body: CustomMetricUpdate;
    }) => {
      const result = await updateCustomMetric(metricId, body);
      if (isErrorApiResult(result)) {
        throw new Error(getApiErrorMessage(result.error));
      }
      return result.data;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: customMetricKeys.all });
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
    },
  });

  return {
    mutate: mutation.mutate,
    mutateAsync: mutation.mutateAsync,
    isPending: mutation.isPending,
    error: mutation.error?.message ?? null,
  };
}
