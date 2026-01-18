import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  experimental: {},
  allowedDevOrigins: ["localhost", "192.168.89.1", "6vjfqk0n-3000.inc1.devtunnels.ms"],
  output: "standalone",
};

export default nextConfig;
