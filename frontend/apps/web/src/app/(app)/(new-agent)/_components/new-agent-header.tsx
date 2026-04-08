import { PlatformHeader } from '@/components/common/platform-header';
import { SidebarTrigger } from '@workspace/ui/components/ui/sidebar';
import { Separator } from '@workspace/ui/components/ui/separator';
import { Button } from '@workspace/ui/components/ui/button';
import { Plus } from 'lucide-react';

export const NewAgentHeader = () => {
  return (
    <PlatformHeader
      className="px-6"
      leading={<Leading />}
      trailing={<Trailing />}
    />
  );
};

const Leading = () => {
  return (
    <div className="flex items-center gap-3">
      <SidebarTrigger />
      <Separator orientation="vertical" className="h-5" />
      <span className="text-sm font-medium">Agents</span>
    </div>
  );
};

const Trailing = () => {
  return (
    <Button size="sm">
      <Plus className="size-4" />
      Add Agent
    </Button>
  );
};
