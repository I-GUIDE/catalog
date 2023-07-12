<template>
  <v-container class="cd-contribute">
    <div class="display-1">Contribute</div>

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

    <div
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
                >Save</v-btn
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
  }

  protected async submit() {
    try {
      this.isSaving = true;
      const savedDatasetId = await User.submit(this.data);
      this.isSaving = false;
      if (savedDatasetId) {
        this.hasUnsavedChanges = false;
        Notifications.toast({
          message: `Your submission has been saved!`,
          type: "success",
        });
        this.$router.push({ name: "dataset", params: { id: savedDatasetId } });
      } else {
        // Failed to save
        Notifications.toast({
          message: `Failed to save submission`,
          type: "error",
        });
      }
    } catch (e) {
      this.isSaving = false;
    }
  }

  protected onCancel() {
    this.$router.push({ name: "home" });
  }

  protected onDataChange(data) {
    // cz-form emits 'change' event 2 times during instantioation.
    const changesDuringInstantiation = 2;

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
