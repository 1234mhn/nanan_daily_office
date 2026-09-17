import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'export',
  basePath: '/korean-app',
  assetPrefix: '/korean-app',
  images: {
    unoptimized: true,
  },
}

export default nextConfig
