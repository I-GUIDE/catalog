<template>
  <v-container
    class="cd-search-results text-body-1"
    :class="{ 'is-small': $vuetify.breakpoint.smAndDown }"
  >
    <div class="d-sm-block d-md-flex">
      <v-container class="sidebar flex-shrink-0">
        <div class="text-subtitle-2 mb-6">Filter by:</div>
        <!-- PUBLICATION YEAR -->
        <div class="mb-4">
          <v-checkbox
            v-model="filter.publicationYear.isActive"
            @change="onSearch"
            label="Publication year"
            dense
            hide-details
          />
          <v-range-slider
            v-model="publicationYear"
            @change="onSliderControlChange('publicationYear')"
            :class="{ 'grayed-out': !filter.publicationYear.isActive }"
            :min="filter.publicationYear.min"
            :max="filter.publicationYear.max"
            class="mb-1"
            hide-details
          />
          <div
            class="d-flex gap-1"
            :class="{ 'grayed-out': !filter.publicationYear.isActive }"
          >
            <v-text-field
              @change="onSliderChange('publicationYear', 0, $event)"
              :value="publicationYear[0]"
              type="number"
              small
              dense
              outlined
              hide-details
            />
            <v-text-field
              @change="onSliderChange('publicationYear', 1, $event)"
              :value="publicationYear[1]"
              type="number"
              small
              dense
              outlined
              hide-details
            />
          </div>
        </div>

        <!-- DATA COVERAGE -->
        <div class="mb-6">
          <v-checkbox
            v-model="filter.dataCoverage.isActive"
            @change="onSearch"
            dense
            label="Data temporal coverage"
            hide-details
          />
          <v-range-slider
            v-model="dataCoverage"
            @change="onSliderControlChange('dataCoverage')"
            :class="{ 'grayed-out': !filter.dataCoverage.isActive }"
            :min="filter.dataCoverage.min"
            :max="filter.dataCoverage.max"
            class="mb-1"
            hide-details
          />
          <div
            class="d-flex gap-1"
            :class="{ 'grayed-out': !filter.dataCoverage.isActive }"
          >
            <v-text-field
              @change="onSliderChange('dataCoverage', 0, $event)"
              :value="dataCoverage[0]"
              type="number"
              small
              dense
              outlined
              hide-details
            />
            <v-text-field
              @change="onSliderChange('dataCoverage', 1, $event)"
              :value="dataCoverage[1]"
              type="number"
              small
              dense
              outlined
              hide-details
            />
          </div>
        </div>

        <!-- CREATOR NAME -->
        <v-text-field
          @change="
            filter.creatorName = $event;
            onSearch();
          "
          :value="filter.creatorName"
          label="Author / Creator name"
          class="mb-6"
          hide-details
          clearable
          outlined
          dense
        />

        <!-- <v-select
          :items="clusters"
          v-model="filter.project.value"
          @change="onSearch"
          class="mb-6"
          multiple
          small-chips
          deletable-chips
          clearable
          outlined
          :label="$t('searchResults.filters.projectLabel')"
          hide-details
          dense
        /> -->

        <v-select
          :items="filter.repository.options"
          v-model="filter.repository.value"
          @change="onSearch"
          class="mb-6"
          clearable
          outlined
          label="Repository"
          hide-details
          dense
        />

        <!-- <div>
          <div class="text-body-2">Content type</div>
          <v-checkbox
            v-for="(option, index) of filter.contentType.options"
            v-model="filter.contentType.value"
            @change="onSearch"
            :key="index"
            :label="option"
            :value="option"
            hide-details
            dense
          />
        </div> -->

        <div class="text-center mt-8">
          <v-btn @click="clearFilters" :disabled="!isSomeFilterActive"
            >Clear Filters</v-btn
          >
        </div>
      </v-container>

      <div class="results-content-wrapper">
        <v-container class="results-content">
          <cd-search
            v-model="searchQuery"
            @input="onSearch"
            @clear="
              searchQuery = '';
              onSearch(true);
            "
          />
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
            <div
              class="d-table-row d-lg-flex align-center flex-md-row flex-column gap-1"
            >
              <small>Sort results by:</small>
              <v-btn-toggle v-model="sort" dense :mandatory="!!searchQuery">
                <v-btn small value="relevance">Relevance</v-btn>
                <v-btn small value="name">Title</v-btn>
                <v-btn small value="dateCreated">Date Created</v-btn>
                <!-- <v-btn small value="registrationDate">Date Registered</v-btn> -->
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
                v-for="(result, index) of results"
                class="mb-16 text-body-2"
                :key="result.identifier"
              >
                <a 
                  :href="result.url"
                  target="_blank"
                  class="result-title text-body-1 text-decoration-none"
                  v-html="highlight(result, 'name')"
                ></a>

                <p
                  ref="description"
                  class="mt-4 mb-1"
                  :class="{
                    'snip-3': !result.showMore,
                  }"
                  v-html="
                    `<span class='text--secondary text-body-2'>${formatDate(
                      result.dateCreated
                    )}</span>${result.dateCreated ? ' - ' : ''}${highlight(
                      result,
                      'description'
                    )}`
                  "
                ></p>

                <v-btn
                  v-if="hasShowMoreButton(index)"
                  x-small
                  text
                  color="primary"
                  @click="$set(result, 'showMore', !result.showMore)"
                  >Show {{ result.showMore ? "less" : "more" }}...</v-btn
                >

                <div class="my-1" v-if="result.datePublished">
                  Publication Date: {{ formatDate(result.datePublished) }}
                </div>
                <div class="my-2" v-html="highlightCreators(result)"></div>

                <div
                  class="d-flex gap-1 justify-space-between flex-wrap flex-lg-nowrap mt-2"
                >
                  <div>
                    <span class="d-flex align-center mb-2"
                      ><a :href="result.url" target="_blank">{{ result.url }}</a
                      ><v-icon class="ml-2" small>mdi-open-in-new</v-icon></span
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

                  <div
                    v-if="hasSpatialFeatures(result)"
                    :id="`map-${result.id}`"
                  >
                    <cd-spatial-coverage-map
                      :loader="loader"
                      :loader-options="options"
                      :feature="result.spatialCoverage"
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
import { MIN_YEAR, MAX_YEAR } from "@/constants";

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
  public sort: "name" | "dateCreated" | "relevance" | "registrationDate" =
    "relevance";
  public preferredSort: "name" | "dateCreated" | "relevance" = "relevance";
  // public view: 'list' | 'map' = 'list'
  public formatDate = formatDate;
  protected descriptionRefs: any[] = [];
  public filter: ISearchFilter = {
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
      value: "",
    },
    creatorName: "",
  };

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

    // PUBLICATION YEAR
    if (this.filter.publicationYear.isActive) {
      this.$set(queryParams, "publishedStart", this.publicationYear[0]);
      this.$set(queryParams, "publishedEnd", this.publicationYear[1]);
    }

    // DATA COVERAGE
    if (this.filter.dataCoverage.isActive) {
      this.$set(queryParams, "dataCoverageStart", this.dataCoverage[0]);
      this.$set(queryParams, "dataCoverageEnd", this.dataCoverage[1]);
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
    if (this.sort) {
      // @ts-ignore
      queryParams.sortBy = this.sort;
    }

    return queryParams;
  }

  public get isSomeFilterActive() {
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

  protected displayRefs() {
    this.descriptionRefs = (this.$refs["description"] as any[]) || [];
  }

  /** Route query parameters with short keys. These are parameters needed to replicate a search. */
  public get routeParams() {
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
      s: this.sort || undefined,
    };
  }

  protected hasShowMoreButton(index) {
    const lines = this._countLines(this.descriptionRefs[index]);
    return lines >= 3;
  }

  private _countLines(el) {
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

    this.sort = this.$route.query["q"]
      ? this.preferredSort
      : "registrationDate";

    this.onSearch();
  }

  /** @param path: the filter object to act on.
   *  @param index: 0 or 1 (min or max).
   *  @param value: the value to set.
   */
  public onSliderChange(path: string, index: 0 | 1, value: number) {
    // Conditional to prevent change event triggers on focus change where the value has not changed.
    if (this[path][index] !== value) {
      this.$set(this.filter[path], "isActive", true);
      this.$set(this[path], index, value);
      this.onSearch();
    }
  }

  public onSliderControlChange(path: any) {
    this.$set(this.filter[path], "isActive", true);
    this.onSearch();
  }

  protected goToDataset(id: string) {
    this.$router.push({ path: `dataset/${id}` });
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

  public clearFilters() {
    const wasSomeActive = this.isSomeFilterActive;

    this.filter.publicationYear.isActive = false;
    this.filter.dataCoverage.isActive = false;
    // this.filter.contentType.value = [];
    // this.filter.project.value = [];
    this.filter.repository.value = "";
    this.filter.creatorName = "";

    if (wasSomeActive) {
      this.onSearch();
    }
  }

  @Watch("sort")
  public onSortChange(newSort, _oldSort) {
    if (newSort !== "registrationDate") {
      this.preferredSort = newSort;
    }
    this.onSearch();
  }

  // protected async onSearchAll() {
  //   this.hasMore = true;
  //   this.isSearching = true;
  //   this.pageNumber = 1;

  //   try {
  //     this.hasMore = await Search.search({
  //       ...this.queryParams,
  //     });
  //   } catch (e) {
  //     console.log(e);
  //     Search.commit((state) => {
  //       state.results = [];
  //     });
  //     Notifications.toast({
  //       message: `Failed to perform search`,
  //       type: "error",
  //     });
  //   }
  //   this.isSearching = false;
  //   this.$nextTick(() => {
  //     this.displayRefs();
  //   });
  // }

  public async onSearch(useAllResultsSort?: boolean) {
    if (!this.searchQuery && useAllResultsSort) {
      this.sort = "registrationDate";
    } else if (this.searchQuery && this.sort === "registrationDate") {
      this.sort = this.preferredSort; // TODO: use previous sort
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

      if (this.queryParams.term) {
        SearchHistory.log(this.queryParams.term);
      }
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
    this.$nextTick(() => {
      this.displayRefs();
    });
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

    // CREATOR NAME
    this.filter.creatorName = (this.$route.query["cn"] as string) || "";

    // REPOSITORY
    this.filter.repository.value = (this.$route.query["r"] as string) || "";

    // CONTENT TYPE
    // this.filter.contentType.value = (this.$route.query["ct"] as string[]) || [];

    // PROJECT
    // this.filter.project.value = this.$route.query["p"]
    //   ? ([this.$route.query["p"]].flat() as string[])
    //   : [];

    // PUBLICATION YEAR
    if (this.$route.query["py"]) {
      this.filter.publicationYear.isActive = true;
      this.publicationYear =
        ((this.$route.query["py"] as [string, string])?.map((n) => +n) as [
          number,
          number
        ]) || this.publicationYear;
    }

    // DATA COVERAGE
    if (this.$route.query["dc"]) {
      this.filter.dataCoverage.isActive = true;
      this.dataCoverage =
        ((this.$route.query["dc"] as [string, string])?.map((n) => +n) as [
          number,
          number
        ]) || this.dataCoverage;
    }

    // SORT
    if (this.$route.query["s"]) {
      this.sort =
        (this.$route.query["s"] as
          | "name"
          | "dateCreated"
          | "relevance"
          | "registrationDate") || this.sort;
    }
  }

  public hasSpatialFeatures(result: IResult): boolean {
    return result.spatialCoverage?.["@type"];
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
