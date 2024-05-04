<template>
  <v-container class="cd-contribute">
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

    <div class="d-flex justify-end">
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
                >Register</v-btn
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
import { Component, Vue, toNative, Hook, Prop } from "vue-facing-decorator";
import { CzForm } from "@cznethub/cznet-vue-core";
import { hasUnsavedChangesGuard } from "@/guards";
import {
  NavigationGuardNext,
  RouteLocationNormalized,
  useRouter,
} from "vue-router";
import User from "@/models/user.model";

const initialData = {};

@Component({
  name: "cd-register-s3-form",
  components: { CzForm },
})
class CdRegisterS3Form extends Vue {
  @Prop() isSaving!: boolean;
  isValid = false;
  isLoading = true;
  wasLoaded = false;
  submissionId = "";
  errors: { title: string; message: string }[] = [];
  data = initialData;
  timesChanged = 0;
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
  }

  async submit() {
    this.$emit("save", this.data);
    // this.isSaving = true;
    // this.onCreateSubmission();
  }

  onUpdateErrors(errors: { title: string; message: string }[]) {
    this.errors = errors;
  }

  onCancel() {
    this.router.push({ name: "submissions" });
  }

  onDataChange(_data: any) {
    // cz-form emits 'change' event multiple times during instantioation.
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
export default toNative(CdRegisterS3Form);
</script>

<style lang="scss" scoped></style>
