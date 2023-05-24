<template>
  <v-container
    class="cd-search-results text-body-1"
    :class="{ 'is-small': $vuetify.breakpoint.smAndDown }"
  >
    <div class="d-sm-block d-md-flex">
      <div class="results-content-wrapper">
        <v-container class="results-content">
          <cd-search v-model="searchQuery" @input="onSearch" />
          <div
            class="my-6 d-lg-flex flex-row justify-space-between gap-1 d-table"
          >
            <!-- <div class="d-table-row d-lg-flex align-center flex-row">
              <small class="d-table-cell text-right text-lg-left pr-2 py-2" style="white-space: nowrap">View mode:</small>
              <v-btn-toggle class="d-table-cell" v-model="view" dense mandatory>
                <v-btn small><v-icon small>mdi-view-list-outline</v-icon></v-btn>
                <v-btn small><v-icon small>mdi-map</v-icon></v-btn>
              </v-btn-toggle>
            </div> -->
            <div class="d-table-row d-lg-flex align-center flex-row">
              <small
                class="d-table-cell text-right text-lg-left pr-2"
                style="white-space: nowrap"
                >Sort results by:</small
              >
              <v-btn-toggle class="d-table-cell" v-model="sort" dense mandatory>
                <v-btn small value="relevance">Relevance</v-btn>
                <v-btn small value="dateCreated">Date</v-btn>
                <v-btn small value="name">Title</v-btn>
              </v-btn-toggle>
            </div>
          </div>
          <div class="results-container mb-12">
            <template v-if="isSearching">
              <!-- TODO: refactor into a component -->
              <div v-for="index in 4" :key="index" class="mb-16">
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
                  <v-skeleton-loader width="100" max-height="50" type="image" />
                </div>
                <v-skeleton-loader class="my-2" type="paragraph" />
                <div class="d-flex align-center my-2 gap-1">
                  <v-skeleton-loader width="90" type="text" />
                  <v-skeleton-loader width="90" type="text" />
                  <v-skeleton-loader width="90" type="text" />
                </div>
                <v-skeleton-loader type="button" />
              </div>
            </template>
            <template v-else>
              <div
                v-if="!results.length"
                class="text-body-2 text--secondary text-center mt-8"
              >
                <div class="mb-8">No results found.</div>
                <v-icon x-large>mdi-book-remove-multiple</v-icon>
              </div>
              <div
                v-for="result of results"
                class="mb-16 text-body-2"
                :key="result.id"
              >
                <a
                  class="result-title text-body-1 text-decoration-none"
                  :href="result.url"
                  target="_blank"
                  v-html="highlight(result, 'name')"
                ></a>
                <div class="my-1" v-html="highlightCreators(result)"></div>
                <div class="my-1" v-if="result.dateCreated">
                  {{ formatDate(result.dateCreated) }}
                </div>
                <div class="my-1" v-if="result.datePublished">
                  Publication Date: {{ formatDate(result.datePublished) }}
                </div>
                <p
                  class="mt-4 mb-1"
                  :class="{ 'snip-3': !result.showMore }"
                  v-html="highlight(result, 'description')"
                ></p>

                <v-btn
                  x-small
                  text
                  color="primary"
                  @click="$set(result, 'showMore', !result.showMore)"
                  >Show {{ result.showMore ? "less" : "more" }}...</v-btn
                >

                <div
                  class="d-flex gap-1 justify-space-between flex-wrap flex-lg-nowrap mt-2"
                >
                  <div>
                    <a class="mb-2 d-block" :href="result.url">{{
                      result.url
                    }}</a>
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

                  <div
                    v-if="hasSpatialFeatures(result)"
                    :id="`map-${result.id}`"
                  >
                    <cd-spatial-coverage-map
                      :loader="loader"
                      :loader-options="options"
                      :features="result.spatialCoverage"
                    />
                  </div>
                </div>
              </div>
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
            class="text-subtitle-2 text--secondary text-center"
          >
            Loading more results...
          </div>
          <div
            v-if="results.length && !hasMore"
            class="text-subtitle-2 text--secondary text-center"
          >
            End of results.
          </div>
        </v-container>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { sameRouteNavigationErrorHandler } from "@/constants";
import { Loader, LoaderOptions } from "google-maps";
import { formatDate } from "@/util";
import CdSpatialCoverageMap from "@/components/search-results/cd.spatial-coverage-map.vue";
import CdSearch from "@/components/search/cd.search.vue";
import SearchResults from "@/models/search-results.model";
import SearchHistory from "@/models/search-history.model";
import Search from "@/models/search.model";
import { Notifications } from "@cznethub/cznet-vue-core";

