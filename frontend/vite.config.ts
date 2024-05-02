import path from "node:path";
import { defineConfig } from "vite";
import Vue from "@vitejs/plugin-vue";
import Components from "unplugin-vue-components/vite";
import AutoImport from "unplugin-auto-import/vite";
import VueMacros from "unplugin-vue-macros/vite";

export default defineConfig({
  resolve: {
    alias: {
      "@/": `${path.resolve(__dirname, "src")}/`,
    },
  },
  plugins: [
    VueMacros({
      defineOptions: false,
      defineModels: false,
      plugins: {
        vue: Vue({
          script: {
            propsDestructure: true,
            defineModel: true,
          },
        }),
      },
    }),

    // https://github.com/antfu/unplugin-auto-import
    AutoImport({
      imports: [
        "vue",
        "@vueuse/core",
        {
          // add any other imports you were relying on
          "vue-router/auto": ["useLink"],
        },
      ],
      dts: true,
      dirs: ["./src/composables"],
      vueTemplate: true,
    }),

    // https://github.com/antfu/vite-plugin-components
    Components({
      dts: true,
    }),
  ],

  // https://github.com/vitest-dev/vitest
  test: {
    environment: "jsdom",
  },

  server: {
    host: true,
    port: 8080,
    proxy: {
      "/sockjs-node": {
        target: "ws://127.0.0.1:8081",
        ws: true,
      },
    },
    hmr: {
      path: "/sockjs-node",
      port: 8081,
      clientPort: 443,
    },
  },
});
