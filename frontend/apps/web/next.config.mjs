import { resolve } from 'path';

/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@workspace/ui'],
  output: 'standalone', // still supports SSR and API routes
  turbopack: {
    root: resolve(import.meta.dirname, '../../'), // anchor to frontend/ monorepo root
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/agents',
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
