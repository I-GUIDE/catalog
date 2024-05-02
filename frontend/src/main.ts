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
