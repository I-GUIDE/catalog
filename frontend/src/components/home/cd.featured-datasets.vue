<template>
  <v-container class="cd-featured-datasets text-center py-12">
    <div class="display-1 my-4">{{ $t("home.featuredData.title") }}</div>
    <v-subheader
      class="text-body-1 my-4 d-inline-block"
      style="max-width: 35rem"
    >
      {{ $t("home.featuredData.subtitle") }}
    </v-subheader>
    <v-slide-group
      v-model="selected"
      v-if="fetchedDatasets.length || isLoading"
      center-active
      class="pa-4"
      show-arrows
    >
      <v-slide-item
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
              <div class="card-icon info lighten-3">
                <div class="page-icons">
                  <div class="page-icon elevation-1">
                    <v-icon>mdi-text-long</v-icon>
                  </div>
                  <div class="page-icon elevation-1">
                    <v-icon>mdi-text-long</v-icon>
                    <v-icon>mdi-chart-multiple</v-icon>
                    <v-icon>mdi-chart-bar</v-icon>
                    <v-icon>mdi-text-long</v-icon>
                  </div>
                </div>
              </div>
              <div class="card-content info lighten-4">
                <v-card-text class="pb-0 d-flex justify-space-between">
                  <div>
                    <template v-if="result.dateCreated">{{
                      formatDate(result.dateCreated)
                    }}</template>
                  </div>
                  <v-btn
                    class="primary lighten-1"
                    :href="result.url"
                    target="_blank"
                    small
                    depressed
                  >
                    <v-icon small left>mdi-open-in-new</v-icon>
                    View
                  </v-btn>
                </v-card-text>
                <v-card-title :title="result.name" class="text-body-1 d-block">
                  <div class="snip-2">{{ result.name }}</div>
                </v-card-title>
                <v-card-text>
                  <div v-if="result.keywords.length" class="mb-4">
                    <v-chip
                      v-for="(keyowrd, index) of result.keywords.slice(0, 3)"
                      :key="index"
                      class="ma-1"
                      color="secondary lighten-2"
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
      </v-slide-item>
    </v-slide-group>
    <div v-else class="text-body-2">
      No data to feature right now. Check again soon...
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import CdHomeSearch from "@/components/home/cd.home-search.vue";
import Search from "@/models/search.model";
import { formatDate } from "@/util";

const numFeatured = 10;
const featuredSearch = "Water";

@Component({
  name: "cd-featured-datasets",
  components: { CdHomeSearch },
})
export default class CdFeaturedDatasets extends Vue {
  protected selected: number | null = null;
  protected formatDate = formatDate;
  protected isLoading = false;
  // protected datasets = FEATURED_DATASETS;  // JSON file setup. Unused for now.

  protected getResultAuthors(result) {
    return result.creator.join(", ");
  }

  public get datasets(): IResult[] {
    return this.fetchedDatasets.length
      ? this.fetchedDatasets
      : new Array(numFeatured).fill(null);
  }

  protected get fetchedDatasets() {
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

  // public getResultCreationDate(result) {
  //   if (!result.dateCreated) {
  //     return ''
  //   }
  //   return new Date(result.dateCreated).toLocaleDateString("en-us", {
  //     year: "numeric",
  //     month: "long",
  //     day: "numeric",
  //   });
  // }

  // public getResultPublicationDate(result) {
  //   return new Date(result.datePublished).toLocaleDateString("en-us", {
  //     year: "numeric",
  //     month: "long",
  //     day: "numeric",
  //   });
  // }

  // public getResultKeywords(result) {
  //   return result.keywords.join(", ");
  // }

  // public getResultFunding(result) {
  //   if (result.funding) {
  //     return result.funding.map((f) => f.name || f.funder.name).join(", ");
  //   }

  //   return "";
  // }
}
</script>

<style lang="scss" scoped>
.card-wrapper,
.page-icons,
.v-card,
.card-icon {
  overflow: visible;
}

::v-deep .v-card--link:before {
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

::v-deep .v-card:hover {
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
  border-left: 4px solid;
  border-left-color: #afb9c0 !important;
  border-top-right-radius: 1rem;
  border-bottom-right-radius: 1rem;
}

::v-deep .v-slide-group.v-item-group {
  z-index: 2;

  & > .v-slide-group__next {
    box-shadow: -4px 0px 4px -4px rgba(0, 0, 0, 0.25);
  }

  & > .v-slide-group__prev {
    box-shadow: 4px 0px 4px -4px rgba(0, 0, 0, 0.25);
  }
}
</style>
