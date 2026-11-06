/** @type {import('next').NextConfig} */
const backendUrl = (
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  ""
).replace(/\/$/, "");

// Only proxy API requests if an actual external backend URL is configured (prevents Vercel DNS_HOSTNAME_RESOLVED_PRIVATE error)
const isExternalBackend = Boolean(
  backendUrl &&
  (backendUrl.startsWith("http://") || backendUrl.startsWith("https://")) &&
  !backendUrl.includes("localhost") &&
  !backendUrl.includes("127.0.0.1")
);

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  async rewrites() {
    if (!isExternalBackend) {
      return [];
    }
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
      {
        source: "/health",
        destination: `${backendUrl}/health`,
      },
    ];
  },
};

export default nextConfig;
