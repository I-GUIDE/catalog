<template>
  <v-container class="cd-contribute">
    <div v-if="!isLoading && wasLoaded" class="d-flex">
      <v-container
        v-if="!$vuetify.display.mdAndDown"
        class="sidebar pr-8 break-word"
      >
        <div class="sidebar--content">
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

                <a @click="goTo(item.link, scrollOptions)">{{ item.title }}</a>
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
                  <template v-slot:activator="{ props }">
                    <v-btn icon v-bind="props" @click="onCopy(citation)">
                      <v-icon dark> mdi-content-copy </v-icon>
                    </v-btn>
                  </template>
                  <span>Copy</span>
                </v-tooltip>
              </div>
            </v-card-text>
          </v-card>

          <v-card
            v-if="hasSpatialFeatures"
            class="mt-8"
            variant="elevated"
            elevation="2"
          >
            <v-card-title class="text-overline primary--text darken-4">
              Spatial Coverage
            </v-card-title>
            <cd-spatial-coverage-map
              :loader="loader"
              :feature="data.spatialCoverage.geo"
              :key="route.fullPath"
              :flat="true"
            />
            <v-divider></v-divider>
            <v-expansion-panels accordion flat>
              <v-expansion-panel>
                <v-expansion-panel-title color="text-overline">
                  Extent
                </v-expansion-panel-title>

                <v-expansion-panel-text>
                  <v-card-text
                    v-if="data.spatialCoverage.geo['@type'] == 'GeoShape'"
                  >
                    <v-row class="align-start">
                      <v-col cols="12" class="dataset-info pa-0">
                        <div v-bind="infoLabelAttr">North Latitude:</div>
                        <div v-bind="infoValueAttr" class="text-right">
                          {{ boxCoordinates.north }}°
                        </div>

                        <div v-bind="infoLabelAttr">East Longitude:</div>
                        <div v-bind="infoValueAttr" class="text-right">
                          {{ boxCoordinates.east }}°
                        </div>

                        <div v-bind="infoLabelAttr">South Latitude:</div>
                        <div v-bind="infoValueAttr" class="text-right">
                          {{ boxCoordinates.south }}°
                        </div>

                        <div v-bind="infoLabelAttr">West Longitude:</div>
                        <div v-bind="infoValueAttr" class="text-right">
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
                </v-expansion-panel-text>
              </v-expansion-panel>

              <v-expansion-panel>
                <v-expansion-panel-title color="text-overline">
                  Coordinate System
                </v-expansion-panel-title>

                <v-expansion-panel-text>
                  <v-card-text class="dataset-info one-col pa-0">
                    <div v-bind="infoLabelAttr">
                      Coordinate System/Geographic Projection:
                    </div>
                    <div v-bind="infoValueAttr">WGS 84 EPSG:4326</div>

                    <div v-bind="infoLabelAttr">Coordinate Units:</div>
                    <div v-bind="infoValueAttr">Decimal degrees</div>

                    <div v-bind="infoLabelAttr">Place/Area Name:</div>
                    <div v-bind="infoValueAttr">Woodlawn, MD</div>
                  </v-card-text>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card>

          <v-card
            v-if="data.temporalCoverage"
            class="mt-8"
            variant="elevated"
            elevation="2"
          >
            <v-card-title class="text-overline primary--text darken-4">
              Temporal Coverage
            </v-card-title>
            <v-divider></v-divider>

            <v-card-text>
              <v-timeline align-top dense>
                <v-timeline-item small>
                  <div>
                    <div class="font-weight-normal">
                      <strong>Start Date</strong>
                    </div>
                    <div>{{ parseDate(data.temporalCoverage.startDate) }}</div>
                  </div>
                </v-timeline-item>

                <v-timeline-item small color="orange">
                  <div>
                    <div class="font-weight-normal">
                      <strong>End Date</strong>
                    </div>
                    <div>{{ parseDate(data.temporalCoverage.endDate) }}</div>
                  </div>
                </v-timeline-item>
              </v-timeline>
            </v-card-text>
          </v-card>
        </div>
      </v-container>

      <div
        id="overview"
        class="page-content"
        :class="{ 'is-sm': $vuetify.display.mdAndDown }"
      >
        <h4 class="text-h4">{{ data.name }}</h4>
        <div
          class="d-flex justify-space-between mb-2 flex-column flex-sm-row align-normal align-sm-end"
        >
          <div class="order-2 order-sm-1">
            <v-chip
              small
              class="mr-2"
              color="green"
              text-color="white"
              title="The resource is in draft state and should not be considered final. Content and metadata may change."
            >
              Draft
            </v-chip>
            <template v-if="data.dateModified">
              <span class="d-block d-sm-inline" v-bind="infoLabelAttr"
                >Last Updated:</span
              >
              <span v-bind="infoValueAttr">
                {{ parseDate(data.dateModified) }}
                <span class="font-weight-light">
                  <!-- (<timeago :datetime="data.dateModified"> </timeago>) -->
                </span>
              </span>
            </template>
          </div>
          <v-btn
            v-if="!data.repository_identifier"
            class="order-1 order-sm-2 mb-sm-0 mb-4 mt-sm-0 mt-2"
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

        <v-row
          class="my-4 align-start"
          :no-gutters="$vuetify.display.smAndDown"
        >
          <v-col cols="12" sm="6" class="dataset-info">
            <div v-bind="infoLabelAttr">Created By:</div>

            <div class="infoValueAttr">
              <v-menu
                v-for="(creator, index) of data.creator"
                offset-y
                :close-on-content-click="false"
                class="d-inline"
                :key="index"
              >
                <template v-slot:activator="{ props }">
                  <span class="mr-2" v-bind="{ ...props, ...infoValueAttr }">
                    <div class="d-inline-block">
                      {{ creator.name }} <v-icon small>mdi-menu-down</v-icon>
                    </div>
                  </span>
                </template>
                <v-card v-if="creator['@type'] == 'Person'">
                  <v-card-title class="text-body-1">
                    <!-- <v-icon color="white" class="mr-2"
                      >mdi-account-outline</v-icon
                    > -->
                    {{ creator.name }}
                  </v-card-title>
                  <v-divider></v-divider>

                  <v-card-text
                    v-if="creator.email || creator.identifier"
                    class="d-flex flex-column gap-1"
                  >
                    <div v-if="creator.email">
                      <v-icon
                        class="mr-1"
                        small
                        color="secondary"
                        title="Email address"
                        >mdi-email-outline</v-icon
                      >
                      {{ creator.email }}
                    </div>
                    <div v-if="creator.identifier">
                      <v-icon
                        class="mr-1"
                        small
                        color="secondary"
                        title="ORCID identifier"
                        >fab fa-orcid</v-icon
                      >
                      {{ creator.identifier }}
                    </div>
                  </v-card-text>

                  <v-card-text v-if="creator.affiliation">
                    <div class="d-flex align-center">
                      <v-icon
                        small
                        color="secondary"
                        class="mr-1"
                        title="Affiliation"
                      >
                        mdi-domain
                      </v-icon>
                      Affiliation:
                    </div>
                    <v-divider class="my-2"></v-divider>
                    <div
                      v-if="creator.affiliation.name"
                      class="font-weight-bold mb-2"
                    >
                      <span
                        v-if="creator.affiliation.url"
                        class="d-inline-flex align-baseline"
                      >
                        <a :href="creator.affiliation.url" target="_blank">{{
                          creator.affiliation.name
                        }}</a>
                        <v-icon class="ml-2" small>mdi-open-in-new</v-icon>
                      </span>
                      <span v-else>{{ creator.affiliation.name }}</span>
                    </div>

                    <div v-if="creator.affiliation.address">
                      {{ creator.affiliation.address }}
                    </div>
                  </v-card-text>
                </v-card>
              </v-menu>
            </div>

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

              <div class="font-weight-light text-subtitle-2">
                {{ data.license.description }}
              </div>
            </div>

            <div v-bind="infoLabelAttr">Language:</div>
            <div v-bind="infoValueAttr">{{ data.inLanguage }}</div>

            <template v-if="data.version">
              <div v-bind="infoLabelAttr">Version:</div>
              <div v-bind="infoValueAttr">{{ data.version }}</div>
            </template>
          </v-col>

          <v-col cols="12" sm="6" class="dataset-info">
            <!-- <div v-bind="infoLabelAttr">URL:</div>
            <div
              v-bind="infoValueAttr"
              class="d-flex align-baseline text-body-1"
            >
              <a :href="data.url" target="_blank" class="break-word">{{
                data.url
              }}</a>
              <v-icon class="ml-2" small>mdi-open-in-new</v-icon>
            </div> -->

            <div v-bind="infoLabelAttr">Created:</div>
            <div v-bind="infoValueAttr">
              {{ parseDate(data.dateCreated) }}
            </div>

            <template v-if="data.datePublished">
              <div v-bind="infoLabelAttr">Published:</div>
              <div v-bind="infoValueAttr">
                {{ parseDate(data.datePublished) }}
              </div>
            </template>

            <div v-bind="infoLabelAttr">Host Repository:</div>
            <div v-bind="infoValueAttr">
              HydroShare
              <v-img
                max-width="200"
                contain
                class="mt-2"
                alt="HydroShare logo"
                :src="'/img/hydroshare.png'"
              ></v-img>
            </div>
          </v-col>
        </v-row>

        <div class="mb-8 field" id="url">
          <div class="text-overline primary--text darken-4">URL</div>
          <v-divider class="primary my-1"></v-divider>
          <p class="text-body-1">
            <a :href="data.url" target="_blank" class="break-word">{{
              data.url
            }}</a>
            <v-icon class="ml-2" small>mdi-open-in-new</v-icon>
          </p>
        </div>

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
          <v-divider class="primary mt-1 mb-4"></v-divider>

          <cz-file-explorer
            :rootDirectory="rootDirectory"
            :isReadOnly="true"
            :hasFileMetadata="() => true"
            @showMetadata="onShowMetadata($event)"
          />

          <v-card v-if="readmeMd" class="readme-container" flat outlined>
            <v-card-title>README</v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <pre v-html="readmeMd"></pre>
              <!-- <vue-marked :marked="marked">{{ readmeMd }}</vue-marked> -->
            </v-card-text>
          </v-card>
        </div>

        <div
          v-if="data.funding && data.funding.length"
          class="mb-8 field"
          id="funding"
        >
          <div class="text-overline primary--text darken-4">Funding</div>
          <v-divider class="primary mt-1 mb-4"></v-divider>
          <v-expansion-panels multiple>
            <v-expansion-panel
              v-for="(funding, index) of data.funding"
              :key="index"
              :readonly="!(funding.description || funding.funder)"
            >
              <v-expansion-panel-title>
                <div>
                  <div class="text-body-1">{{ funding.name }}</div>

                  <div
                    v-if="funding.identifier"
                    class="text-body-2 font-weight-light"
                  >
                    Award number: {{ funding.identifier }}
                  </div>
                </div>

                <template
                  v-slot:actions
                  v-if="!(funding.description || funding.funder)"
                  ><span></span
                ></template>
              </v-expansion-panel-title>

              <v-expansion-panel-text
                v-if="funding.description || funding.funder"
              >
                <div
                  class="pt-2 text-body-2 font-weight-light"
                  v-if="funding.description"
                >
                  {{ funding.description }}
                </div>
                <template v-if="funding.funder">
                  <div class="d-flex align-center text-body-1 mt-4 mb-2">
                    <v-icon class="mr-2"> mdi-domain </v-icon>
                    <div>Funding Organization:</div>
                  </div>
                  <div class="text-body-2 font-weight-light">
                    <div class="text-body-1">
                      {{ funding.funder.name }}
                    </div>
                    <div>{{ funding.funder.address }}</div>
                    <a
                      class="font-weight-light"
                      :href="funding.funder.url"
                      target="_blank"
                      >{{ funding.funder.url }}
                    </a>
                  </div>
                </template>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
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
          <v-table>
            <template v-slot:default>
              <tbody>
                <tr v-for="(part, index) in data.hasPart" :key="`hp-${index}`">
                  <td class="">Has Part</td>
                  <td>
                    <a :href="part.url" target="_blank">{{ part.name }}</a>
                  </td>
                </tr>
              </tbody>
            </template>
          </v-table>
        </div>

        <div
          v-if="hasSpatialFeatures && $vuetify.display.mdAndDown"
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
                  :key="route.fullPath"
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

        <div
          v-if="data.temporalCoverage && $vuetify.display.mdAndDown"
          class="mb-8 field text-body-1"
        >
          <div class="text-overline primary--text darken-4">
            Temporal Coverage
          </div>
          <v-divider class="primary mb-2"></v-divider>

          <v-timeline align-top dense>
            <v-timeline-item small>
              <div>
                <div class="font-weight-normal">
                  <strong>Start Date</strong>
                </div>
                <div>{{ parseDate(data.temporalCoverage.startDate) }}</div>
              </div>
            </v-timeline-item>

            <v-timeline-item small color="orange">
              <div>
                <div class="font-weight-normal">
                  <strong>End Date</strong>
                </div>
                <div>{{ parseDate(data.temporalCoverage.endDate) }}</div>
              </div>
            </v-timeline-item>
          </v-timeline>
        </div>
      </div>
    </div>
    <div v-else-if="isLoading" class="text-h6 text--secondary my-12">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <v-alert
      v-else-if="!wasLoaded && !isLoading"
      border="start"
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

    <v-dialog v-model="showMetadata" width="800">
      <v-card>
        <v-card-title class="flex-column align-start">
          <div>{{ selectedMetadata.name }}</div>
          <div class="text-caption">
            {{ selectedMetadata.metadata?.contentSize }}
          </div>
        </v-card-title>

        <v-card-text>
          <div>Metadata here...</div>
          <div>{{ selectedMetadata.metadata?.contentUrl }}</div>
          <div>{{ selectedMetadata.metadata?.encodingFormat }}</div>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="showMetadata = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { CzFileExplorer, Notifications } from "@cznethub/cznet-vue-core";
