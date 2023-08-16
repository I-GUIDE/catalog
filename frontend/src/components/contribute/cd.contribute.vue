<template>
  <v-container class="cd-contribute">
    <div class="display-1">
      {{ isEditMode ? "Edit Submission" : "Contribute" }}
    </div>

    <template v-if="!isEditMode || (!isLoading && wasLoaded)">
      <cz-form
        :schema="schema"
        :uischema="uiSchema"
        :errors.sync="errors"
        :isValid.sync="isValid"
        :data.sync="data"
        :config="config"
        @update:data="onDataChange"
        ref="form"
      />
    </template>

    <div v-else-if="isLoading" class="text-h6 text--secondary my-12">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div
      v-if="!(isEditMode && (isLoading || !wasLoaded))"
      class="d-flex form-controls flex-column flex-sm-row flex-grow-1 flex-sm-grow-0 gap-1"
    >
      <v-spacer></v-spacer>
      <v-btn @click="onCancel">Cancel</v-btn>

      <v-menu :disabled="isValid" open-on-hover bottom left offset-y>
        <template v-slot:activator="{ on, attrs }">
          <div
            v-bind="attrs"
            v-on="on"
            class="d-flex form-controls flex-column flex-sm-row"
          >
            <v-badge
              :value="!!errors.length"
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

        <div class="white pa-4">
          <ul
            v-for="(error, index) of errors"
            :key="index"
            class="text-subtitle-1"
          >
            <li>
              <b>{{ error.title }}</b> {{ error.message }}.
            </li>
          </ul>
        </div>
      </v-menu>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { Notifications, CzForm } from "@cznethub/cznet-vue-core";

import User from "@/models/user.model";

const initialData = {};

@Component({
  name: "cd-contribute",
  components: { CzForm },
})
export default class CdContribute extends Vue {
  protected isValid = false;
  protected isEditMode = false;
  protected isLoading = true;
  protected wasLoaded = false;
  protected submissionId = "";
  protected errors = [];
  protected data = initialData;
  protected timesChanged = 0;
  protected isSaving = false;
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
  };

  protected get schema() {
    return User.$state.schema;
  }

  protected get uiSchema() {
    return User.$state.uiSchema;
  }

  // protected get schemaDefaults() {
  //   return User.$state.schemaDefaults;
  // }

  protected get hasUnsavedChanges(): boolean {
    return User.$state.hasUnsavedChanges;
  }

  protected set hasUnsavedChanges(value: boolean) {
    User.commit((state) => {
      state.hasUnsavedChanges = value;
    });
  }

  created() {
    this.hasUnsavedChanges = false;
    if (this.$route.name === "dataset-edit") {
      this.isEditMode = true;
      this.submissionId = this.$route.params.id;
      this.loadDataset();
    }
  }

  protected async loadDataset() {
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

  protected async onSaveChanges() {
    try {
      const wasSaved = await User.updateDataset(this.submissionId, this.data);
      if (wasSaved) {
        Notifications.toast({
          message: `Your changes habe been saved!`,
          type: "success",
        });
        this.hasUnsavedChanges = false;
        this.$router.push({
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

  protected async onCreateSubmission() {
    try {
      const savedDatasetId = await User.submit(this.data);
      this.isSaving = false;
      if (savedDatasetId) {
        this.hasUnsavedChanges = false;
        Notifications.toast({
          message: `Your submission has been saved!`,
          type: "success",
        });
        this.$router.push({
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

  protected async submit() {
    this.isSaving = true;

    if (this.isEditMode) {
      this.onSaveChanges();
    } else {
      this.onCreateSubmission();
    }
  }

  protected onCancel() {
    if (this.isEditMode) {
      this.$router.push({
        name: "dataset",
        params: { id: this.submissionId },
      });
    } else {
      this.$router.push({ name: "submissions" });
    }
  }

  protected onDataChange(data) {
    // cz-form emits 'change' event multiple times during instantioation.
    const changesDuringInstantiation = this.isEditMode ? 2 : 3;

    if (this.timesChanged <= changesDuringInstantiation) {
      this.timesChanged = this.timesChanged + 1;
    }

    this.hasUnsavedChanges = this.timesChanged > changesDuringInstantiation;
  }

  // mounted() {
  //   Notifications.toast({
  //     message: `Failed to perform search`,
  //     type: "error",
  //   });

  //   Notifications.openDialog({
  //     title: "some title",
  //     content: "some content",
  //     onConfirm: () => {},
  //   });
  // }
}
</script>

<style lang="scss" scoped></style>
