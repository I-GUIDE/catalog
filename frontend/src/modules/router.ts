import { APP_NAME } from "@/constants";
import type { UserModule } from "@/types";
import { NavigationHookAfter } from "vue-router";

const addRouteTags: NavigationHookAfter = (to, from) => {
  // This goes through the matched routes from last to first, finding the closest route with a title.
  // e.g., if we have `/some/deep/nested/route` and `/some`, `/deep`, and `/nested` have titles,
  // `/nested`'s will be chosen.
  const nearestWithTitle = to.matched
    .slice()
    .reverse()
    .find((r) => r.meta && r.meta.title);

  // Find the nearest route element with meta tags.
  const nearestWithMeta = to.matched
    .slice()
    .reverse()
    .find((r) => r.meta && r.meta.metaTags);

  const previousNearestWithMeta = from?.matched
    .slice()
    .reverse()
    .find((r) => r.meta && r.meta.metaTags);

  // const { t } = useI18n();

  // If a route with a title was found, set the document (page) title to that value.
  if (nearestWithTitle)
    document.title = `${APP_NAME} | ${nearestWithTitle.meta.title}`;
  else if (previousNearestWithMeta)
    document.title = previousNearestWithMeta.meta.title as string;
  else document.title = `${APP_NAME}`;

  // Remove any stale meta tags from the document using the key attribute we set below.
  Array.from(document.querySelectorAll("[data-vue-router-controlled]")).map(
    (el) => el.parentNode?.removeChild(el),
  );

  // Skip rendering meta tags if there are none.
  if (!nearestWithMeta) return false;

  // Turn the meta tag definitions into actual elements in the head.
  (nearestWithMeta.meta.metaTags as { name: string; content: string }[])
    .map((tagDef: any) => {
      const tag = document.createElement("meta");

      Object.keys(tagDef).forEach((key) => {
        tag.setAttribute(key, tagDef[key]);
      });

      // We use this to track which meta tags we create so we don't interfere with other ones.
      tag.setAttribute("data-vue-router-controlled", "");

      return tag;
    })
    // Add the meta tags to the document head.
    .forEach((tag) => document.head.appendChild(tag));
};

export const install: UserModule = ({ app, router, isClient }) => {
  router.afterEach(addRouteTags);
};
