export const APP_NAME = process.env.VUE_APP_NAME || "";
export const SUPPORT_EMAIL = process.env.VUE_APP_SUPPORT_EMAIL || "";
export const DEFAULT_TOAST_DURATION = 3500;

export const sameRouteNavigationErrorHandler = (e) => {
  // Ignore the vuex err regarding  navigating to the page they are already on.
  if (
    e.name !== "NavigationDuplicated" &&
    !e.message.includes("Avoided redundant navigation to current location")
  ) {
    // But print any other errors to the console
    console.error(e);
  }
};

export const MAX_YEAR = new Date().getFullYear();
export const MIN_YEAR = 1900;
export const API_BASE = process.env.VUE_APP_API_URL || "";
export const ENDPOINTS: { [key: string]: string } = {
  search: `${API_BASE}/discovery/search`,
  typeahead: `${API_BASE}/discovery/typeahead`,
  submit: `${API_BASE}/catalog/dataset`,
  dataset: `${API_BASE}/catalog/dataset`,
  schemaUrl: `${API_BASE}/schemas/schema.json`,
  uiSchemaUrl: `${API_BASE}/schemas/ui-schema.json`,
  schemaDefaultsUrl: `${API_BASE}/schemas/schema-defaults.json`,
  // api: `${API_BASE}`,
  // logout: `${API_BASE}/logout`,
};
export const INITIAL_RANGE: [number, number] = [MIN_YEAR, MAX_YEAR];
