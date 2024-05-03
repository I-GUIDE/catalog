<template>
  <v-container class="cd-register-dataset">
    <div class="text-h4">Register Dataset</div>
    <v-divider class="mb-4" />

    <v-alert
      border="start"
      type="info"
      variant="text"
      prominent
      density="compact"
      elevation="1"
    >
      <div
        class="d-flex justify-space-between align-center flex-sm-row flex-column text-body-1"
      >
        <div>
          Use this form to register existing datasets from
          <a href="https://www.hydroshare.org/">HydroShare</a> or
          <a href="https://aws.amazon.com/s3/">Amazon S3</a>.
        </div>
      </div>
    </v-alert>

    <div class="d-flex align-center mt-12">
      <v-badge color="primary" content="1" inline class="mr-2"></v-badge>
      <div>What repository is the resource in?</div>
    </div>

    <v-radio-group v-model="repository" class="mb-12">
      <v-radio label="HydroShare" value="HydroShare"></v-radio>
      <v-radio label="Amazon S3" value="AmazonS3"></v-radio>
    </v-radio-group>

    <template v-if="repository === 'HydroShare'">
      <CdRegisterHydroShare />
    </template>
    <CdRegisterS3 v-else />
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, toNative } from "vue-facing-decorator";
import CdRegisterHydroShare from "./cd.register-hydroshare.vue";
import CdRegisterS3 from "./cd.register-s3.vue";

@Component({
  name: "cd-register-dataset",
  components: { CdRegisterHydroShare, CdRegisterS3 },
})
class CdRegisterDataset extends Vue {
  repository: "HydroShare" | "AmazonS3" = "HydroShare";
}
export default toNative(CdRegisterDataset);
</script>

<style lang="scss" scoped>
.table-item {
  padding: 1rem;

  table {
    width: 100%;

    &.is-xs-small {
      tr,
      td,
      th {
        display: block;
        text-align: left;
      }

      th {
        padding-top: 1rem;
      }
    }

    th {
      text-align: right;
      width: 11rem;
      font-weight: normal;
    }

    td {
      word-break: break-word;
    }
  }
}
</style>
