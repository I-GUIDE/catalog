<template>
  <v-parallax
    dark
    class="cd-home-search"
    alt="Landscape with a river and trees during fall"
    :src="'/img/bg2.jpg'"
    :height="$vuetify.display.smAndDown ? 600 : 500"
  >
    <v-container
      class="d-flex flex-column justify-center align-center full-height pa-12 text-white"
      :style="{
        'background-image':
          'linear-gradient(rgb(48 41 21 / 45%), rgba(40, 74, 64, 0.07))',
        'backdrop-filter': 'blur(1px)',
      }"
    >
      <div class="text-h3 my-4 text-center has-text-shadow">
        {{ $t("home.search.title") }}
      </div>
      <div class="text-h5 mt-2 mb-12 has-text-shadow text-center">
        {{ $t("home.search.subtitle") }}
      </div>
      <div class="search-container full-width px-4 text-center mb-4">
        <div class="has-text-shadow font-weight-light text-h6 mb-2">
          {{ $t("home.search.inputLabel") }}
        </div>
        <cd-search />
        <div class="has-text-shadow text-h5 mt-12 mb-2">
          Not sure what you are looking for?
        </div>
        <v-btn @click="$router.push({ name: 'search' })" color="white"
          >Browse IGUIDE catalog</v-btn
        >
      </div>
    </v-container>
  </v-parallax>
</template>

<script lang="ts">
import { Component, Vue, toNative } from "vue-facing-decorator";
import CdSearch from "@/components/search/cd.search.vue";

@Component({
  name: "cd-home-search",
  components: { CdSearch },
})
class CdHomeSearch extends Vue {}
export default toNative(CdHomeSearch);
</script>

<style lang="scss" scoped>
.cd-home-search {
  background-color: var(--v-navbar-base);
}

.search-container {
  max-width: 45rem;
}

:deep(.v-parallax__content) {
  padding: 0;
}
</style>
