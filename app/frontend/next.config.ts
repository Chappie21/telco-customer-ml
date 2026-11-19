import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone", // imagen Docker mínima (app/frontend/Dockerfile)
  cacheComponents: true,
  partialPrefetching: true,
};

export default nextConfig;
