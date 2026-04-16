'use client';

import { Skeleton } from '@workspace/ui/components/ui/skeleton';

// Silhouette of TablePagination: "Page X of Y" text + nav buttons (first,
// prev, next, last). First/last are hidden below lg, matching the real bar.

export function TablePaginationSkeleton() {
  return (
    <div className="flex items-center justify-between">
      <div className="flex w-full items-center gap-6 lg:ml-auto lg:w-fit">
        <Skeleton className="h-5 w-24" />
        <div className="ml-auto flex items-center gap-2 lg:ml-0">
          <Skeleton className="hidden h-8 w-8 rounded-md lg:block" />
          <Skeleton className="h-8 w-8 rounded-md" />
          <Skeleton className="h-8 w-8 rounded-md" />
          <Skeleton className="hidden h-8 w-8 rounded-md lg:block" />
        </div>
      </div>
    </div>
  );
}
