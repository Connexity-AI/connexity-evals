'use client';

import { useState } from 'react';
import {
  FlaskConical,
  Pencil,
  Radio,
  Rocket,
  type LucideIcon,
} from 'lucide-react';

import {
  Tabs,
  TabsList,
  TabsTrigger,
} from '@workspace/ui/components/ui/tabs';

export type AgentPageMode = 'edit' | 'evals' | 'deploy' | 'observe';

interface ModeTab {
  value: AgentPageMode;
  label: string;
  Icon: LucideIcon;
}

const MODE_TABS: ModeTab[] = [
  { value: 'edit', label: 'Edit', Icon: Pencil },
  { value: 'evals', label: 'Evals', Icon: FlaskConical },
  { value: 'deploy', label: 'Deploy', Icon: Rocket },
  { value: 'observe', label: 'Observe', Icon: Radio },
];

export function AgentModeTabs() {
  const [mode, setMode] = useState<AgentPageMode>('edit');

  return (
    <Tabs value={mode} onValueChange={(value) => setMode(value as AgentPageMode)}>
      <TabsList>
        {MODE_TABS.map(({ value, label, Icon }) => (
          <TabsTrigger key={value} value={value} className="gap-1.5 cursor-pointer">
            <Icon className="h-3.5 w-3.5" />
            {label}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
}
