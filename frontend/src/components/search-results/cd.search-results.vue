<template>
  <v-container
    class="cd-search-results text-body-1"
    :class="{ 'is-small': $vuetify.display.smAndDown }"
  >
    <div class="d-sm-block d-md-flex">
      <v-container class="sidebar flex-shrink-0">
        <div class="sidebar--content">
          <div class="text-subtitle-2 mb-6">Filter by:</div>
          <!-- PUBLICATION YEAR -->
          <cd-range-input
            v-model="publicationYear"
            v-model:isActive="filter.publicationYear.isActive"
            @update:is-active="pushSearchRoute"
            @end="onSliderControlChange(filter.publicationYear)"
            :min="filter.publicationYear.min"
            :max="filter.publicationYear.max"
            label="Publication Year"
          />

          <!-- DATA COVERAGE -->
          <cd-range-input
            v-model="dataCoverage"
            v-model:isActive="filter.dataCoverage.isActive"
            @update:is-active="pushSearchRoute"
            @end="onSliderControlChange(filter.dataCoverage)"
            :min="filter.dataCoverage.min"
            :max="filter.dataCoverage.max"
            label="Data Coverage"
          />

          <!-- CREATOR NAME -->
          <v-text-field
            @blur="pushSearchRoute"
            @keyup.enter="pushSearchRoute"
            @click:clear="pushSearchRoute"
            v-model="filter.creatorName"
            label="Author / Creator name"
            class="mb-6"
            hide-details
            clearable
            variant="outlined"
            density="compact"
          />

          <!-- <v-select
          :items="clusters"
          v-model="filter.project.value"
          @update:model-value="onSearch"
          class="mb-6"
          multiple
          small-chips
          deletable-chips
          clearable
          outlined
          :label="$t('searchResults.filters.projectLabel')"
          hide-details
          density="compact"
        /> -->

          <!-- REPOSITORY -->
          <v-select
            :items="filter.repository.options"
            v-model="filter.repository.value"
            @update:model-value="pushSearchRoute"
            class="mb-6"
            clearable
            variant="outlined"
            density="compact"
            label="Repository"
            hide-details
          />

          <!-- <div>
          <div class="text-body-2">Content type</div>
          <v-checkbox
            v-for="(option, index) of filter.contentType.options"
            v-model="filter.contentType.value"
            @update:model-value="onSearch"
            :key="index"
            :label="option"
            :value="option"
            hide-details
            density="compact"
          />
        </div> -->

          <div class="text-center mt-8">
            <v-btn @click="clearFilters" :disabled="!isSomeFilterActive"
              >Clear Filters</v-btn
            >
          </div>
        </div>
      </v-container>

      <div class="results-content-wrapper">
        <v-container class="results-content">
          <cd-search
            v-model="searchQuery"
            @update:model-value="pushSearchRoute"
            @clear="
              searchQuery = '';
              pushSearchRoute();
            "
            :inputAttrs="{ variant: 'outlined' }"
          />
          <div
            class="my-6 d-lg-flex flex-row justify-space-between gap-1 d-table"
          >
            <div
              class="d-table-row d-lg-flex align-center flex-md-row flex-column gap-1"
            >
              <small class="mr-2">Sort results by:</small>
              <v-btn-toggle
                v-if="searchQuery"
                v-model="sort"
                density="compact"
                size="small"
                divided
                variant="outlined"
                mandatory
              >
                <v-btn
                  v-for="option of sortOptions"
                  :key="option.value"
                  density="compact"
                  @click="
                    $nextTick(() => {
                      pushSearchRoute();
                    })
                  "
                  :value="option.value"
                  >{{ option.label }}</v-btn
                >
              </v-btn-toggle>
              <v-btn-toggle
                v-else
                v-model="sortEmpty"
                density="compact"
                divided
                variant="outlined"
                mandatory
              >
                <v-btn
                  v-for="option of sortOptions"
                  :key="option.value"
                  @click="
                    $nextTick(() => {
                      pushSearchRoute();
                    })
                  "
                  density="compact"
                  :value="option.value"
                  >{{ option.label }}</v-btn
                >
              </v-btn-toggle>
            </div>
          </div>
          <div class="results-container mb-12">
            <template v-if="isSearching">
              <!-- TODO: refactor into a component -->
              <v-card
                v-for="index in 4"
                :key="index"
                class="mb-6"
                variant="elevated"
                elevation="1"
              >
                <v-card-text>
                  <div class="d-flex">
                    <div class="flex-grow-1">
                      <v-skeleton-loader type="heading" />
                      <v-skeleton-loader
                        class="mt-2"
                        max-width="180"
                        type="text"
                      />
                      <v-skeleton-loader max-width="100" type="text" />
                    </div>
                    <v-skeleton-loader
                      width="100"
                      max-height="50"
                      type="image"
                    />
                  </div>
                  <v-skeleton-loader class="my-2" type="paragraph" />
                  <div class="d-flex align-center my-2 gap-1">
                    <v-skeleton-loader width="90" type="text" />
                    <v-skeleton-loader width="90" type="text" />
                    <v-skeleton-loader width="90" type="text" />
                  </div>
                  <v-skeleton-loader type="button" />
                </v-card-text>
              </v-card>
            </template>
            <template v-else>
              <div
                v-if="!results.length"
                class="text-body-2 text--secondary text-center mt-8"
              >
                <div class="mb-8">No results found.</div>
                <v-icon x-large>mdi-book-remove-multiple</v-icon>
              </div>

              <v-card
                v-for="(result, index) of results"
                class="mb-6 text-body-2"
                :key="result.identifier"
                variant="elevated"
                elevation="1"
              >
                <v-card-text>
                  <v-btn
                    :to="{ path: `dataset/${result.id}` }"
                    class="text-body-1 text-primary px-0"
                    v-html="highlight(result, 'name')"
                    variant="text"
                  ></v-btn>
                  <div
                    class="d-flex gap-1 justify-space-between flex-wrap flex-lg-nowrap mt-2"
                  >
                    <div>
                      <p
                        ref="description"
                        class="mt-4 mb-1"
                        :class="{
                          'snip-3': !result.showMore,
                        }"
                        v-html="
                          `<span class='text-body-2 font-weight-bold'>${formatDate(
                            result.dateCreated,
                          )}</span>${result.dateCreated ? ' - ' : ''}${highlight(
                            result,
                            'description',
                          )}`
                        "
                      ></p>

                      <v-btn
                        v-if="hasShowMoreButton(index)"
                        size="x-small"
                        variant="text"
                        color="primary"
                        @click="result.showMore = !result.showMore"
                        >Show {{ result.showMore ? "less" : "more" }}...</v-btn
                      >

                      <div class="my-1" v-if="result.datePublished">
                        Publication Date: {{ formatDate(result.datePublished) }}
                      </div>
                      <div
                        class="my-2"
                        v-html="highlightCreators(result)"
                      ></div>

                      <div>
                        <span class="d-flex align-center mb-2"
                          ><a :href="result.url" target="_blank">{{
                            result.url
                          }}</a
                          ><v-icon class="ml-2" small
                            >mdi-open-in-new</v-icon
                          ></span
                        >
                        <div class="mb-2">
                          <strong>Keywords: </strong
                          ><span v-html="highlight(result, 'keywords')"></span>
                        </div>
                        <div class="mb-2" v-if="result.funding.length">
                          <strong>Funded by: </strong
                          >{{ result.funding.join(", ") }}
                        </div>
                        <div class="mb-2" v-if="result.license">
                          <strong>License: </strong>{{ result.license }}
                        </div>
                      </div>
                    </div>
                    <div
                      v-if="hasSpatialFeatures(result)"
                      :id="`map-${result.id}`"
                      :class="{ 'full-width': $vuetify.display.mdAndDown }"
                    >
                      <cd-spatial-coverage-map
                        :loader="loader"
                        :feature="result.spatialCoverage"
                        :key="`map-${result.id}`"
                      />
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </template>
          </div>
          <div
            v-if="results.length"
            v-intersect="{
              handler: onIntersect,
              options: { threshold: [0, 0.5, 1.0] },
            }"
          ></div>
          <div
            v-if="isFetchingMore"
            class="text-subtitle-2 text-secondary text-center"
          >
            Loading more results...
          </div>
          <div
            v-if="results.length && !hasMore"
            class="text-subtitle-2 text-secondary text-center"
          >
            End of results.
          </div>
        </v-container>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, toNative } from "vue-facing-decorator";
