/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
      return [
        {
          source: '/api/colorize',
          destination: 'http://localhost:5000/colorize'
        },
      ];
    },
  };
  
  export default nextConfig;
  