'use client';

import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@workspace/ui/components/ui/tabs';
import { cn } from '@workspace/ui/lib/utils';

import { TABS } from '@/app/(app)/(new-agent)/agents/new/_constants/agent';
import { PromptTab } from '@/app/(app)/(new-agent)/agents/new/_components/prompt-tab';
import { SettingsTab } from '@/app/(app)/(new-agent)/agents/new/_components/settings-tab';

const triggerClassName = cn(
  'relative rounded-none bg-transparent px-5 py-3 text-sm font-medium shadow-none',
  'transition-colors duration-150 select-none',
  'after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:rounded-t-full after:transition-all after:duration-150',
  'data-[state=active]:bg-transparent data-[state=active]:text-foreground data-[state=active]:shadow-none data-[state=active]:after:bg-foreground',
  'data-[state=inactive]:text-muted-foreground data-[state=inactive]:after:bg-transparent',
  'hover:text-foreground hover:after:bg-border',
  'focus-visible:ring-0 focus-visible:ring-offset-0'
);

const NewAgentPage = () => {
  return (
    <Tabs defaultValue="prompt" className="flex flex-col h-full">
      <TabsList className="h-auto w-full justify-start rounded-none bg-transparent p-0 border-b border-border">
        {TABS.map((tab) => (
          <TabsTrigger key={tab.id} value={tab.id} className={triggerClassName}>
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>

      <PromptTab />

      {/* Tools Tab */}
      <TabsContent value="tools" className="flex-1 mt-0 p-6">
        <div className="text-muted-foreground">
          <h2 className="text-lg font-semibold text-foreground mb-2">Tools</h2>
          <p>Define and configure agent tools here.</p>
        </div>
      </TabsContent>

      <SettingsTab />
    </Tabs>
  );
};

export default NewAgentPage;
