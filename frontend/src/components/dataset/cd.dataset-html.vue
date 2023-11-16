<template>
  <v-container class="cd-contribute">
    <div v-if="!isLoading && wasLoaded" class="d-flex">
      <div v-if="!isSm" class="sidebar pr-4">
        <div class="table-of-contents">
          <div class="text-h6">Table of contents</div>
          <ol class="text-body-2">
            <li
              v-for="(item, index) of tableOfContents"
              :key="index"
              class="my-2 text-body-1"
            >
              <!-- <router-link :to="{ hash: item.link }">{{
                item.title
              }}</router-link> -->

              <a :href="item.link">{{ item.title }}</a>
            </li>
          </ol>
        </div>
      </div>

      <div class="page-content" :class="{ 'is-sm': isSm }">
        <div
          class="d-flex justify-space-between mb-2 flex-column flex-sm-row align-normal align-sm-end"
        >
          <div class="order-2 order-sm-1">
            <template v-if="data.dateModified">
              <span class="d-block d-sm-inline" v-bind="infoLabelAttr"
                >Last Updated:</span
              >
              <span v-bind="infoValueAttr">
                {{ parseDate(data.dateModified) }} (<timeago
                  :datetime="data.dateModified"
                ></timeago
                >)
              </span>
            </template>
          </div>
          <v-btn
            v-if="!data.repository_identifier"
            class="order-1 order-sm-2 mb-sm-0 mb-4"
            @click="
              $router.push({
                name: 'dataset-edit',
                params: { id: data._id },
              })
            "
            rounded
          >
            <v-icon>mdi-text-box-edit</v-icon><span class="ml-1">Edit</span>
          </v-btn>
        </div>

        <v-divider class="my-4"></v-divider>
        <h4 class="text-h4">{{ data.name }}</h4>

        <v-row class="my-4 align-start" no-gutters>
          <v-col cols="12" sm="8" class="dataset-info">
            <div v-bind="infoLabelAttr">Created By:</div>
            <div v-bind="infoValueAttr">{{ createdBy }}</div>

            <div v-bind="infoLabelAttr">Provider:</div>
            <div v-bind="infoValueAttr">
              <span v-if="data.provider.url" class="d-flex align-center">
                <a :href="data.provider.url" target="_blank">{{
                  data.provider.name
                }}</a>
                <v-icon class="ml-2" small>mdi-open-in-new</v-icon>
              </span>

              <template v-else>{{ data.provider.name }}</template>
            </div>

            <div v-bind="infoLabelAttr">Resource Type:</div>
            <div v-bind="infoValueAttr">{{ data["@type"] }}</div>

            <div v-bind="infoLabelAttr">Resource Size:</div>
            <div v-bind="infoValueAttr">~2 MB</div>

            <div v-bind="infoLabelAttr">License:</div>
            <div v-bind="infoValueAttr">
              <div v-if="data.license.url" class="d-flex align-center">
                <a :href="data.license.url" target="_blank">{{
                  data.license.name
                }}</a>
                <v-icon class="ml-2" small>mdi-open-in-new</v-icon>
              </div>

              <template v-else>{{ data.license.name }}</template>

              <div class="font-weight-light">
                {{ data.license.description }}
              </div>
            </div>

            <div v-bind="infoLabelAttr">Language:</div>
            <div v-bind="infoValueAttr">{{ data.inLanguage }}</div>
          </v-col>

          <v-col cols="12" sm="4" class="dataset-info">
            <div v-bind="infoLabelAttr">Host Repository:</div>
            <div v-bind="infoValueAttr">HydroShare</div>

            <div v-bind="infoLabelAttr">Created:</div>
            <div v-bind="infoValueAttr">
              {{ parseDate(data.dateCreated) }}
            </div>
          </v-col>
        </v-row>

        <div class="mb-8 field" id="description">
          <div class="text-overline primary--text darken-4">Description</div>
          <v-divider class="primary my-1"></v-divider>
          <p class="text-body-1">{{ data.description }}</p>
        </div>

        <div class="mb-8 field">
          <div class="text-overline primary--text darken-4">Url</div>
          <v-divider class="primary my-1"></v-divider>

          <span class="d-flex align-center text-body-1">
            <a :href="data.url" target="_blank" class="break-word">{{
              data.url
            }}</a>
            <v-icon class="ml-2" small>mdi-open-in-new</v-icon>
          </span>
        </div>

        <div class="my-4 field" id="subject">
          <div class="text-overline primary--text darken-4">
            Subject Keywords
          </div>
          <v-divider class="primary mb-2"></v-divider>
          <v-chip
            v-for="keyword of data.keywords"
            :key="keyword"
            small
            outlined
            class="mr-1"
            >{{ keyword }}</v-chip
          >
        </div>

        <div
          v-if="hasSpatialFeatures"
          class="my-4 field text-body-1"
          id="coverage"
        >
          <div class="text-overline primary--text darken-4">
            Spatial Coverage
          </div>

          <v-divider class="primary mb-2"></v-divider>
          <v-row>
            <v-col cols="12" sm="8">
              <v-card flat outlined>
                <cd-spatial-coverage-map
                  :loader="loader"
                  :loader-options="options"
                  :feature="data.spatialCoverage.geo"
                  :key="$route.fullPath"
                  :flat="true"
                />
                <v-divider></v-divider>
                <v-card-text>
                  <v-row class="align-start">
                    <v-col cols="12" sm="6" class="dataset-info">
                      <div v-bind="infoLabelAttr">North Latitude:</div>
                      <div v-bind="infoValueAttr">
                        {{ boxCoordinates.north }}°
                      </div>

                      <div v-bind="infoLabelAttr">East Longitude:</div>
                      <div v-bind="infoValueAttr">
                        {{ boxCoordinates.east }}°
                      </div>
                    </v-col>
                    <v-col cols="12" sm="6" class="dataset-info">
                      <div v-bind="infoLabelAttr">South Latitude:</div>
                      <div v-bind="infoValueAttr">
                        {{ boxCoordinates.south }}°
                      </div>

                      <div v-bind="infoLabelAttr">West Longitude:</div>
                      <div v-bind="infoValueAttr">
                        {{ boxCoordinates.west }}°
                      </div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="4" class="dataset-info">
              <div v-bind="infoLabelAttr">
                Coordinate System/Geographic Projection:
              </div>
              <div v-bind="infoValueAttr">WGS 84 EPSG:4326</div>

              <div v-bind="infoLabelAttr">Coordinate Units:</div>
              <div v-bind="infoValueAttr">Decimal degrees</div>

              <div v-bind="infoLabelAttr">Place/Area Name:</div>
              <div v-bind="infoValueAttr">Woodlawn, MD</div>
            </v-col>
          </v-row>
        </div>

        <div class="mb-8 field text-body-1">
          <div class="text-overline primary--text darken-4">
            Temporal Coverage
          </div>
          <v-divider class="primary mb-2"></v-divider>

          <v-stepper flat vertical non-linear>
            <v-stepper-step
              complete
              step="1"
              complete-icon="mdi-calendar-start-outline"
            >
              <span>Nov 24, 2023</span>
              <small class="primary--text font-weight-medium mt-1"
                >Start Date</small
              >
            </v-stepper-step>

            <v-stepper-content step="1"></v-stepper-content>

            <v-stepper-step
              complete
              step="2"
              complete-icon="mdi-calendar-end-outline"
            >
              <span>Dec 1, 2023</span>
              <small class="primary--text font-weight-medium mt-1"
                >End Date</small
              >
            </v-stepper-step>

            <v-stepper-content step="2"></v-stepper-content>
          </v-stepper>
        </div>

        <div class="mb-8 field" id="access">
          <div id="access" class="text-overline primary--text darken-4">
            Access and Usage
          </div>
          <v-divider class="primary my-1"></v-divider>
        </div>

        <div class="mb-8 field" id="related">
          <div class="text-overline primary--text darken-4">
            Related Resources
          </div>
          <v-divider class="primary my-1"></v-divider>
        </div>

        <div class="mb-8 field" id="credits">
          <div class="text-overline primary--text darken-4">Credits</div>
          <v-divider class="primary my-1"></v-divider>
        </div>

        <div class="mb-8 field" id="howtocite">
          <div class="text-overline primary--text darken-4">How to Cite</div>
          <v-divider class="primary my-1"></v-divider>
        </div>

        <div class="my-4 field">
          <div class="text-overline primary--text darken-4">Creators</div>
          <div v-for="(creator, index) of data.creator" :key="index">
            <p class="text-body-1">{{ creator.name }}</p>
          </div>
        </div>

        <div v-if="data.identifier?.length" class="my-4 field">
          <div class="text-overline primary--text darken-4">Identifiers</div>
          <div v-for="(identifier, index) of data.identifier" :key="index">
            <p class="text-body-1">{{ identifier }}</p>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="isLoading" class="text-h6 text--secondary my-12">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <v-alert
      v-else-if="!wasLoaded && !isLoading"
      border="left"
      colored-border
      type="error"
      elevation="2"
      >Failed to load dataset</v-alert
    >
    <!-- <v-card>
      <v-card-text>
        <pre>{{ JSON.stringify(data, null, 2) }}</pre>
      </v-card-text>
    </v-card> -->
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { CzForm } from "@cznethub/cznet-vue-core";
import { Loader, LoaderOptions } from "google-maps";
import CdSpatialCoverageMap from "@/components/search-results/cd.spatial-coverage-map.vue";
import User from "@/models/user.model";

