<template>
  <v-container class="cd-contribute">
    <div v-if="!isLoading && wasLoaded" class="d-flex">
      <div v-if="!$vuetify.breakpoint.mdAndDown" class="sidebar pr-4">
        <div class="table-of-contents">
          <div class="text-h6">Table of contents</div>
          <ol class="text-body-2">
            <li
              v-for="(item, index) of tableOfContents"
              :key="index"
              class="my-2"
            >
              <a :href="item.link">{{ item.title }}</a>
            </li>
          </ol>
        </div>
      </div>

      <div class="page-content">
        <div class="d-flex justify-space-between mb-8">
          <div class="text-h4">{{ data.name }}</div>
          <v-btn
            v-if="!data.repository_identifier"
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

        <div class="dataset-info mb-8">
          <div class="text-subtitle-2 gray--text">Created By:</div>
          <div class="text-body-2">{{ createdBy }}</div>

          <div class="text-subtitle-2">Provider:</div>
          <div class="text-body-2">
            <span v-if="data.provider.url" class="d-flex align-center">
              <a :href="data.provider.url" target="_blank">{{
                data.provider.name
              }}</a>
              <v-icon class="ml-2" small>mdi-open-in-new</v-icon>
            </span>

            <template v-else>{{ data.provider.name }}</template>
          </div>

          <div class="text-subtitle-2">Resource Type:</div>
          <div class="text-body-2">{{ data["@type"] }}</div>

          <div class="text-subtitle-2">Resource Size:</div>
          <div class="text-body-2">some test</div>

          <div class="text-subtitle-2">License:</div>
          <div class="text-body-2">{{ data.license.name }}</div>

          <div class="text-subtitle-2">Host Repository:</div>
          <div class="text-body-2">HydroShare</div>

          <div class="text-subtitle-2">Created:</div>
          <div class="text-body-2">{{ data.dateCreated }}</div>

          <template v-if="data.dateModified">
            <div class="text-subtitle-2">Last Updated:</div>
            <div class="text-body-2">{{ data.dateModified }}</div>
          </template>
        </div>

        <div class="mb-8 field">
          <div class="text-overline primary--text darken-4">Description</div>
          <v-divider class="primary my-1"></v-divider>
          <p class="text-body-1">{{ data.description }}</p>
        </div>

        <div class="mb-8 field">
          <div class="text-overline primary--text darken-4">Url</div>
          <v-divider class="primary my-1"></v-divider>

          <span class="d-flex align-center text-body-1">
            <a :href="data.url" target="_blank">{{ data.url }}</a>
            <v-icon class="ml-2" small>mdi-open-in-new</v-icon>
          </span>
        </div>

        <div class="my-4 field">
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

        <div class="my-4 field">
          <div class="text-overline primary--text darken-4">Language</div>
          <p class="text-body-1">{{ data.inLanguage }}</p>
        </div>

        <div class="my-4 field text-body-1">
          <div class="text-overline primary--text darken-4">
            Spatial and Temporal Coverage
          </div>

          <v-divider class="primary mb-2"></v-divider>

          <v-row>
            <v-col col="12" sm="8">
              <div class="text-subtitle-2">Spatial</div>
              <div class="my-2">metadata here</div>
              <div>
                <v-card flat outlined>
                  <div>MAP HERE</div>
                  <v-divider></v-divider>
                  <v-card-text> coordinates here </v-card-text>
                </v-card>
              </div>
            </v-col>
            <v-col col="12" sm="4">
              <div class="text-subtitle-2">Temporal</div>
              <div>
                <v-stepper flat vertical>
                  <v-stepper-step
                    complete
                    complete-icon="mdi-calendar-start-outline"
                  >
                    <span>Nov 24, 2023</span>
                    <small class="primary--text font-weight-medium mt-1"
                      >Start Date</small
                    >
                  </v-stepper-step>

                  <v-stepper-content></v-stepper-content>

                  <v-stepper-step
                    complete
                    complete-icon="mdi-calendar-end-outline"
                  >
                    <span>Dec 1, 2023</span>
                    <small class="primary--text font-weight-medium mt-1"
                      >End Date</small
                    >
                  </v-stepper-step>

                  <v-stepper-content></v-stepper-content>
                </v-stepper>
              </div>
            </v-col>
          </v-row>
        </div>

        <div class="mb-8 field">
          <div class="text-overline primary--text darken-4">
            Access and Usage
          </div>
          <v-divider class="primary my-1"></v-divider>
        </div>

        <div class="mb-8 field">
          <div class="text-overline primary--text darken-4">
            Related Resources
          </div>
          <v-divider class="primary my-1"></v-divider>
        </div>

        <div class="mb-8 field">
          <div class="text-overline primary--text darken-4">Credits</div>
          <v-divider class="primary my-1"></v-divider>
        </div>

        <div class="mb-8 field">
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

import User from "@/models/user.model";
import { computed } from "vue";

@Component({
  name: "cd-contribute",
  components: { CzForm },
})
export default class CdDataset extends Vue {
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
    { title: "Description", link: "" },
    { title: "Subject Keywords", link: "" },
    { title: "Spatial and Temporal Coverage", link: "" },
    { title: "Access and Usage", link: "" },
    { title: "Additional Metadata", link: "" },
    { title: "Related Resources", link: "" },
    { title: "Credits", link: "" },
    { title: "How to Cite", link: "" },
  ];

  created() {
    this.loadDataset();
  }

  protected get createdBy() {
    return this.data.creator?.map((c) => c.name).join(", ");
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

  protected get schema() {
    return User.$state.schema;
  }

  protected get uiSchema() {
    return User.$state.uiSchema;
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

.page-content {
  flex-grow: 1;
  word-break: break-word;
}

.dataset-info {
  display: grid;
  grid-template-columns: auto auto;
  gap: 0.5rem 1rem;
  justify-content: start;
}
</style>
