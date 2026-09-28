import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    // The rewrite proxy defaults to a 30s timeout, but a coach reply from a
    // local 27B model routinely takes 20-70s, so the proxy was cutting
    // requests off and returning a bare 500. Allow a few minutes.
    proxyTimeout: 300_000,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8765/api/:path*",
      },
    ];
  },
};

export default nextConfig;