const options: LoaderOptions = { libraries: ["drawing"] };
const loader: Loader = new Loader(
  process.env.VUE_APP_GOOGLE_MAPS_API_KEY,
  options
);

@Component({
  name: "cd-contribute",
  components: { CzForm, CdSpatialCoverageMap },
})
export default class CdDataset extends Vue {
  public loader = loader;
  public options = options;
  protected data: any = {};
  protected isLoading = true;
  protected wasLoaded = false;
  protected submissionId = "";

  protected config = {
    restrict: true,
    trim: false,
    showUnfocusedDescription: false,
    hideRequiredAsterisk: false,
    collapseNewItems: false,
    breakHorizontal: false,
    initCollapsed: false,
    hideAvatar: false,
    hideArraySummaryValidation: false,
    vuetify: {
      commonAttrs: {
        dense: true,
        outlined: true,
        "persistent-hint": true,
        "hide-details": false,
      },
    },
    isViewMode: true,
  };

  protected tableOfContents = [
    { title: "Description", link: "#description" },
    { title: "Subject Keywords", link: "#subject" },
    { title: "Spatial and Temporal Coverage", link: "#coverage" },
    { title: "Access and Usage", link: "#access" },
    { title: "Additional Metadata", link: "#additional" },
    { title: "Related Resources", link: "#related" },
    { title: "Credits", link: "#credits" },
    { title: "How to Cite", link: "#howtocite" },
  ];

