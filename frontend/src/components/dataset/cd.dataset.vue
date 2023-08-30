<template>
  <v-container class="cd-contribute">
    <div class="display-1">Dataset</div>
    <v-divider class="my-4"></v-divider>
    <div v-if="wasLoaded" class="d-flex gap-1">
      <v-spacer></v-spacer>
      <template v-if="data.repository_identifier">
        <v-menu bottom left offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn rounded v-bind="attrs" v-on="on">
              <v-icon class="mr-2">mdi-open-in-app</v-icon>
              <span>Open with</span>
              <v-icon>mdi-menu-down</v-icon>
            </v-btn>
          </template>

          <v-list class="pa-0">
            <v-list-item :href="jupyterHubUrl" target="_blank">
              <v-list-item-icon class="mr-2">
                <v-icon>mdi-open-in-new</v-icon>
              </v-list-item-icon>

              <v-list-item-content>
                <v-list-item-title>JupyterHub</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
      <template v-else>
        <v-btn
          @click="
            $router.push({
              name: 'dataset-edit',
              params: { id: data._id },
            })
          "
          rounded
        >
          <v-icon class="mr-2">mdi-text-box-edit</v-icon><span>Edit</span>
        </v-btn>
      </template>
    </div>
    <template v-if="!isLoading && wasLoaded">
      <cz-form
        v-if="!isLoading"
        :schema="schema"
        :uischema="uiSchema"
        :data="data"
        :config="config"
      />
    </template>
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
    <!-- Uncomment to view a card with the data object in the UI -->
    <!-- <v-card>
      <v-card-text>
        <pre>{{ data }}</pre>
      </v-card-text>
    </v-card> -->
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { CzForm } from "@cznethub/cznet-vue-core";
import { JUPYTERHUB_DOMAIN } from "@/constants";

import User from "@/models/user.model";

@Component({
  name: "cd-contribute",
  components: { CzForm },
})
export default class CdDataset extends Vue {
  protected data = {};
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

  created() {
    this.loadDataset();
  }

  protected async loadDataset() {
    this.submissionId = this.$route.params.id;
    this.isLoading = true;
    try {
      const data = await User.fetchDataset(this.submissionId);
      if (data) {
        this.data = data;
      }
      this.wasLoaded = !!data;
    } catch (e) {
      this.wasLoaded = false;
    } finally {
      this.isLoading = false;
    }
  }

  protected get jupyterHubUrl() {
    return `${JUPYTERHUB_DOMAIN}/hub/spawn?next=/user-redirect/nbfetch/hs-pull?id=${this.data["repository_identifier"]}&app=lab`;
  }

  protected get schema() {
    return User.$state.schema;
  }

  protected get uiSchema() {
    return User.$state.uiSchema;
  }
}
</script>

<style lang="scss" scoped></style>
