'use client';

import { Skeleton } from '@workspace/ui/components/ui/skeleton';
import { TabsContent } from '@workspace/ui/components/ui/tabs';

// Silhouette of the tools tab list view — toolbar (count + add button) and
// rows matching ToolRow layout: icon square · name + method pill · params
// count · chevron.

export function ToolsTabSkeleton() {
  return (
    <TabsContent value="tools" className="flex-1 mt-0 flex flex-col min-h-0 overflow-hidden">
      <div className="flex items-center justify-between px-5 py-2.5 border-b border-border shrink-0">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-7 w-24 rounded-md" />
      </div>
      <div className="flex-1 overflow-hidden">
        {Array.from({ length: 6 }).map((_, index) => (
          <ToolRowSkeleton key={index} />
        ))}
      </div>
    </TabsContent>
  );
}

function ToolRowSkeleton() {
  return (
    <div className="flex items-center gap-4 px-5 py-4 border-b border-border">
      <Skeleton className="w-8 h-8 rounded-md shrink-0" />
      <div className="flex-1 min-w-0 space-y-2">
        <div className="flex items-center gap-2">
          <Skeleton className="h-3.5 w-40" />
          <Skeleton className="h-4 w-12 rounded" />
        </div>
        <Skeleton className="h-3 w-[70%]" />
      </div>
      <Skeleton className="h-3 w-14 shrink-0" />
      <Skeleton className="w-3.5 h-3.5 shrink-0" />
    </div>
  );
}
