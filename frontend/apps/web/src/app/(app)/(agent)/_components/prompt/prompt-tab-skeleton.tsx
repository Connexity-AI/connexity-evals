'use client';

import { Skeleton } from '@workspace/ui/components/ui/skeleton';
import { TabsContent } from '@workspace/ui/components/ui/tabs';
import { cn } from '@workspace/ui/lib/utils';

// Silhouette of the filled prompt textarea — section headings and paragraph
// blocks of varying widths, matching the structure of a typical agent prompt
// (identity, voice guidelines, formatting rules, etc.).

export function PromptTabSkeleton() {
  return (
    <TabsContent value="prompt" className="flex-1 mt-0 p-6 flex flex-col min-h-0">
      <div className="w-full flex-1 rounded-md border border-input bg-background/30 p-4 space-y-5 overflow-hidden">
        <PromptSection headingWidth="w-32" lineWidths={['w-full', 'w-[92%]', 'w-[78%]']} />
        <PromptSection
          headingWidth="w-48"
          lineWidths={['w-full', 'w-[88%]', 'w-[95%]', 'w-[70%]']}
        />
        <PromptSection headingWidth="w-28" lineWidths={['w-full', 'w-[85%]']} />
        <PromptSection
          headingWidth="w-40"
          lineWidths={['w-full', 'w-[90%]', 'w-[82%]', 'w-[65%]']}
        />
      </div>
    </TabsContent>
  );
}

interface PromptSectionProps {
  headingWidth: string;
  lineWidths: string[];
}

function PromptSection({ headingWidth, lineWidths }: PromptSectionProps) {
  return (
    <div className="space-y-2">
      <Skeleton className={cn('h-3.5', headingWidth)} />
      {lineWidths.map((width, index) => (
        <Skeleton key={index} className={cn('h-3', width)} />
      ))}
    </div>
  );
}
