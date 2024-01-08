<template>
  <v-container class="cd-contribute">
    <div v-if="!isLoading && wasLoaded" class="d-flex">
      <div v-if="!isMd" class="sidebar pr-4 break-word">
        <div class="table-of-contents">
          <div class="text-h6">Table of contents</div>
          <ol class="text-body-2">
            <template v-for="(item, index) of tableOfContents">
              <li
                v-if="!(item.isShown === false)"
                :key="index"
                class="my-2 text-body-1"
              >
                <!-- <router-link :to="{ hash: item.link }">{{
                  item.title
                }}</router-link> -->

                <a :href="item.link">{{ item.title }}</a>
              </li>
            </template>
          </ol>

          <v-card
            v-if="data.citation && data.citation.length"
            class="mt-8"
            flat
          >
            <v-card-title class="pa-0 pb-2">How to cite</v-card-title>
            <v-card-text
              v-for="(citation, index) of data.citation"
              :key="index"
              class="pa-0"
            >
              <div class="d-flex align-center justify-space-between gap-1">
                <div>
                  {{ citation }}
                </div>

                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      icon
                      v-bind="attrs"
                      v-on="on"
                      @click="onCopy(citation)"
                    >
                      <v-icon dark> mdi-content-copy </v-icon>
                    </v-btn>
                  </template>
                  <span>Copy</span>
                </v-tooltip>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </div>

      <div id="overview" class="page-content" :class="{ 'is-sm': isMd }">
        <h4 class="text-h4">{{ data.name }}</h4>
        <div
          class="d-flex justify-space-between mb-2 flex-column flex-sm-row align-normal align-sm-end"
        >
          <div class="order-2 order-sm-1">
            <template v-if="data.dateModified">
              <span class="d-block d-sm-inline" v-bind="infoLabelAttr"
                >Last Updated:</span
              >
              <span v-bind="infoValueAttr">
                {{ parseDate(data.dateModified) }}
                <span class="font-weight-light"
                  >(<timeago :datetime="data.dateModified"> </timeago>)</span
                >
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

        <v-row class="my-4 align-start" :no-gutters="isMd">
          <v-col cols="12" sm="6" class="dataset-info">
            <div v-bind="infoLabelAttr">Created By:</div>
            <div v-bind="infoValueAttr">{{ createdBy }}</div>

            <div v-bind="infoLabelAttr">Provider:</div>
            <div v-bind="infoValueAttr">
              <span v-if="data.provider.url" class="d-flex align-baseline">
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
              <div v-if="data.license.url" class="d-flex align-baseline">
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

          <v-col cols="12" sm="6" class="dataset-info">
            <div v-bind="infoLabelAttr">URL:</div>
            <div
              v-bind="infoValueAttr"
              class="d-flex align-baseline text-body-1"
            >
              <a :href="data.url" target="_blank" class="break-word">{{
                data.url
              }}</a>
              <v-icon class="ml-2" small>mdi-open-in-new</v-icon>
            </div>

            <div v-bind="infoLabelAttr">Created:</div>
            <div v-bind="infoValueAttr">
              {{ parseDate(data.dateCreated) }}
            </div>

            <div v-bind="infoLabelAttr">Host Repository:</div>
            <div v-bind="infoValueAttr">HydroShare</div>
          </v-col>
        </v-row>

        <div class="mb-8 field" id="description">
          <div class="text-overline primary--text darken-4">Description</div>
          <v-divider class="primary my-1"></v-divider>
          <p class="text-body-1">{{ data.description }}</p>
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
          v-if="data.associatedMedia && data.associatedMedia.length"
          class="mb-8 field"
          id="content"
        >
          <div class="text-overline primary--text darken-4">Content</div>
          <v-divider class="primary my-1"></v-divider>

          <cz-file-explorer :rootDirectory="rootDirectory" :canUpload="false" />
        </div>

        <div
          v-if="data.funding && data.funding.length"
          class="mb-8 field"
          id="funding"
        >
          <div class="text-overline primary--text darken-4">Funding</div>
          <v-divider class="primary my-1"></v-divider>
          <v-card
            v-for="(funding, index) of data.funding"
            :key="index"
            class="mt-2"
            flat
            outlined
          >
            <v-card-title class="d-flex align-center">
              <v-icon large left class="mr-2"> mdi-domain </v-icon>
              <div>
                <div class="font-weight-light">{{ funding.funder.name }}</div>
                <a
                  class="text-subtitle-1 font-weight-light"
                  :href="funding.funder.url"
                  target="_blank"
                  >{{ funding.funder.url }}
                </a>
              </div>
            </v-card-title>

            <v-card-text class="font-weight-bold">
              {{ funding.name }}
            </v-card-text>
          </v-card>
        </div>

        <div
          v-if="data.hasPart && data.hasPart.length"
          class="mb-8 field"
          id="related"
        >
          <div class="text-overline primary--text darken-4">
            Related Resources
          </div>
          <v-divider class="primary my-1"></v-divider>
          <div>
            <v-simple-table>
              <template v-slot:default>
                <tbody>
                  <tr
                    v-for="(part, index) in data.hasPart"
                    :key="`hp-${index}`"
                  >
                    <td>Has Part</td>
                    <td>
                      <a :href="part.url" target="_blank">{{ part.name }}</a>
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </div>
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
                <v-card-text
                  v-if="data.spatialCoverage.geo['@type'] == 'GeoShape'"
                >
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

                <v-card-text
                  v-if="data.spatialCoverage.geo['@type'] == 'GeoCoordinates'"
                >
                  <v-row class="align-start">
                    <v-col cols="12" sm="6" class="dataset-info">
                      <div v-bind="infoLabelAttr">Latitude:</div>
                      <div v-bind="infoValueAttr">
                        {{ data.spatialCoverage.geo.latitude }}°
                      </div>
                    </v-col>

                    <v-col cols="12" sm="6" class="dataset-info">
                      <div v-bind="infoLabelAttr">Longitude:</div>
                      <div v-bind="infoValueAttr">
                        {{ data.spatialCoverage.geo.longitude }}°
                      </div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="4" class="dataset-info one-col">
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

        <div v-if="data.temporalCoverage" class="mb-8 field text-body-1">
          <div class="text-overline primary--text darken-4">
            Temporal Coverage
          </div>
          <v-divider class="primary mb-2"></v-divider>

          <v-stepper flat vertical non-linear class="pb-0">
            <v-stepper-step
              v-if="data.temporalCoverage.startDate"
              complete
              step="1"
              complete-icon="mdi-calendar-start-outline"
            >
              <span>{{ parseDate(data.temporalCoverage.startDate) }}</span>
              <small class="primary--text font-weight-medium mt-1"
                >Start Date</small
              >
            </v-stepper-step>

            <v-stepper-content step="1" class="pb-0"></v-stepper-content>

            <v-stepper-step
              v-if="data.temporalCoverage.endDate"
              complete
              step="2"
              complete-icon="mdi-calendar-end-outline"
            >
              <span>{{ parseDate(data.temporalCoverage.endDate) }}</span>
              <small class="primary--text font-weight-medium mt-1"
                >End Date</small
              >
            </v-stepper-step>

            <v-stepper-content step="2" class="pb-0"></v-stepper-content>
          </v-stepper>
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
import {
  CzForm,
  Notifications,
  CzFileExplorer,
} from "@cznethub/cznet-vue-core";
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
  components: { CzForm, CdSpatialCoverageMap, CzFileExplorer },
})
export default class CdDataset extends Vue {
  public loader = loader;
  public options = options;
  protected data: any = {};
  protected isLoading = true;
  protected wasLoaded = false;
  protected submissionId = "";
  protected tab = 0;

