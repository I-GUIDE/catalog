import { routes } from "./routes";
import VueRouter from "vue-router";

export const router = new VueRouter({
  mode: "history",
  routes,
  scrollBehavior(to, from, savedPosition) {
    document.getElementsByTagName("html")[0]?.scrollTo({ left: 0, top: 0 });
  },
});
