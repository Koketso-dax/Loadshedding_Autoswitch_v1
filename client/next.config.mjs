/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
        return [
          {
            source: '/api/:path*',
            destination: 'http://web-01.koketsodiale.tech/api/:path*',
          },
        ];
      },
};

export default nextConfig;