import { Loader, LoaderOptions } from "google-maps";
import CdSpatialCoverageMap from "@/components/search-results/cd.spatial-coverage-map.vue";
import User from "@/models/user.model";

const options: LoaderOptions = { libraries: ["drawing"] };
const loader: Loader = new Loader(
  import.meta.env.VUE_APP_GOOGLE_MAPS_API_KEY,
  options,
);

import markdownit from "markdown-it";
const md = markdownit();

import { Component, Vue, toNative } from "vue-facing-decorator";
import { useGoTo } from "vuetify/lib/framework.mjs";
import { useRoute } from "vue-router";

@Component({
  name: "cd-dataset",
  components: { CdSpatialCoverageMap, CzFileExplorer },
})
class CdDataset extends Vue {
  goTo = useGoTo();
  loader = loader;
  options = options;
  data: any = {};
  isLoading = true;
  wasLoaded = false;
  submissionId = "";
  tab = 0;
  selectedMetadata: any = false;
  readmeMd = "";
  // marked = marked;
  showCoordinateSystem = false;
  showExtent = false;

  /** Example folder/file tree structure */
  rootDirectory = {
    name: "root",
    children: [] as any[],
  };

  showMetadata = false;

  config = {
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

  scrollOptions = {
    offset: 20,
    easing: "easeInOutCubic",
  };

  tableOfContents = [
    { title: "Overview", link: 0 },
    {
      title: "Url",
      link: "#url",
    },
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
      isShown: this.hasSpatialFeatures && this.$vuetify.display.mdAndDown,
    },
    {
      title: "Temporal Coverage",
      link: "#temporal-coverage",
      isShown: !!this.data.temporalCoverage && this.$vuetify.display.mdAndDown,
    },
  ];

