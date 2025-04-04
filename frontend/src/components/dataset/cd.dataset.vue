<template>
  <v-container class="cd-contribute">
    <div v-if="!isLoading && wasLoaded" class="d-flex">
      <v-container
        v-if="!$vuetify.display.mdAndDown"
        class="sidebar pr-8 break-word"
      >
        <div class="sidebar--content">
          <v-card variant="outlined" border="grey thin">
            <v-card-title class="pt-4 text-body-1"
              >Table of contents</v-card-title
            >
            <v-card-text class="text-body-2">
              <v-list density="compact">
                <template v-for="(item, index) of tableOfContents">
                  <v-list-item
                    v-if="!(item.isShown?.() === false)"
                    :key="index"
                    :value="index"
                    class="text-body-1"
                    @click="goTo(item.link, scrollOptions)"
                  >
                    {{ item.title }}
                  </v-list-item>
                </template>
              </v-list>
            </v-card-text>
          </v-card>

          <v-card
            v-if="hasSpatialFeatures"
            class="mt-8"
            variant="outlined"
            border="grey thin"
          >
            <v-card-title class="text-overline">
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
                      <v-col cols="12" class="dataset-info">
                        <div v-bind="infoLabelAttr">Latitude:</div>
                        <div v-bind="infoValueAttr">
                          {{ data.spatialCoverage.geo.latitude }}°
                        </div>
                      </v-col>

                      <v-col cols="12" class="dataset-info">
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
                    <div v-bind="infoValueAttr">
                      {{ data.spatialCoverage.name }}
                    </div>
                  </v-card-text>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card>

          <v-card
            v-if="data.temporalCoverage"
            class="mt-8"
            variant="outlined"
            border="grey thin"
          >
            <v-card-title class="text-overline primary--text darken-4">
              Temporal Coverage
            </v-card-title>
            <v-divider></v-divider>

            <v-card-text>
              <v-timeline align-top density="compact" line-color="info">
                <v-timeline-item
                  dot-color="primary"
                  icon="mdi-calendar"
                  fill-dot
                >
                  <div>
                    <strong>Start Date</strong>
                    <div>{{ parseDate(data.temporalCoverage.startDate) }}</div>
                  </div>
                </v-timeline-item>

                <v-timeline-item
                  dot-color="orange-darken-2"
                  icon="mdi-calendar"
                  fill-dot
                >
                  <div>
                    <strong>End Date</strong>
                    <div>{{ parseDate(data.temporalCoverage.endDate) }}</div>
                  </div>
                </v-timeline-item>
              </v-timeline>
            </v-card-text>
          </v-card>

          <v-card
            v-if="data.citation && data.citation.length"
            class="mt-8"
            variant="flat"
          >
            <v-card-title class="pa-0 pb-2">How to cite</v-card-title>
            <v-card-text
              v-for="(citation, index) of data.citation"
              :key="index"
              class="pa-0"
            >
              <div class="d-flex align-center justify-space-between gap-1">
                <div class="citation-text">
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
        </div>
      </v-container>

      <div
        id="overview"
        class="page-content"
        :class="{ 'is-sm': $vuetify.display.mdAndDown }"
      >
        <h4 class="text-h5 my-4">{{ data.name }}</h4>
        <div
          class="d-flex justify-space-between mb-2 flex-column flex-sm-row align-normal align-sm-end"
        >
          <div
            v-if="data.creativeWorkStatus || data.dateModified"
            class="order-2 order-sm-1"
          >
            <v-chip
              v-if="data.creativeWorkStatus"
              small
              class="mr-2"
              :color="getStautsColor(data.creativeWorkStatus.name)"
              :title="data.creativeWorkStatus.description"
            >
              {{ data.creativeWorkStatus.name }}
            </v-chip>

            <template v-if="data.dateModified">
              <span class="d-block d-sm-inline" v-bind="infoLabelAttr"
                >Last Updated:
              </span>
              <span v-bind="infoValueAttr">
                {{ parseDate(data.dateModified) }}
                <span class="font-weight-light">
                  (<timeago :datetime="data.dateModified" />)
                </span>
              </span>
            </template>
          </div>

          <!-- TODO: disabled until dataset endpoint returns current user permissions -->
          <!-- <div class="order-1 order-sm-2">
            <v-btn
              v-if="data.submission_type !== 'HYDROSHARE'"
              class="order-1 order-sm-2 mb-sm-0 mb-4 mt-sm-0 mt-2"
              @click="
                router.push({
                  name: 'dataset-edit',
                  params: { id: data._id },
                })
              "
              rounded
            >
              <v-icon>mdi-text-box-edit</v-icon><span class="ml-1">Edit</span>
            </v-btn>

            <v-btn
              v-if="data.repository_identifier"
              :href="data.repository_identifier"
              target="_blank"
              color="blue-grey lighten-4"
              rounded
            >
              <v-icon class="mr-1">mdi-open-in-new</v-icon> View in repository
            </v-btn>
          </div> -->
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
                  <span
                    class="mr-2 cursor-pointer"
                    v-bind="{ ...props, ...infoValueAttr }"
                  >
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
                        icon="mdi-email-outline"
                      />
                      {{ creator.email }}
                    </div>
                    <div v-if="creator.identifier" class="d-flex align-center">
                      <i
                        class="fab fa-orcid mr-2 text-secondary text-h6"
                        aria-hidden="true"
                        title="ORCID"
                      ></i>
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
                        <a :href="creator.affiliation.url">{{
                          creator.affiliation.name
                        }}</a>
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

            <template v-if="data.provider">
              <div v-bind="infoLabelAttr">Provider:</div>
              <div v-bind="infoValueAttr">
                <span v-if="data.provider.url" class="d-flex align-baseline">
                  <a :href="data.provider.url">{{ data.provider.name }}</a>
                </span>

                <template v-else>{{ data.provider.name }}</template>
              </div>
            </template>

            <template v-if="data.publisher">
              <div v-bind="infoLabelAttr">Publisher:</div>
              <div v-bind="infoValueAttr">
                <span v-if="data.publisher.url" class="d-flex align-baseline">
                  <a :href="data.publisher.url">{{ data.publisher.name }}</a>
                </span>

                <template v-else>{{ data.publisher.name }}</template>
              </div>
            </template>

            <div v-bind="infoLabelAttr">Resource Type:</div>
            <div v-bind="infoValueAttr">{{ data["@type"] }}</div>

            <template v-if="contentSize">
              <div v-bind="infoLabelAttr">Resource Size:</div>
              <div v-bind="infoValueAttr">~{{ contentSize }}</div>
            </template>

            <div v-bind="infoLabelAttr">License:</div>
            <div v-bind="infoValueAttr">
              <div v-if="data.license.url" class="d-flex align-baseline">
                <a :href="data.license.url">{{ data.license.name }}</a>
              </div>

              <template v-else>{{ data.license.name }}</template>

              <div class="font-weight-light text-subtitle-2">
                {{ data.license.description }}
              </div>
            </div>

            <template v-if="data.inLanguage">
              <div v-bind="infoLabelAttr">Language:</div>
              <div v-bind="infoValueAttr">{{ data.inLanguage }}</div>
            </template>

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

            <template v-if="data.submission_type === 'HYDROSHARE'">
              <div v-bind="infoLabelAttr">Host Repository:</div>
              <div v-bind="infoValueAttr">
                <v-card variant="outlined" border="grey thin">
                  <v-card-title class="text-overline">HydroShare</v-card-title>
                  <v-divider></v-divider>
                  <v-card-text>
                    <v-img
                      max-width="200"
                      contain
                      class="mt-2"
                      alt="HydroShare logo"
                      src="/img/hydroshare.png"
                    ></v-img>
                  </v-card-text>
                </v-card>
              </div>
            </template>

            <template v-if="data.submission_type === 'S3'">
              <div v-bind="infoLabelAttr">Host Repository:</div>
              <div>
                <v-card variant="outlined" border="grey thin">
                  <v-card-title class="text-overline">Amazon S3</v-card-title>
                  <v-divider></v-divider>
                  <v-card-text>
                    <v-img
                      max-width="200"
                      max-height="30"
                      contain
                      class="mt-2"
                      alt="Amazon S3 logo"
                      src="/img/amazon-s3.svg"
                    ></v-img>
                  </v-card-text>
                  <v-divider></v-divider>

                  <v-expansion-panels accordion flat>
                    <v-expansion-panel>
                      <v-expansion-panel-title color="text-overline">
                        Bucket Information
                      </v-expansion-panel-title>

                      <v-expansion-panel-text>
                        <v-table variant="elevated" density="compact">
                          <tbody>
                            <tr>
                              <th>Path:</th>
                              <td>{{ data.s3_path.path }}</td>
                            </tr>
                            <tr>
                              <th>Bucket:</th>
                              <td>{{ data.s3_path.bucket }}</td>
                            </tr>
                            <tr>
                              <th>Endpoint URL:</th>
                              <td>
                                <a :href="data.s3_path.endpoint_url">{{
                                  data.s3_path.endpoint_url
                                }}</a>
                              </td>
                            </tr>
                          </tbody>
                        </v-table>
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </v-card>
              </div>
            </template>
          </v-col>
        </v-row>

        <div class="mb-8 field" id="url">
          <div class="text-overline primary--text darken-4">URL</div>
          <v-divider class="primary my-1"></v-divider>
          <p class="text-body-1">
            <a :href="data.url" class="break-word">{{ data.url }}</a>
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
            density="compact"
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
            id="fileExplorer"
          />

          <v-card
            v-if="readmeMd || isLoadingMD"
            class="readme-container"
            variant="outlined"
            border="grey thin"
          >
            <v-card-title class="text-overline">README</v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <div class="text-center py-4" v-if="isLoadingMD">
                <v-progress-circular
                  indeterminate
                  class="text-center"
                  color="primary"
                />
              </div>
              <div v-html="readmeMd" class="markdown-body px-4"></div>
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
                  v-if="!(funding.description || !!funding.funder)"
                  ><span></span
                ></template>
              </v-expansion-panel-title>

              <v-expansion-panel-text
                v-if="funding.description || !!funding.funder"
              >
                <div
                  class="pt-2 text-body-2 font-weight-light"
                  v-if="funding.description"
                >
                  {{ funding.description }}
                </div>
                <template v-if="!!funding.funder">
                  <div class="d-flex align-center text-body-1 mt-4 mb-2">
                    <v-icon class="mr-2"> mdi-domain </v-icon>
                    <div>Funding Organization:</div>
                  </div>
                  <div class="text-body-2">
                    <div class="text-body-1">
                      {{ funding.funder.name }}
                    </div>
                    <div>{{ funding.funder.address }}</div>
                    <a :href="funding.funder.url">{{ funding.funder.url }} </a>
                  </div>
                </template>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>

        <div
          v-if="
            data.hasPart?.length ||
            data.isPartOf?.length ||
            data.subjectOf?.length
          "
          class="mb-8 field"
          id="related"
        >
          <div class="text-overline primary--text darken-4">
            Related Resources
          </div>
          <v-divider class="primary mt-1 mb-4"></v-divider>
          <v-card variant="outlined" border="grey thin">
            <v-table>
              <template v-slot:default>
                <tbody>
                  <tr
                    v-for="(part, index) in data.hasPart"
                    :key="`hp-${index}`"
                  >
                    <td class="">Has part</td>
                    <td>
                      <a :href="part.url">{{ part.name }}</a>
                    </td>
                  </tr>

                  <tr
                    v-for="(part, index) in data.isPartOf"
                    :key="`hp-${index}`"
                  >
                    <td class="">Is part of</td>
                    <td>
                      <a :href="part.url">{{ part.name }}</a>
                    </td>
                  </tr>

                  <tr
                    v-for="(part, index) in data.subjectOf"
                    :key="`hp-${index}`"
                  >
                    <td class="">Subject of</td>
                    <td>
                      <a :href="part.url">{{ part.name }}</a>
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-table>
          </v-card>
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
              <v-card variant="outlined" border="grey thin">
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
              <div v-bind="infoValueAttr">{{ data.spatialCoverage.name }}</div>
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

          <v-timeline align-top density="compact" line-color="info">
            <v-timeline-item dot-color="primary">
              <div>
                <div class="font-weight-normal">
                  <strong>Start Date</strong>
                </div>
                <div>{{ parseDate(data.temporalCoverage.startDate) }}</div>
              </div>
            </v-timeline-item>

            <v-timeline-item dot-color="orange">
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
      type="error"
      variant="text"
      prominent
      density="compact"
      elevation="1"
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

        <v-divider />

        <v-card-text>
          <v-table>
            <tbody>
              <tr v-if="selectedMetadata.metadata?.contentUrl">
                <th>Content URL</th>
                <td>
                  <a
                    :href="getFileURL(selectedMetadata)"
                    :download="selectedMetadata.name"
                    >{{ selectedMetadata.metadata?.contentUrl }}</a
                  >
                </td>
              </tr>
              <tr v-if="selectedMetadata.metadata?.encodingFormat">
                <th>Encoding Format</th>
                <td>{{ selectedMetadata.metadata?.encodingFormat }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>

        <v-divider />

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
import markdownit from "markdown-it";
import { Component, Vue, toNative } from "vue-facing-decorator";
import { useGoTo } from "vuetify/lib/framework.mjs";
import { useRoute, useRouter } from "vue-router";
import { EnumCreativeWorkStatus } from "@/types";
import { sizeToBytes } from "@/util";
import prettyBytes from "pretty-bytes";

const options: LoaderOptions = { libraries: ["drawing"] };
const loader: Loader = new Loader(
  import.meta.env.VITE_APP_GOOGLE_MAPS_API_KEY,
  options,
);

const md = markdownit({
  linkify: true,
  typographer: true,
  breaks: true,
  html: true,
});

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
  showCoordinateSystem = false;
  showExtent = false;
  isLoadingMD = false;
  prettyBytes = prettyBytes;

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
    offset: -80,
    easing: "easeInOutCubic",
  };

  tableOfContents: any[] = [];

  infoLabelAttr = {
    class: "text-subtitle-1 font-weight-light",
  };

  infoValueAttr = {
    class: "text-body-1 mb-2",
  };

  route = useRoute();
  router = useRouter();

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

  get contentSize() {
    let total = 0;

    if (this.data.associatedMedia?.length) {
      total = this.data.associatedMedia.reduce(
        (acc: number, m: any, _index: number) => {
          let size = 0;

          if (typeof m.contentSize === "string") {
            size = sizeToBytes(m.contentSize);
          } else if (typeof m.size === "number") {
            size = m.size;
          }

          acc += size;
          return acc;
        },
        0,
      );
    }
    return prettyBytes(total);
  }

  async created() {
    await this.loadDataset();

    this.tableOfContents = [
      { title: "Overview", link: 0 },
      {
        title: "Url",
        link: "#url",
      },
      {
        title: "Description",
        link: "#description",
        isShown: () => !!this.data.description || false,
      },
      {
        title: "Subject Keywords",
        link: "#subject",
        isShown: () => this.data.keywords?.length || false,
      },
      {
        title: "Content",
        link: "#content",
        isShown: () => this.data.associatedMedia?.length || false,
      },
      {
        title: "Funding",
        link: "#funding",
        isShown: () => this.data.funding?.length || false,
      },
      {
        title: "Related Resources",
        link: "#related",
        isShown: () => this.data.hasPart?.length || false,
      },
      {
        title: "Spatial Coverage",
        link: "#spatial-coverage",
        isShown: () =>
          (!!this.hasSpatialFeatures && this.$vuetify.display.mdAndDown) ||
          false,
      },
      {
        title: "Temporal Coverage!!",
        link: "#temporal-coverage",
        isShown: () =>
          (this.data.temporalCoverage && this.$vuetify.display.mdAndDown) ||
          false,
      },
    ];
  }

  onShowMetadata(item: any) {
    this.selectedMetadata = item;
    this.showMetadata = true;
  }

  onCopy(text: string) {
    navigator.clipboard.writeText(text);
    Notifications.toast({ message: "Copied to clipboard", type: "info" });
  }

  getStautsColor(status: EnumCreativeWorkStatus) {
    switch (status) {
      case EnumCreativeWorkStatus.Draft:
        return "primary";
      case EnumCreativeWorkStatus.Incomplete:
        return "red";
      case EnumCreativeWorkStatus.Obsolete:
        return "orange";
      case EnumCreativeWorkStatus.Published:
        return "green";
      default:
        "primary";
    }
  }

  loadFileExporer() {
    // Load file explorer
    if (this.data.associatedMedia?.length) {
      this.data.associatedMedia.map((m: any, _index: number) => {
        let fileSizeBytes;

        if (typeof m.contentSize === "string") {
          fileSizeBytes = sizeToBytes(m.contentSize);
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
    const readmeFile = this.data.associatedMedia?.find(
      (f: any) => f.name.toLowerCase() === "readme.md",
    );

    if (readmeFile?.contentUrl) {
      const url = readmeFile.contentUrl.replace("http:", "https:");
      try {
        this.isLoadingMD = true;
        const response = await fetch(url);
        const rawMd = await response.text();
        this.readmeMd = md.render(rawMd);
      } catch (e) {
        console.log(e);
      } finally {
        this.isLoadingMD = false;
      }
    }
  }

  async loadDataset() {
    this.submissionId = this.route.params.id as string;
    this.isLoading = true;
    try {
      const data = await User.fetchDataset(this.submissionId);
      if (data) {
        this.data = data;

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

  getFileURL(fileMetadata: any): string {
    const url = fileMetadata.metadata?.contentUrl;
    if (url) {
      return url.startsWith("http:") ? url.replace("http:", "https:") : url;
    }
    return "";
  }

  parseDate(date: string): string {
    const parsed = new Date(Date.parse(date));
    return parsed.toLocaleString("default", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  }
}

export default toNative(CdDataset);
</script>

<style lang="scss" scoped>
.sidebar {
  flex-basis: 25rem;
  flex-shrink: 0;
  position: relative;
  min-width: 0;

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

  .markdown-body {
    box-sizing: border-box;
    min-width: 200px;
    max-width: 980px;
    padding: 45px;
    font-family: inherit;
  }

  @media (max-width: 767px) {
    .markdown-body {
      padding: 15px;
    }
  }
}

.page-content {
  flex-grow: 1;
  max-width: 100%;
  min-width: 0;

  &.is-sm {
    .dataset-info {
      grid-template-columns: auto;
      gap: 0;
    }
  }
}

:deep(.map-container) {
  min-height: 15rem;
}

.citation-text {
  min-width: 0;
  word-break: break-word;
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

:deep(#fileExplorer .v-sheet) {
  background-color: #f6f6f6 !important;
}
</style>