import { sameRouteNavigationErrorHandler } from "@/constants";
import { Loader, LoaderOptions } from "google-maps";
import { formatDate } from "@/util";
import { Notifications } from "@cznethub/cznet-vue-core";
import { MIN_YEAR, MAX_YEAR } from "@/constants";
import { ISearchFilter, ISearchParams, IResult } from "@/types";
import CdSpatialCoverageMap from "@/components/search-results/cd.spatial-coverage-map.vue";
import CdSearch from "@/components/search/cd.search.vue";
import SearchResults from "@/models/search-results.model";
import SearchHistory from "@/models/search-history.model";
import Search from "@/models/search.model";
import { clamp } from "@vueuse/core";
import { useRoute, useRouter } from "vue-router";
import CdRangeInput from "./cd.range-input.vue";

const options: LoaderOptions = { libraries: ["drawing"] };
const loader: Loader = new Loader(
  import.meta.env.VITE_APP_GOOGLE_MAPS_API_KEY,
  options,
);

const sortOptions: { label: string; value: string }[] = [
  { label: "Relevance", value: "relevance" },
  { label: "Title", value: "name" },
  { label: "Date Created", value: "dateCreated" },
];

@Component({
  name: "cd-search-results",
  components: { CdSearch, CdSpatialCoverageMap, CdRangeInput },
})
class CdSearchResults extends Vue {
  loader = loader;
  options = options;
  isIntersecting = false;
  searchQuery = "";
  pageNumber = 1;
  pageSize = 15;
  hasMore = true;
  isSearching = false;
  isFetchingMore = false;
  sort: "name" | "dateCreated" | "relevance" = "relevance";
  sortEmpty = "dateCreated";
  formatDate = formatDate;
  descriptionRefs: any[] = [];
  filter: ISearchFilter = {
    publicationYear: {
      min: MIN_YEAR,
      max: MAX_YEAR,
      isActive: false,
    },
    dataCoverage: {
      min: MIN_YEAR,
      max: MAX_YEAR,
      isActive: false,
    },
    // project: {
    //   // Options are loaded via api during app `created` hook.
    //   value: [],
    // },
    // contentType: {
    //   options: ["Dataset", "Notebook/Code", "Software"],
    //   value: [],
    // },
    repository: {
      options: ["HydroShare"],
      value: null,
    },
    creatorName: "",
  };
  route = useRoute();
  router = useRouter();

