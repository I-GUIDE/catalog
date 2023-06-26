<template>
  <v-container class="cd-contribute">
    <div class="display-1">Dataset</div>
    <v-divider class="my-4"></v-divider>
    <template v-if="!isLoading && wasLoaded">
      <cz-form
        v-if="!isLoading"
        :schema="schema"
        :uischema="uiSchema"
        :data="data"
        :config="config"
      />
    </template>
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
import { Notifications, CzForm } from "@cznethub/cznet-vue-core";

import User from "@/models/user.model";

@Component({
  name: "cd-contribute",
  components: { CzForm },
})
export default class CdDataset extends Vue {
  protected data = {};
  protected isLoading = true;
  protected wasLoaded = false;

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
        filled: true,
      },
    },
    isViewMode: true,
  };

  created() {
    this.loadDataset();
  }

  protected async loadDataset() {
    const id = this.$route.params.id;
    const data = await User.fetchDataset(id);
    if (data) {
      this.data = data;
    }
    this.wasLoaded = !!data;
    this.isLoading = false;
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
