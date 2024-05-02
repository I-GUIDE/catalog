import { createMemoryHistory, createRouter } from "vue-router";
import { routes } from "@/routes";
import User from "@/models/user.model";

export const router = createRouter({
  history: createMemoryHistory(),
  routes,
  scrollBehavior(_to, _from, _savedPosition) {
    document.getElementsByTagName("html")[0]?.scrollTo({ left: 0, top: 0 });
  },
});

/** Call before navigating to an external url to save the next route in state and navigate to it after callback url */
export function saveNextRoute() {
  const next = router.currentRoute.value.query.next;
  if (next) {
    User.commit((state) => {
      state.next = next;
    });
  }
}