  protected infoLabelAttr = {
    class: "text-subtitle-1 font-weight-light",
  };

  protected infoValueAttr = {
    class: "text-body-1 mb-2 mb-sm-0",
  };

  created() {
    this.loadDataset();
  }

  protected get createdBy() {
    return this.data.creator?.map((c) => c.name).join(", ");
  }

  protected get isSm() {
    return this.$vuetify.breakpoint.mdAndDown;
  }

  protected async loadDataset() {
    this.submissionId = this.$route.params.id;
    this.isLoading = true;
    try {
      const data = await User.fetchDataset(this.submissionId);
      if (data) {
        this.data = data;
        console.log(data);
      }
      this.wasLoaded = !!data;
    } catch (e) {
      this.wasLoaded = false;
    } finally {
      this.isLoading = false;
    }
  }

  protected parseDate(date: string): string {
    const parsed = new Date(Date.parse(date));
    return parsed.toLocaleString("default", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  }

  // protected getTransformedSpatialCoverage() {
  //   return { ...data.spatialCoverage, }
  // }

  protected get hasSpatialFeatures(): boolean {
    return !!this.data.spatialCoverage?.["@type"];
  }

  protected get schema() {
    return User.$state.schema;
  }

  protected get uiSchema() {
    return User.$state.uiSchema;
  }

  protected get boxCoordinates() {
    const extents = this.data.spatialCoverage.geo.box
      .trim()
      .split(" ")
      .map((n) => +n);
    return {
      north: extents[0],
      east: extents[1],
      south: extents[2],
      west: extents[3],
    };
  }
}
</script>

<style lang="scss" scoped>
.sidebar {
  flex-basis: 15rem;
  flex-shrink: 0;
  position: relative;

  .table-of-contents {
    position: sticky;
    top: 6rem;
  }
}

.break-word {
  word-break: break-word;
}

.page-content {
  flex-grow: 1;

  &.is-sm {
    .dataset-info {
      grid-template-columns: auto;
      gap: 0;
    }
  }
}

.dataset-info {
  display: grid;
  grid-template-columns: auto auto;
  gap: 0.5rem 1rem;
  justify-content: start;
  align-items: baseline;
  align-content: baseline;
}

::v-deep .map-container {
  width: 100%;
  height: 20rem;
}
</style>