  get sortOptions(): { label: string; value: string }[] {
    return this.searchQuery
      ? sortOptions
      : sortOptions.slice(1, sortOptions.length);
  }

  public get publicationYear(): [number, number] {
    return SearchResults.$state.publicationYear;
  }

  public set publicationYear(range: [number, number]) {
    SearchResults.commit((state) => {
      state.publicationYear = [
        clamp(
          range[0],
          this.filter.publicationYear.min,
          this.filter.publicationYear.max,
        ),
        clamp(
          range[1],
          this.filter.publicationYear.min,
          this.filter.publicationYear.max,
        ),
      ];
    });
  }

  public get dataCoverage() {
    return SearchResults.$state.dataCoverage;
  }

  public set dataCoverage(range: [number, number]) {
    SearchResults.commit((state) => {
      state.dataCoverage = [
        clamp(
          range[0],
          this.filter.dataCoverage.min,
          this.filter.dataCoverage.max,
        ),
        clamp(
          range[1],
          this.filter.dataCoverage.min,
          this.filter.dataCoverage.max,
        ),
      ];
    });
  }

  get results() {
    return Search.$state.results;
  }

  get clusters() {
    return Search.$state.clusters;
  }

  /** Search query parameters */
  get queryParams(): ISearchParams {
    const queryParams: ISearchParams = {
      term: this.searchQuery,
      pageSize: this.pageSize,
      pageNumber: this.pageNumber,
    };

    // PUBLICATION YEAR
    if (this.filter.publicationYear.isActive) {
      queryParams.publishedStart = this.publicationYear[0];
      queryParams.publishedEnd = this.publicationYear[1];
    }

    // DATA COVERAGE
    if (this.filter.dataCoverage.isActive) {
      queryParams.dataCoverageStart = this.dataCoverage[0];
      queryParams.dataCoverageEnd = this.dataCoverage[1];
    }

    // CREATOR NAME
    if (this.filter.creatorName) {
      queryParams.creatorName = this.filter.creatorName;
    }

    // REPOSITORY
    if (this.filter.repository.value) {
      queryParams.providerName = this.filter.repository.value;
    }

    // PROJECT
    // if (this.filter.project.value.length) {
    //   queryParams.clusters = this.filter.project.value;
    // }

    // CONTENT TYPE
    // if (this.filter.contentType.value?.length) {
    //   queryParams.contentType = this.filter.contentType.value;
    // }

    // SORT BY
    if (this.searchQuery && this.sort) {
      queryParams.sortBy = this.sort;
    } else if (this.sortEmpty) {
      // @ts-ignore
      queryParams.sortBy = this.sortEmpty;
    }

    return queryParams;
  }

