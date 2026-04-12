import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  build: {
    outDir: "build",
    lib: {
      entry: "./src/index.ts",
      formats: ["es"],
      fileName: "index-[hash]",
    },
    rollupOptions: {
      output: {
        entryFileNames: "index-[hash].js",
        assetFileNames: "styles-[hash][extname]",
      },
    },
    minify: "esbuild",
    sourcemap: false,
  },
  define: {
    "process.env.NODE_ENV": JSON.stringify(
      process.env.NODE_ENV || "production"
    ),
  },
});
