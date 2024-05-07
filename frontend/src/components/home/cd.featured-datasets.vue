<template>
  <v-container class="cd-featured-datasets text-center py-12">
    <div class="display-1 my-4">{{ $t("home.featuredData.title") }}</div>
    <div
      class="text-body-1 my-4 d-inline-block font-weight-light"
      style="max-width: 35rem"
    >
      {{ $t("home.featuredData.subtitle") }}
    </div>
    <v-slide-group
      v-model="selected"
      v-if="fetchedDatasets.length || isLoading"
      center-active
      class="pa-4"
      show-arrows
    >
      <v-slide-group-item
        v-for="(result, index) in datasets"
        :key="index"
        v-slot="{ toggle }"
      >
        <v-card
          class="my-4 mx-7 text-left"
          outlined
          width="400"
          height="auto"
          @click="toggle"
          :ripple="false"
          elevation="1"
        >
          <template v-if="!isLoading && result">
            <div class="d-flex full-height card-wrapper">
              <div class="card-icon bg-blue-grey-lighten-3">
                <div class="page-icons">
                  <div class="page-icon elevation-1">
                    <v-icon size="x-small">mdi-text-long</v-icon>
                  </div>
                  <div class="page-icon elevation-1">
                    <v-icon size="x-small">mdi-text-long</v-icon>
                    <v-icon size="x-small">mdi-chart-multiple</v-icon>
                    <v-icon size="x-small">mdi-chart-bar</v-icon>
                    <v-icon size="x-small">mdi-text-long</v-icon>
                  </div>
                </div>
              </div>
              <div class="card-content bg-blue-grey-lighten-4">
                <v-card-text class="pb-0 d-flex justify-space-between">
                  <div>
                    <template v-if="result.dateCreated">{{
                      formatDate(result.dateCreated)
                    }}</template>
                  </div>
                  <v-btn
                    color="primary-lighten-1"
                    @click="
                      router.push({
                        name: 'dataset',
                        params: { id: result.id },
                      })
                    "
                    target="_blank"
                    size="small"
                    depressed
                    variant="flat"
                  >
                    <v-icon small left>mdi-open-in-new</v-icon>
                    View
                  </v-btn>
                </v-card-text>
                <v-card-title
                  :title="result.name"
                  class="text-body-1 d-block font-weight-regular"
                >
                  <div class="snip-2">{{ result.name }}</div>
                </v-card-title>
                <v-card-text>
                  <div v-if="result.keywords.length" class="mb-4">
                    <v-chip
                      v-for="(keyowrd, index) of result.keywords.slice(0, 3)"
                      :key="index"
                      class="ma-1 bg-secondary-lighten-1"
                      style="pointer-events: none"
                      small
                      >{{ keyowrd }}</v-chip
                    >
                  </div>
                  <div class="text-truncate" :title="getResultAuthors(result)">
                    {{ getResultAuthors(result) }}
                  </div>
                </v-card-text>
              </div>
            </div>
          </template>
          <v-skeleton-loader v-else type="image"></v-skeleton-loader>
        </v-card>
      </v-slide-group-item>
    </v-slide-group>
    <div v-else class="text-body-2">
      No data to feature right now. Check again soon...
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, toNative } from "vue-facing-decorator";
import CdHomeSearch from "@/components/home/cd.home-search.vue";
import Search from "@/models/search.model";
import { formatDate } from "@/util";
import { IResult } from "@/types";
import { useRouter } from "vue-router";

const numFeatured = 10;
const featuredSearch = "Water";

@Component({
  name: "cd-featured-datasets",
  components: { CdHomeSearch },
})
class CdFeaturedDatasets extends Vue {
  selected: number | null = null;
  formatDate = formatDate;
  isLoading = false;
  router = useRouter();
  // datasets = FEATURED_DATASETS;  // JSON file setup. Unused for now.

  getResultAuthors(result: IResult) {
    return result.creator.join(", ");
  }

  get datasets(): IResult[] {
    return this.fetchedDatasets.length
      ? this.fetchedDatasets
      : new Array(numFeatured).fill(null);
  }

  get fetchedDatasets() {
    return Search.$state.results;
  }

  created() {
    this.getFeaturedDatasets();
  }

  public async getFeaturedDatasets() {
    try {
      this.isLoading = true;
      await Search.search({
        term: featuredSearch,
        pageSize: numFeatured,
        pageNumber: 1,
      });
      this.isLoading = false;
    } catch (e) {
      console.log(e);
      this.isLoading = false;
    }
  }
}
export default toNative(CdFeaturedDatasets);
</script>

<style lang="scss" scoped>
.card-wrapper,
.page-icons,
.v-card,
.card-icon {
  overflow: visible;
}

:deep(.v-card--link:before) {
  background: transparent !important;
}

.v-card {
  transition: transform 0.15s ease-in-out;
  border-radius: 1rem;
  border: 0;

  &::before {
    border-radius: 1rem;
  }
}

.card-icon {
  width: 1rem;
  display: block;
  flex-shrink: 0;
  position: relative;
  border-top-left-radius: 1rem;
  border-bottom-left-radius: 1rem;

  --dx: 50%;
  --m: 0.5;
  --h: calc(var(--m) * 11rem);
  --w: calc(var(--m) * 8.5rem);
  --dy: calc(50% - var(--h) / 2);

  .page-icons {
    position: absolute;
    right: -1.8rem;
    top: var(--dy);
    transition: all 0.15s ease-in-out;

    .page-icon {
      width: var(--w);
      height: var(--h);
      background: #fff;
      transition: all 0.25s ease-in-out;
      border: 1px solid #efefef;
      padding: 10%;
      .v-icon {
        opacity: 0.25;
      }
    }

    .page-icon:nth-child(1) {
      transform: rotate(-1deg);
    }

    .page-icon:nth-child(2) {
      transform: rotate(1deg);
      translate: 1rem calc(var(--h) * -1.2);
    }
  }
}

:deep(.v-card:hover) {
  transform: scale(1.05);
  z-index: 1;

  .page-icons {
    transform: rotate(-15deg);
  }

  .page-icon:nth-child(1) {
    transform-origin: bottom center;
    transform: rotate(-18deg);
  }
}

.card-content {
  flex: 1 1 auto;
  width: 0;
  box-shadow: -4px 0px 15px -4px rgb(0 0 0 / 25%);
  z-index: 1;
  border-top-right-radius: 1rem;
  border-bottom-right-radius: 1rem;
}

:deep(.v-slide-group.v-item-group) {
  z-index: 2;

  & > .v-slide-group__next {
    box-shadow: -4px 0px 4px -4px rgba(0, 0, 0, 0.25);
  }

  & > .v-slide-group__prev {
    box-shadow: 4px 0px 4px -4px rgba(0, 0, 0, 0.25);
  }
}
</style>