const options: LoaderOptions = { libraries: ["drawing"] };
const loader: Loader = new Loader(
  process.env.VUE_APP_GOOGLE_MAPS_API_KEY,
  options
);

@Component({
  name: "cd-search-results",
  components: { CdSearch, CdSpatialCoverageMap },
})
export default class CdSearchResults extends Vue {
  public loader = loader;
  public options = options;
  public isIntersecting = false;
  public searchQuery = "";
  public pageNumber = 1;
  public pageSize = 15;
  public hasMore = true;
  public isSearching = false;
  public isFetchingMore = false;
  public sort: "name" | "dateCreated" | "relevance" = "relevance";
  // public view: 'list' | 'map' = 'list'
  public formatDate = formatDate;

  public get publicationYear() {
    return SearchResults.$state.publicationYear;
  }

  public set publicationYear(range: [number, number]) {
    // TODO: validate input
    SearchResults.commit((state) => {
      state.publicationYear = range;
    });
  }

  public get dataCoverage() {
    return SearchResults.$state.dataCoverage;
  }

  public set dataCoverage(range: [number, number]) {
    // TODO: validate input
    SearchResults.commit((state) => {
      state.dataCoverage = range;
    });
  }

  public get results() {
    return Search.$state.results;
  }

  public get clusters() {
    return Search.$state.clusters;
  }

  /** Search query parameters */
  public get queryParams(): ISearchParams {
    const queryParams: ISearchParams = {
      term: this.searchQuery,
      pageSize: this.pageSize,
      pageNumber: this.pageNumber,
    };

    // SORT BY
    if (this.sort) {
      queryParams.sortBy = this.sort;
    }

    return queryParams;
  }

  /** Route query parameters with short keys. These are parameters needed to replicate a search. */
  public get routeParams() {
    return {
      q: this.searchQuery,
      s: this.sort || undefined,
    };
  }

  created() {
    this._loadRouteParams();
    if (this.$route.query["q"]) {
      this.onSearch();
    }
  }

  public onIntersect(entries, observer) {
    this.isIntersecting = entries[0].intersectionRatio >= 0.5;
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

  @Watch("sort")
  public onSortChange() {
    this.onSearch();
  }

  public async onSearch() {
    if (!this.searchQuery) {
      return;
    }
    this.hasMore = true;
    this.isSearching = true;
    this.pageNumber = 1;

    try {
      // set the parameters on the route
      this.$router
        .push({
          name: "search",
          query: this.routeParams,
        })
        .catch(sameRouteNavigationErrorHandler);

      SearchHistory.log(this.queryParams.term);
      this.hasMore = await Search.search(this.queryParams);
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
    this.isSearching = false;
  }

  /** Get the next page of results. */
  public async fetchMore() {
    this.pageNumber++;
    this.isFetchingMore = true;
    try {
      this.hasMore = await Search.fetchMore(this.queryParams);
    } catch (e) {
      console.log(e);
    }
    this.isFetchingMore = false;
  }

  public highlightCreators(result: IResult) {
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
          hit.texts.filter((t) => t.type === "hit").map((t) => t.value)
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
  public highlight(result: IResult, path: string) {
    const div = document.createElement("DIV");
    div.innerHTML = Array.isArray(result[path])
      ? result[path].join(", ")
      : result[path];
    let content = div.textContent || div.innerText || "";

    if (result.highlights) {
      let hits = result.highlights
        .filter((highlight) => highlight.path === path)
        .map((hit) =>
          hit.texts.filter((t) => t.type === "hit").map((t) => t.value)
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
    this.searchQuery = this.$route.query["q"] as string;

    // SORT
    if (this.$route.query["s"]) {
      this.sort =
        (this.$route.query["s"] as "name" | "dateCreated" | "relevance") ||
        this.sort;
    }
  }

  public hasSpatialFeatures(result: IResult): boolean {
    return result.spatialCoverage?.some((feature) => feature.geometry);
  }
}
</script>

<style lang="scss" scoped>
.sidebar {
  width: 20rem;
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

.grayed-out {
  opacity: 0.55;
}

::v-deep .v-select--chips .v-select__selections .v-chip--select:first-child {
  margin-top: 1rem;
}
</style>