  infoLabelAttr = {
    class: "text-subtitle-1 font-weight-light",
  };

  infoValueAttr = {
    class: "text-body-1 mb-2",
  };

  route = useRoute();

  created() {
    this.loadDataset();
  }

  onShowMetadata(item: any) {
    this.selectedMetadata = item;
    this.showMetadata = true;
  }

  onCopy(text: string) {
    navigator.clipboard.writeText(text);
    Notifications.toast({ message: "Copied to clipboard", type: "info" });
  }

  loadFileExporer() {
    // Load file explorer
    if (this.data.associatedMedia?.length) {
      this.data.associatedMedia.map((m: any, index: number) => {
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
          file: {
            size: fileSizeBytes,
          },
          metadata: m,
        });
      });
    }
  }

  async loadReadmeFile() {
    const readmeFile = this.data.associatedMedia.find(
      (f: any) => f.name.toLowerCase() === "readme.md",
    );

    if (readmeFile?.contentUrl) {
      try {
        const response = await fetch(readmeFile.contentUrl);
        const rawMd = await response.text();
        this.readmeMd = md.render(rawMd);

        // this.marked.setOptions({
        //   // ...
        // });
      } catch (e) {
        console.log(e);
      }
    }
  }

  async loadDataset() {
    this.submissionId = useRoute().params.id as string;
    this.isLoading = true;
    try {
      const data = await User.fetchDataset(this.submissionId);
      if (data) {
        this.data = data;
        console.log(data);

        this.loadFileExporer();
        this.loadReadmeFile();
      }
      this.wasLoaded = !!data;
    } catch (e) {
      this.wasLoaded = false;
    } finally {
      this.isLoading = false;
    }
  }

  parseDate(date: string): string {
    const parsed = new Date(Date.parse(date));
    return parsed.toLocaleString("default", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  }

  // getTransformedSpatialCoverage() {
  //   return { ...data.spatialCoverage, }
  // }

  get hasSpatialFeatures(): boolean {
    const feat = this.data.spatialCoverage?.["@type"];
    return feat === "GeoShape" || feat === "GeoCoordinates" || feat === "Place";
  }

  get schema() {
    return User.$state.schema;
  }

  get uiSchema() {
    return User.$state.uiSchema;
  }

  get boxCoordinates() {
    const extents = this.data.spatialCoverage.geo.box
      .trim()
      .split(" ")
      .map((n: string) => +n);
    return {
      north: extents[0],
      east: extents[1],
      south: extents[2],
      west: extents[3],
    };
  }
}

export default toNative(CdDataset);
</script>

<style lang="scss" scoped>
.sidebar {
  flex-basis: 25rem;
  flex-shrink: 0;
  position: relative;

  .sidebar--content {
    position: sticky;
    top: 6rem;
  }
}

.readme-container {
  .v-card__text {
    min-height: 5rem;
    overflow: auto;
    resize: vertical;
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
    grid-template-columns: 1fr;
  }
}
</style>
