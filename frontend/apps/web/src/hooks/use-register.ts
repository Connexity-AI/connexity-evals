'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';

import { registerAction } from '@/actions/auth';
import { registerFormSchema } from '@/schemas/forms';
import { isErrorApiResult, isSuccessApiResult } from '@/utils/api';
import { getApiErrorMessage } from '@/utils/error';

import type { RegisterFormValues } from '@/types/forms';

const resolver = zodResolver(registerFormSchema);

const defaultValues: RegisterFormValues = {
  email: '',
  full_name: '',
  password: '',
  confirm_password: '',
} as const;

export function useRegister() {
  const form = useForm<RegisterFormValues>({ resolver, defaultValues });

  const mutation = useMutation({
    mutationFn: (values: RegisterFormValues) => {
      const { confirm_password: _, ...body } = values;
      return registerAction(body);
    },
  });

  const onSubmit = (values: RegisterFormValues) => mutation.mutate(values);

  const error =
    mutation.data && isErrorApiResult(mutation.data)
      ? getApiErrorMessage(mutation.data.error)
      : null;

  const success = mutation.data ? isSuccessApiResult(mutation.data) : false;

  return { form, onSubmit, error, success, isPending: mutation.isPending };
}
