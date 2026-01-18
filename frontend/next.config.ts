import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  experimental: {},
  allowedDevOrigins: ["localhost", "192.168.89.1"],
  output: "standalone",
};

export default nextConfig;
