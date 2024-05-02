import "@mdi/font/css/materialdesignicons.css";
import "@fortawesome/fontawesome-free/css/all.css";

import "vuetify/styles";
import type { ThemeDefinition } from "vuetify";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { fa, aliases as fa_aliases } from "vuetify/iconsets/fa";
import { aliases as md_aliases, mdi } from "vuetify/iconsets/mdi";
import colors from "vuetify/util/colors";

const lightTheme: ThemeDefinition = {
  dark: false,
  colors: {
    primary: colors.teal.base,
    secondary: colors.blueGrey.base,
    accent: colors.blue.base,
    error: colors.red.accent3,
    success: colors.teal.accent4,
    info: colors.blueGrey.base,
    navbar: colors.blueGrey.darken2,
  },
};

const darkTheme: ThemeDefinition = {
  dark: true,
  colors: {
    primary: colors.blueGrey.base,
    secondary: colors.teal.darken1,
    accent: colors.amber.base,
    error: colors.red.accent3,
    success: colors.teal.accent4,
    info: colors.blueGrey.base,
  },
};

export const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: "lightTheme",
    themes: {
      lightTheme,
      darkTheme,
    },
    variations: {
      colors: ["primary", "secondary", "info", "navbar"],
      lighten: 4,
      darken: 4,
    },
  },
  icons: {
    defaultSet: "mdi",
    aliases: {
      ...fa_aliases,
      ...md_aliases,
    },
    sets: {
      mdi,
      fa,
    },
  },
});
