import { queryOptions } from '@tanstack/react-query';

import { listCustomMetrics } from '@/actions/custom-metrics';
import { customMetricKeys } from '@/constants/query-keys';

export const CustomMetricService = {
  getCustomMetricsQuery: () =>
    queryOptions({
      queryKey: customMetricKeys.list(),
      queryFn: () => listCustomMetrics(),
    }),
};
