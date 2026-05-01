import { Suspense } from 'react';

import { dehydrate } from '@tanstack/react-query';

import { CustomMetricService } from '@/app/(app)/(metrics)/_service';
import { MetricsPage } from '@/app/(app)/(metrics)/metrics/_components/metrics-page';
import { MetricsPageSkeleton } from '@/app/(app)/(metrics)/metrics/_components/metrics-page-skeleton';
import ErrorBoundary from '@/components/common/error-boundary';
import { HydrateProvider } from '@/components/common/hydrate-provider';
import getQueryClient from '@/lib/react-query/getQueryClient';

export default async function MetricsRoutePage() {
  const queryClient = getQueryClient();

  // Stream the metrics list: HTML ships immediately, the list resolves via
  // Suspense as the prefetched promise settles on the client.
  queryClient.prefetchQuery(CustomMetricService.getCustomMetricsQuery());

  const dehydratedState = dehydrate(queryClient);

  return (
    <HydrateProvider state={dehydratedState}>
      <ErrorBoundary>
        <Suspense fallback={<MetricsPageSkeleton />}>
          <MetricsPage />
        </Suspense>
      </ErrorBoundary>
    </HydrateProvider>
  );
}