  get isSomeFilterActive() {
    return (
      this.filter.publicationYear.isActive ||
      this.filter.publicationYear.isActive ||
      this.filter.dataCoverage.isActive ||
      this.filter.repository.value ||
      // this.filter.project.value ||
      // this.filter.contentType.value.length ||
      this.filter.creatorName
    );
  }

  displayRefs() {
    this.descriptionRefs = (this.$refs["description"] as any[]) || [];
  }

  /** Route query parameters with short keys. These are parameters needed to replicate a search. */
  get routeParams() {
    return {
      q: this.searchQuery,
      cn: this.filter.creatorName || undefined,
      r: this.filter.repository.value || undefined,
      py: this.filter.publicationYear.isActive
        ? this.publicationYear.map((n) => n.toString()) || undefined
        : undefined,
      dc: this.filter.dataCoverage.isActive
        ? this.dataCoverage.map((n) => n.toString()) || undefined
        : undefined,
      // p: this.filter.project.value || undefined,
      // ct: this.filter.contentType.value || undefined,
      s: (this.searchQuery ? this.sort : this.sortEmpty) || undefined,
    };
  }

  hasShowMoreButton(index: number) {
    const lines = this._countLines(this.descriptionRefs[index]);
    return lines >= 3;
  }

  private _countLines(el: HTMLElement) {
    if (el && document.defaultView) {
      const divHeight = el.offsetHeight;
      const lineHeight = +document.defaultView
        .getComputedStyle(el, null)
        .lineHeight.replace("px", "");
      return divHeight / lineHeight;
    }

    return 0;
  }

  created() {
    this._loadRouteParams();
    this._onSearch();
  }

  public onSliderControlChange(filter: {
    min: number;
    max: number;
    isActive: boolean;
  }) {
    console.log("onSliderControlChange");
    filter.isActive = true;
    this.pushSearchRoute();
  }

  goToDataset(id: string) {
    this.router.push({ path: `dataset/${id}` });
  }

  public onIntersect(_isIntersecting: boolean, entries: any[], _observer: any) {
    this.isIntersecting = entries[0]?.intersectionRatio >= 0.5;
    if (
      this.isIntersecting &&
      this.results.length &&
      this.hasMore &&
      !this.isSearching &&
      !this.isFetchingMore
    ) {
      this.fetchMore();
    }
  }

  public clearFilters() {
    const wasSomeActive = this.isSomeFilterActive;

    this.filter.publicationYear.isActive = false;
    this.filter.dataCoverage.isActive = false;
    // this.filter.contentType.value = [];
    // this.filter.project.value = [];
    this.filter.repository.value = null;
    this.filter.creatorName = "";

    if (wasSomeActive) {
      this.pushSearchRoute();
    }
  }

  /** Pushes the desired search to the router, which will reload the route with the new query parameters */
  pushSearchRoute() {
    try {
      if (this.queryParams.term) {
        SearchHistory.log(this.queryParams.term);
      }

      // Note: this will reload the component
      this.router
        .push({
          name: "search",
          query: this.routeParams,
        })
        .catch(sameRouteNavigationErrorHandler);
    } catch (e) {
      console.log(e);
      Search.commit((state) => {
        state.results = [];
      });
      Notifications.toast({
        message: `Failed to perform search`,
        type: "error",
      });
    }
  }

  async _onSearch() {
    this.hasMore = true;
    this.isSearching = true;
    this.pageNumber = 1;

    this.hasMore = await Search.search(this.queryParams);
    this.isSearching = false;

    this.$nextTick(() => {
      this.displayRefs();
    });
  }

