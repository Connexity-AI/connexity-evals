'use client';

import { useTransition } from 'react';
import Link from 'next/link';

import { LogOut, Settings, User } from 'lucide-react';

import { Button } from '@workspace/ui/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@workspace/ui/components/ui/dropdown-menu';

import { SidebarTrigger } from '@workspace/ui/components/ui/sidebar';

import { logoutAction } from '@/actions/auth';
import ThemeToggle from '@/components/dashboard/layout/theme-toggle';
import { UrlGenerator } from '@/common/url-generator/url-generator';

import type { FC } from 'react';

const Header: FC = () => {
  const [isPending, startTransition] = useTransition();

  const handleLogout = () => startTransition(() => logoutAction());

  return (
    <header className="flex h-16 items-center justify-between border-b bg-card dark:bg-zinc-900 px-6">
      <div className="flex items-center space-x-4">
        <SidebarTrigger />
      </div>

      {/* Client components already */}
      <div className="flex items-center">
        <ThemeToggle />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative rounded-full">
              <div className="h-8 w-8 rounded-full bg-teal-600 flex items-center justify-center">
                <User className="h-4 w-4 text-white" />
              </div>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <Link href={UrlGenerator.settings()}>
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                <span>Profile Settings</span>
              </DropdownMenuItem>
            </Link>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <button
                type="button"
                onClick={handleLogout}
                disabled={isPending}
                className="flex w-full items-center"
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>{isPending ? 'Logging out...' : 'Logout'}</span>
              </button>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};

export default Header;
