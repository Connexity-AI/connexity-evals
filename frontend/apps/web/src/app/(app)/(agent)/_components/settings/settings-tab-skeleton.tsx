'use client';

import { Skeleton } from '@workspace/ui/components/ui/skeleton';
import { TabsContent } from '@workspace/ui/components/ui/tabs';
import { cn } from '@workspace/ui/lib/utils';

// Silhouette of the model settings form: Provider select, Model select,
// Temperature slider with value label and scale.

export function SettingsTabSkeleton() {
  return (
    <TabsContent value="settings" className="flex-1 mt-0 overflow-auto">
      <div className="px-6 pt-6 pb-2 max-w-xl">
        <p className="text-xs text-muted-foreground uppercase tracking-wider pb-3 border-b border-border">
          Model
        </p>
      </div>
      <div className="px-6 pb-6 max-w-xl space-y-8">
        <FieldSkeleton labelWidth="w-16" />
        <FieldSkeleton labelWidth="w-12" />
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Skeleton className="h-3.5 w-24" />
            <div className="flex items-center gap-2">
              <Skeleton className="h-3 w-16" />
              <Skeleton className="h-3.5 w-8" />
            </div>
          </div>
          <Skeleton className="h-2 w-full rounded-full" />
          <div className="flex justify-between">
            <Skeleton className="h-2.5 w-6" />
            <Skeleton className="h-2.5 w-6" />
            <Skeleton className="h-2.5 w-6" />
          </div>
        </div>
      </div>
    </TabsContent>
  );
}

function FieldSkeleton({ labelWidth }: { labelWidth: string }) {
  return (
    <div className="space-y-2">
      <Skeleton className={cn('h-3.5', labelWidth)} />
      <Skeleton className="h-9 w-full rounded-md" />
    </div>
  );
}
