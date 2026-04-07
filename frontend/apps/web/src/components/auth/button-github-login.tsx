import Link from 'next/link';

import IconsCustom from '@workspace/ui/components/icons-custom';
import { Button } from '@workspace/ui/components/ui/button';
import { cn } from '@workspace/ui/lib/utils';

import { UrlGenerator } from '@/common/url-generator/url-generator';
import { getPublicEnv } from '@/config/process-env';

import type { FC } from 'react';

interface Props {
  className?: string;
}

const { GitHub } = IconsCustom;

const ButtonGithubLogin: FC<Props> = async ({ className }) => {
  const { API_URL } = getPublicEnv();

  // Note: BROWSER (<a/> or <Link />) must call this API url, not http client or server
  const absoluteApiUrl = `${API_URL}${UrlGenerator.apiLoginGithub()}`;

  return (
    <Button
      asChild
      variant="outline"
      className={cn('w-full h-auto px-4 py-2.5 flex items-center justify-center gap-2', className)}
    >
      <Link href={absoluteApiUrl}>
        <GitHub className="w-5 h-5" />
        Sign in with GitHub
      </Link>
    </Button>
  );
};

export default ButtonGithubLogin;
