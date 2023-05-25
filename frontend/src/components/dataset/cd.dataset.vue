<template>
  <v-container class="cd-contribute">
    <div class="display-1">Dataset</div>
    <v-divider class="my-4"></v-divider>
    <cz-form
      v-if="!isLoading"
      :schema="schema"
      :uischema="uiSchema"
      :isReadOnly="true"
    />
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

  created() {
    this.loadDataset();
  }

  protected async loadDataset() {
    const id = this.$route.params.id;
    console.log(id);
    this.data = await User.fetchDataset(id);
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
