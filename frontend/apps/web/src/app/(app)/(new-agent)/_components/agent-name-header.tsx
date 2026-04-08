'use client';

import Link from 'next/link';

import { UrlGenerator } from '@/common/url-generator/url-generator';
import { parseAsString, useQueryState } from 'nuqs';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@workspace/ui/components/ui/breadcrumb';
import { Separator } from '@workspace/ui/components/ui/separator';
import { SidebarTrigger } from '@workspace/ui/components/ui/sidebar';

import { PlatformHeader } from '@/components/common/platform-header';

export const AgentNameHeader = () => {
  const [name] = useQueryState('name', parseAsString.withDefault(''));

  return (
    <PlatformHeader
      className="px-6"
      leading={
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

              <BreadcrumbItem>
                <BreadcrumbPage>{name || 'New Agent'}</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </div>
      }
    />
  );
};
