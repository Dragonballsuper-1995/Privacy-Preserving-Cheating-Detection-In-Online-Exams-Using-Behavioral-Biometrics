import type { NextConfig } from "next";
import bundleAnalyzer from "@next/bundle-analyzer";

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
});

const nextConfig: NextConfig = {
  allowedDevOrigins: ["localhost", "192.168.89.1", "127.0.0.1", "172.17.16.1"],
  output: "standalone",
  experimental: {},
  async rewrites() {
    return [
      {
        source: "/health",
        destination: "http://127.0.0.1:8000/health",
      },
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
    ];
  },
};

export default withBundleAnalyzer(nextConfig);
