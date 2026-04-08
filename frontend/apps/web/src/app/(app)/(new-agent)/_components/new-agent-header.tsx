'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import { UrlGenerator } from '@/common/url-generator/url-generator';
import { Plus } from 'lucide-react';
import { useQueryState } from 'nuqs';

import { Button } from '@workspace/ui/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@workspace/ui/components/ui/dialog';
import { Input } from '@workspace/ui/components/ui/input';
import { Separator } from '@workspace/ui/components/ui/separator';
import { SidebarTrigger } from '@workspace/ui/components/ui/sidebar';

import { PlatformHeader } from '@/components/common/platform-header';

export const NewAgentHeader = () => {
  return <PlatformHeader className="px-6" leading={<Leading />} trailing={<Trailing />} />;
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
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [name, setName] = useQueryState('name', {
    shallow: false,
    defaultValue: '',
  });

  const handleCreate = () => {
    const trimmed = name.trim();
    if (!trimmed) return;
    router.push(UrlGenerator.newAgent({ values: { name: trimmed } }));
  };

  const handleOpenChange = (value: boolean) => {
    setOpen(value);
    if (!value) setName(null);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus className="size-4" />
          Add Agent
        </Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create new agent</DialogTitle>

          <DialogDescription>Give your agent a name to get started.</DialogDescription>
        </DialogHeader>
        <Input
          placeholder="Agent name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleCreate();
          }}
          autoFocus
        />

        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreate} disabled={!name.trim()}>
            Create
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