  /** Example folder/file tree structure */
  protected rootDirectory = {
    name: "root",
    children: [
      // {
      //   name: "landscape.png",
      //   key: `1`,
      // }
    ] as any[],
    parent: null,
    key: "0",
    path: "",
  };

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
    { title: "Overview", link: "#overview" },
    {
      title: "Description",
      link: "#description",
      isShown: this.data.description,
    },
    {
      title: "Subject Keywords",
      link: "#subject",
      isShown: this.data.keywords?.length,
    },
    {
      title: "Content",
      link: "#content",
      isShown: this.data.associatedMedia?.length,
    },
    {
      title: "Funding",
      link: "#funding",
      isShown: this.data.funding?.length,
    },
    {
      title: "Related Resources",
      link: "#related",
      isShown: this.data.hasPart?.length,
    },
    {
      title: "Spatial Coverage",
      link: "#spatial-coverage",
      isShown: !this.hasSpatialFeatures,
    },
    {
      title: "Temporal Coverage",
      link: "#temporal-coverage",
      isShown: this.data.temporalCoverage,
    },
  ];

  protected infoLabelAttr = {
    class: "text-subtitle-1 font-weight-light",
  };

  protected infoValueAttr = {
    class: "text-body-1 mb-2",
  };

  created() {
    this.loadDataset();
  }

  onCopy(text: string) {
    navigator.clipboard.writeText(text);
    Notifications.toast({ message: "Copied to clipboard", type: "info" });
  }

  protected get createdBy() {
    return this.data.creator?.map((c) => c.name).join(", ");
  }

  protected get isMd() {
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

        if (this.data.associatedMedia?.length) {
          this.data.associatedMedia.map((m, index) => {
            let fileSizeBytes;

            if (typeof m.contentSize === "string") {
              const parts = m.contentSize.trim().split(" ");
              if (parts.length != 2) {
                fileSizeBytes = undefined;
              } else {
                const num = parts[0];
                const notation = parts[1].toLowerCase();

                // https://wiki.ubuntu.com/UnitsPolicy
                const kib = 1024;
                const mib = 1024 * kib;
                const gib = 1024 * mib;
                const tib = 1024 * gib;

                const kb = 1000;
                const mb = 1024 * kb;
                const gb = 1024 * mb;
                const tb = 1024 * gb;

                let multiplier = 0;

                switch (notation) {
                  case "b":
                    multiplier = 1;
                    break;
                  case "kb":
                    multiplier = kb;
                    break;
                  case "mb":
                    multiplier = mb;
                    break;
                  case "gb":
                    multiplier = gb;
                    break;
                  case "tb":
                    multiplier = tb;
                    break;

                  case "kib":
                    multiplier = kib;
                    break;
                  case "mib":
                    multiplier = mib;
                    break;
                  case "gib":
                    multiplier = gib;
                    break;
                  case "tib":
                    multiplier = tib;
                    break;
                }
                fileSizeBytes = num * multiplier;
              }
            } else if (typeof m.size === "number") {
              fileSizeBytes = m.size;
            }

            this.rootDirectory.children.push({
              name: m.name,
              key: `${index}`,
              file: {
                size: fileSizeBytes,
              },
            });
          });
        }
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
    const feat = this.data.spatialCoverage?.["@type"];
    return feat === "GeoShape" || feat === "GeoCoordinates";
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
  flex-basis: 20rem;
  flex-shrink: 0;
  position: relative;

  .table-of-contents {
    position: sticky;
    top: 6rem;
  }
}

.page-content {
  flex-grow: 1;
  max-width: 100%;

  &.is-sm {
    .dataset-info {
      grid-template-columns: auto;
      gap: 0;
    }
  }
}

#graph-container {
  width: 600px;
  height: 400px;
  border: 1px solid #ddd;
}

.dataset-info {
  display: grid;
  grid-template-columns: auto auto;
  gap: 0rem 1rem;
  justify-content: start;
  align-items: baseline;
  align-content: baseline;

  &.one-col {
    grid-template-columns: auto;
  }
}

::v-deep .map-container {
  width: 100%;
  height: 20rem;
}
</style>