  /** Get the next page of results. */
  async fetchMore() {
    this.pageNumber++;
    this.isFetchingMore = true;
    try {
      this.hasMore = await Search.fetchMore(this.queryParams);
    } catch (e) {
      console.log(e);
    }
    this.isFetchingMore = false;
  }

  highlightCreators(result: IResult) {
    if (!result.creator) {
      return "";
    }
    const div = document.createElement("DIV");
    div.innerHTML = result.creator.join(", ");

    let content = div.textContent || div.innerText || "";

    if (result.highlights) {
      let hits = result.highlights
        .filter((highlight) => highlight.path === "creator.name")
        .map((hit) =>
          hit.texts.filter((t) => t.type === "hit").map((t) => t.value),
        )
        .flat();

      hits = [...new Set(hits)];
      hits.map((hit) => {
        content = content.replaceAll(hit, `<mark>${hit}</mark>`);
      });
    }

    return content;
  }

  /** Applies highlights to a string or string[] field and returns the new content as HTML */
  public highlight(result: IResult, path: keyof IResult) {
    const div = document.createElement("DIV");
    const field = result[path];

    div.innerHTML = Array.isArray(field) ? field.join(", ") : field;
    let content = div.textContent || div.innerText || "";

    if (result.highlights) {
      let hits = result.highlights
        .filter((highlight) => highlight.path === path)
        .map((hit) =>
          hit.texts.filter((t) => t.type === "hit").map((t) => t.value),
        )
        .flat();

      hits = [...new Set(hits)];
      hits.map((hit) => {
        content = content.replaceAll(hit, `<mark>${hit}</mark>`);
      });
    }

    return content;
  }

  /** Load route query parameters into component values. */
  private _loadRouteParams() {
    // SEARCH QUERY
    this.searchQuery = this.route.query["q"] as string;

    // CREATOR NAME
    this.filter.creatorName = (this.route.query["cn"] as string) || "";

    // REPOSITORY
    this.filter.repository.value = (this.route.query["r"] as string) || null;

    // CONTENT TYPE
    // this.filter.contentType.value = (this.route.query["ct"] as string[]) || [];

    // PROJECT
    // this.filter.project.value = this.route.query["p"]
    //   ? ([this.route.query["p"]].flat() as string[])
    //   : [];

    // PUBLICATION YEAR
    if (this.route.query["py"]) {
      this.filter.publicationYear.isActive = true;
      this.publicationYear =
        ((this.route.query["py"] as [string, string])?.map((n) => +n) as [
          number,
          number,
        ]) || this.publicationYear;
    }

    // DATA COVERAGE
    if (this.route.query["dc"]) {
      this.filter.dataCoverage.isActive = true;
      this.dataCoverage =
        ((this.route.query["dc"] as [string, string])?.map((n) => +n) as [
          number,
          number,
        ]) || this.dataCoverage;
    }

    // SORT
    if (this.route.query["s"]) {
      if (this.searchQuery) {
        this.sort =
          (this.route.query["s"] as "name" | "dateCreated" | "relevance") ||
          this.sort;
      } else {
        this.sortEmpty =
          (this.route.query["s"] as "name" | "dateCreated" | "relevance") ||
          this.sort;
      }
    }
  }

  hasSpatialFeatures(result: IResult): boolean {
    return result.spatialCoverage?.["@type"];
  }
}
export default toNative(CdSearchResults);
</script>

<style lang="scss" scoped>
.sidebar {
  flex-basis: 20rem;
  flex-shrink: 0;
  // position: relative;
  min-width: 0;

  // TODO: pending compatibility with infinite-scrolling content
  // .sidebar--content {
  //   position: sticky;
  //   top: 6rem;
  // }
}

.cd-search-results.is-small {
  .sidebar {
    width: 100%;
  }
}

.results-content-wrapper {
  flex: 1 1 auto;
}

.results-content {
  min-width: 0; // https://stackoverflow.com/a/66689926/3288102
  max-width: 70rem;
  margin: unset;
}

.results-container {
  * {
    word-break: break-word;
  }

  a {
    text-decoration: none;
    &:hover {
      text-decoration: underline !important;
    }
  }
}

:deep(.v-select--chips .v-select__selections .v-chip--select:first-child) {
  margin-top: 1rem;
}
</style>
