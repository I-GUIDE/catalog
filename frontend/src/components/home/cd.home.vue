<template>
  <div class="cd-home">
    <cd-home-search />
    <cd-featured-datasets></cd-featured-datasets>

    <v-divider />

    <v-container class="text-center py-12">
      <div class="display-1 mt-4">{{ $t("home.contribute.title") }}</div>
      <v-list-subheader
        class="text-body-1 mt-2 mb-4 d-inline-block"
        style="max-width: 35rem"
      >
        {{ $t("home.contribute.subtitle") }}
      </v-list-subheader>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Component, Vue, toNative } from "vue-facing-decorator";
import CdHomeSearch from "@/components/home/cd.home-search.vue";
import CdFeaturedDatasets from "@/components/home/cd.featured-datasets.vue";

@Component({
  name: "cd-home",
  components: { CdHomeSearch, CdFeaturedDatasets },
})
class CdHome extends Vue {}

export default toNative(CdHome);
</script>

<style lang="scss" scoped></style>
