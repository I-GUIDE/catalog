<template>
  <v-container class="cd-contribute">
    <div class="display-1 d-sm-flex d-block justify-space-between align-center">
      <div class="text-h4">
        {{ isEditMode ? "Edit Submission" : "Contribute" }}
      </div>

      <cd-form-actions
        v-if="!isLoading && wasLoaded"
        :canConfirm="
          !isSaving && isValid && hasUnsavedChanges && !(isS3 && !isS3Valid)
        "
        :confirmText="isEditMode ? 'Save Changes' : 'Save'"
        :errors="errors"
        @confirm="submit"
        @cancel="onCancel"
      />
    </div>

    <v-divider class="my-4" />

    <v-row v-if="!isLoading && wasLoaded">
      <v-col cols="12" order="2" order-lg="1" :lg="isS3 ? 8 : 12"
        ><cz-form
          :schema="schema"
          :uischema="uiSchema"
          v-model:isValid="isValid"
          :errors.sync="errors"
          @update:errors="onUpdateErrors"
          @update:model-value="onDataChange"
          :config="config"
          v-model="data"
          ref="form"
      /></v-col>
      <v-col v-if="isS3" cols="12" order="1" lg="4">
        <cd-register-s3-bucket
          v-model="s3State"
          @update:model-value=""
          :is-responsive="false"
          ref="s3Form"
          class="mt-4"
        />
      </v-col>
    </v-row>

    <div v-else-if="isLoading" class="text-h6 text-medium-emphasis my-12">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <cd-form-actions
      v-if="!isLoading && wasLoaded"
      :canConfirm="
        !isSaving && isValid && hasUnsavedChanges && !(isS3 && !isS3Valid)
      "
      :confirmText="isEditMode ? 'Save Changes' : 'Save'"
      :errors="errors"
      @confirm="submit"
      @cancel="onCancel"
    />
  </v-container>
</template>

<script lang="ts">
import {
  Component,
  Vue,
  toNative,
  Hook,
  Ref,
  Watch,
} from "vue-facing-decorator";
import { Notifications, CzForm } from "@cznethub/cznet-vue-core";
import CdFormActions from "./cd.form-actions.vue";
import User from "@/models/user.model";
import { hasUnsavedChangesGuard } from "@/guards";
import {
  NavigationGuardNext,
  RouteLocationNormalized,
  useRoute,
  useRouter,
} from "vue-router";
import CdRegisterS3Bucket from "@/components/register/cd.register-s3-bucket.vue";
const initialData = {};

@Component({
  name: "cd-contribute",
  components: { CzForm, CdFormActions, CdRegisterS3Bucket },
})
class CdContribute extends Vue {
  @Ref("s3Form") s3Form!: InstanceType<typeof CdRegisterS3Bucket>;
  isValid = false;
  isS3Valid = false;
  isEditMode = false;
  isLoading = true;
  wasLoaded = false;
  submissionId = "";
  errors: { title: string; message: string }[] = [];
  data: any = initialData;
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
  s3State = {
    path: "",
    bucket: "",
    endpointUrl: "",
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

  get isS3() {
    return this.data.submission_type === "S3";
  }

  set hasUnsavedChanges(value: boolean) {
    User.commit((state) => {
      state.hasUnsavedChanges = value;
    });
  }

  @Watch("s3State", { deep: true })
  onS3FormChange() {
    if (this.s3Form?.form) {
      this.hasUnsavedChanges = true;
      this.isS3Valid = !this.s3Form.form.$invalid;
    }
  }

  created() {
    this.hasUnsavedChanges = false;
    if (this.route.name === "dataset-edit") {
      this.isEditMode = true;
      this.submissionId = this.route.params.id as string;
      this.loadDataset();
    } else {
      this.isLoading = false;
      this.wasLoaded = true;
    }
  }

  async loadDataset() {
    this.isLoading = true;
    try {
      const data = await User.fetchDataset(this.submissionId);
      this.wasLoaded = !!data;
      if (data) {
        this.data = data;
        if (this.isS3) {
          this.s3State.bucket = data.s3_path.bucket;
          this.s3State.path = data.s3_path.path;
          this.s3State.endpointUrl = data.s3_path.endpoint_url;
        }
      }
    } catch (e) {
      this.wasLoaded = false;
    } finally {
      this.isLoading = false;
    }
  }

  async onSaveChanges() {
    try {
      const wasSaved = this.isS3
        ? await User.updateS3Dataset(this.submissionId, this.data, this.s3State)
        : await User.updateDataset(this.submissionId, this.data);
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
