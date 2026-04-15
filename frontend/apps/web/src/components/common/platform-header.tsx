import { type ReactNode } from 'react';
import { cn } from '@workspace/ui/lib/utils';

interface PlatformHeaderProps {
  leading?: ReactNode;
  trailing?: ReactNode;
  className?: string;
}

export const PlatformHeader = ({
  leading,
  trailing,
  className,
}: PlatformHeaderProps) => {
  return (
    <header
      className={cn(
        'h-16 border-b border-border flex justify-between items-center sticky top-0 z-10 bg-card dark:bg-zinc-900',
        className,
      )}
    >
      {leading}
      {trailing}
    </header>
  );
};
