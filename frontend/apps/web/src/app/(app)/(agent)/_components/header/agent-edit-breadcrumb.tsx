'use client';

import Link from 'next/link';

import { UrlGenerator } from '@/common/url-generator/url-generator';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from '@workspace/ui/components/ui/breadcrumb';
import { Separator } from '@workspace/ui/components/ui/separator';
import { SidebarTrigger } from '@workspace/ui/components/ui/sidebar';

import { EditableBreadcrumbName } from '@/app/(app)/(agent)/_components/header/editable-breadcrumb-name';
import { useAgentEditFormActions } from '@/app/(app)/(agent)/_context/agent-edit-form-context';

export function AgentEditBreadcrumb() {
  const { agentName, agentId } = useAgentEditFormActions();

  return (
    <div className="flex items-center gap-3">
      <SidebarTrigger />

      <Separator orientation="vertical" className="h-5" />

      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href={UrlGenerator.agents()}>Agents</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>

          <BreadcrumbSeparator />

          <EditableBreadcrumbName agentId={agentId} agentName={agentName} />
        </BreadcrumbList>
      </Breadcrumb>
    </div>
  );
}
