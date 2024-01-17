<template>
  <v-container
    class="white--text cd-home-search d-flex flex-column justify-center align-center full-height pa-12"
    :style="{
      'background-image':
        'linear-gradient(rgb(48 41 21 / 45%), rgba(40, 74, 64, 0.07)), url(' +
        require('@/assets/img/bg2.jpg') +
        ')',
    }"
  >
    <div class="text-h3 my-4 text-center has-text-shadow">
      {{ $t("home.search.title") }}
    </div>
    <div class="text-h5 mt-2 mb-12 has-text-shadow text-center">
      {{ $t("home.search.subtitle") }}
    </div>
    <div class="search-container full-width px-4 text-center mb-4">
      <div class="has-text-shadow font-weight-normal text-h6 mb-2">
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
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import CdSearch from "@/components/search/cd.search.vue";

@Component({
  name: "cd-home-search",
  components: { CdSearch },
})
export default class CdHomeSearch extends Vue {}
</script>

<style lang="scss" scoped>
.cd-home-search {
  background-color: var(--v-navbar-base);
  background-size: cover;
  background-position: center;
}

.search-container {
  max-width: 45rem;
}

::v-deep .v-parallax__content {
  padding: 0;
}
</style>
