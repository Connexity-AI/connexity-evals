import Link from 'next/link';

import { BarChart3, Bot } from 'lucide-react';

import {
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  Sidebar as UISidebar,
} from '@workspace/ui/components/ui/sidebar';

import WithIsActive from '@/components/dashboard/layout/with-is-active';
import { UrlGenerator } from '@/common/url-generator/url-generator';

import type { UserPublic } from '@/client/types.gen';
import type { FC } from 'react';

interface Props {
  currentUser?: UserPublic;
}

const menuItems = [
  {
    title: 'Agents',
    url: UrlGenerator.agents(),
    icon: Bot,
  },
  {
    title: 'Metrics',
    url: UrlGenerator.metrics(),
    icon: BarChart3,
  },
];

const Sidebar: FC<Props> = async ({ currentUser }) => {
  return (
    <UISidebar collapsible="icon" className="border-r bg-card dark:bg-zinc-900">
      {currentUser && (
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                {menuItems.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    {/* passes isActive prop */}
                    <WithIsActive url={item.url}>
                      <SidebarMenuButton
                        asChild
                        tooltip={item.title}
                        className="text-muted-foreground hover:text-foreground hover:bg-accent dark:hover:bg-zinc-800 data-[state=open]:bg-accent dark:data-[state=open]:bg-zinc-800"
                      >
                        <Link href={item.url} className="flex items-center gap-3">
                          <item.icon className="h-5 w-5" />
                          <span className="text-base">{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </WithIsActive>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      )}

      {currentUser?.email && (
        <SidebarFooter className="p-6 group-data-[collapsible=icon]:p-2">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            <p className="group-data-[collapsible=icon]:hidden">Logged in as:</p>
            <p className="font-medium group-data-[collapsible=icon]:hidden">{currentUser.email}</p>
          </div>
        </SidebarFooter>
      )}
    </UISidebar>
  );
};

export default Sidebar;
