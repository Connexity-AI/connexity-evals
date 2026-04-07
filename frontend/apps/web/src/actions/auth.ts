'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { LoginService, UsersService } from '@/client/sdk.gen';
import { isSuccessApiResult } from '@/utils/api';
import { AUTH_COOKIE } from '@/constants/auth';
import { UrlGenerator } from '@/common/url-generator/url-generator';
import { getPublicEnv } from '@/config/process-env';

import type { BodyLoginLoginAccessToken, UserRegister } from '@/client/types.gen';
import type { ApiResult } from '@/types/api';

export const loginAction = async (body: BodyLoginLoginAccessToken): Promise<ApiResult> => {
  const { NODE_ENV } = getPublicEnv();

  const apiResponse = await LoginService.loginAccessToken({ body });

  const { response: _, ...result } = apiResponse;

  const isSuccess = isSuccessApiResult(result);
  if (!isSuccess) return result;

  const { access_token, expires } = result.data;
  const isProd = NODE_ENV === 'production';

  const expiresDate = new Date(Number(expires) * 1000);

  const cookieStore = await cookies();

  cookieStore.set({
    name: AUTH_COOKIE,
    value: access_token,
    expires: expiresDate,
    httpOnly: true,
    secure: isProd,
    path: '/',
    sameSite: 'lax',
    domain: undefined,
  });

  return result;
};

export const registerAction = async (body: UserRegister): Promise<ApiResult> => {
  const apiResponse = await UsersService.registerUser({ body });

  const { response: _, ...result } = apiResponse;

  return result;
};

export const logoutAction = async (): Promise<void> => {
  const cookiesList = await cookies();
  cookiesList.delete(AUTH_COOKIE);

  redirect(UrlGenerator.login());
};
