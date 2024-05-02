// import { ViteSSG } from "vite-ssg";
// import App from "./App.vue";
// import type { UserModule } from "./types";

// import "./assets/css/global.scss";
// import { routes } from "./routes";

// // https://github.com/antfu/vite-ssg
// export const createApp = ViteSSG(
//   App,
//   {
//     routes,
//     base: import.meta.env.BASE_URL,
//   },
//   (ctx) => {
//     // install all modules under `modules/`
//     Object.values(
//       import.meta.glob<{ install: UserModule }>("./modules/*.ts", {
//         eager: true,
//       }),
//     ).forEach((i) => i.install?.(ctx));
//   },
// );

import "./assets/css/global.scss";
import { createApp } from "vue";
import App from "./App.vue";

import { router } from "./modules/router";
import { vuetify } from "./modules/vuetify";
import { i18n } from "./modules/i18n";
import { store } from "./modules/vuex";

const app = createApp(App);

app.use(router);
app.use(vuetify);
app.use(i18n);
app.use(store);
app.mount("#app");
