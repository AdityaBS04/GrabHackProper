const path = require("path");

/**
 * Create React App resolves `baseUrl` but refuses tsconfig `paths`, so the
 * `@/…` alias that shadcn components ship with needs a webpack alias. craco
 * layers that onto react-scripts without ejecting.
 */
module.exports = {
  webpack: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
};
