<template>
  <v-container class="cd-contribute">
    <div class="display-1 d-sm-flex d-block justify-space-between align-center">
      <div class="text-h4">
        {{ isEditMode ? "Edit Submission" : "Contribute" }}
      </div>

      <div
        v-if="!(isEditMode && (isLoading || !wasLoaded))"
        class="d-flex form-controls flex-column flex-sm-row flex-grow-1 flex-sm-grow-0 gap-1"
      >
        <v-spacer></v-spacer>
        <v-btn @click="onCancel">Cancel</v-btn>

        <v-menu :disabled="isValid" open-on-hover bottom left offset-y>
          <template #activator="{ props }">
            <div
              v-bind="props"
              class="d-flex form-controls flex-column flex-sm-row"
            >
              <v-badge
                :model-value="!isValid"
                bordered
                color="error"
                icon="mdi-exclamation-thick"
                overlap
              >
                <v-btn
                  color="primary"
                  block
                  depressed
                  @click="submit"
                  :disabled="isSaving || !isValid || !hasUnsavedChanges"
                  >{{ isEditMode ? "Save Changes" : "Save" }}</v-btn
                >
              </v-badge>
            </div>
          </template>

          <v-card class="bg-white">
            <v-card-text>
              <ul
                v-for="(error, index) of errors"
                :key="index"
                class="text-subtitle-1 ml-4"
              >
                <li>
                  <b>{{ error.title }}</b> {{ error.message }}.
                </li>
              </ul>
            </v-card-text>
          </v-card>
        </v-menu>
      </div>
    </div>

    <v-divider class="my-4" />

    <template v-if="!isEditMode || (!isLoading && wasLoaded)">
      <cz-form
        :schema="schema"
        :uischema="uiSchema"
        v-model:isValid="isValid"
        :errors.sync="errors"
        @update:errors="onUpdateErrors"
        @update:model-value="onDataChange"
        :config="config"
        v-model="data"
        ref="form"
      />
    </template>

    <div v-else-if="isLoading" class="text-h6 text-medium-emphasis my-12">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div
      v-if="!(isEditMode && (isLoading || !wasLoaded))"
      class="d-flex form-controls flex-column flex-sm-row flex-grow-1 flex-sm-grow-0 gap-1"
    >
      <v-spacer></v-spacer>
      <v-btn @click="onCancel">Cancel</v-btn>

      <v-menu :disabled="isValid" open-on-hover bottom left offset-y>
        <template #activator="{ props }">
          <div
            v-bind="props"
            class="d-flex form-controls flex-column flex-sm-row"
          >
            <v-badge
              :model-value="!isValid"
              bordered
              color="error"
              icon="mdi-exclamation-thick"
              overlap
            >
              <v-btn
                color="primary"
                block
                depressed
                @click="submit"
                :disabled="isSaving || !isValid || !hasUnsavedChanges"
                >{{ isEditMode ? "Save Changes" : "Save" }}</v-btn
              >
            </v-badge>
          </div>
        </template>

        <v-card class="bg-white">
          <v-card-text>
            <ul
              v-for="(error, index) of errors"
              :key="index"
              class="text-subtitle-1 ml-4"
            >
              <li>
                <b>{{ error.title }}</b> {{ error.message }}.
              </li>
            </ul>
          </v-card-text>
        </v-card>
      </v-menu>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, toNative, Hook } from "vue-facing-decorator";
import { Notifications, CzForm } from "@cznethub/cznet-vue-core";

import User from "@/models/user.model";
import { hasUnsavedChangesGuard } from "@/guards";
import {
  NavigationGuardNext,
  RouteLocationNormalized,
  useRoute,
  useRouter,
} from "vue-router";

const initialData = {};

@Component({
  name: "cd-contribute",
  components: { CzForm },
})
class CdContribute extends Vue {
  isValid = false;
  isEditMode = false;
  isLoading = true;
  wasLoaded = false;
  submissionId = "";
  errors: { title: string; message: string }[] = [];
  data = initialData;
  timesChanged = 0;
  isSaving = false;
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
        density: "compact",
        variant: "outlined",
        "persistent-hint": true,
        "hide-details": false,
      },
    },
  };

  route = useRoute();
  router = useRouter();

  get schema() {
    return User.$state.schema;
  }

  get uiSchema() {
    return User.$state.uiSchema;
  }

  // get schemaDefaults() {
  //   return User.$state.schemaDefaults;
  // }

  get hasUnsavedChanges(): boolean {
    return User.$state.hasUnsavedChanges;
  }

  set hasUnsavedChanges(value: boolean) {
    User.commit((state) => {
      state.hasUnsavedChanges = value;
    });
  }

  created() {
    this.hasUnsavedChanges = false;
    if (this.route.name === "dataset-edit") {
      this.isEditMode = true;
      this.submissionId = this.route.params.id as string;
      this.loadDataset();
    }
  }

  async loadDataset() {
    this.isLoading = true;
    try {
      const data = await User.fetchDataset(this.submissionId);
      this.wasLoaded = !!data;
      if (data) {
        this.data = data;
      }
    } catch (e) {
      this.wasLoaded = false;
    } finally {
      this.isLoading = false;
    }
  }

  async onSaveChanges() {
    try {
      const wasSaved = await User.updateDataset(this.submissionId, this.data);
      if (wasSaved) {
        Notifications.toast({
          message: `Your changes habe been saved!`,
          type: "success",
        });
        this.hasUnsavedChanges = false;
        this.router.push({
          name: "dataset",
          params: { id: this.submissionId },
        });
      }
    } catch (e) {
      Notifications.toast({
        message: `Failed to save changes`,
        type: "error",
      });
    } finally {
      this.isSaving = false;
    }
  }

  async onCreateSubmission() {
    try {
      const savedDatasetId = await User.submit(this.data);
      this.isSaving = false;
      if (savedDatasetId) {
        this.hasUnsavedChanges = false;
        Notifications.toast({
          message: `Your submission has been saved!`,
          type: "success",
        });
        this.router.push({
          name: "dataset",
          params: { id: savedDatasetId },
        });
      } else {
        // Failed to save
        Notifications.toast({
          message: `Failed to save submission`,
          type: "error",
        });
      }
    } finally {
      this.isSaving = false;
    }
  }

  async submit() {
    this.isSaving = true;

    if (this.isEditMode) {
      this.onSaveChanges();
    } else {
      this.onCreateSubmission();
    }
  }

  onUpdateErrors(errors: { title: string; message: string }[]) {
    this.errors = errors;
  }

  onCancel() {
    if (this.isEditMode) {
      this.router.push({
        name: "dataset",
        params: { id: this.submissionId },
      });
    } else {
      this.router.push({ name: "submissions" });
    }
  }

  onDataChange(_data: any) {
    // cz-form emits 'update:model-value' event multiple times during instantioation.
    const changesDuringInstantiation = 3;
    if (this.timesChanged <= changesDuringInstantiation) {
      this.timesChanged = this.timesChanged + 1;
    }

    this.hasUnsavedChanges = this.timesChanged > changesDuringInstantiation;
  }

  @Hook
  beforeRouteLeave(
    to: RouteLocationNormalized,
    from: RouteLocationNormalized,
    next: NavigationGuardNext,
  ) {
    hasUnsavedChangesGuard(to, from, next);
  }
}
export default toNative(CdContribute);
</script>

<style lang="scss" scoped></style>
