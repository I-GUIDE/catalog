<template>
  <div class="d-flex align-center mb-4">
    <v-badge color="primary" content="2" inline class="mr-2"></v-badge>
    <div>Where is the resource stored?</div>
  </div>

  <cd-register-s3-bucket v-model="s3State" />

  <div class="d-flex align-center mt-12">
    <v-badge color="primary" content="3" inline class="mr-2"></v-badge>
    <div>Describe your resource</div>
  </div>
  <CdRegisterS3Form :isSaving="isSaving || form.$invalid" @save="onSave" />
</template>

<script lang="ts">
import { Component, Vue, toNative } from "vue-facing-decorator";
import { useVuelidate } from "@vuelidate/core";
import { url, required, helpers } from "@vuelidate/validators";
import CdRegisterS3Form from "@/components/register/cd.register-s3-form.vue";
import User from "@/models/user.model";
import { Notifications } from "@cznethub/cznet-vue-core";
import { useRouter } from "vue-router";
import CdRegisterS3Bucket from "./cd.register-s3-bucket.vue";

@Component({
  name: "cd-register-s3",
  components: { CdRegisterS3Form, CdRegisterS3Bucket },
})
class CdRegisterS3 extends Vue {
  s3State = {
    path: "",
    bucket: "",
    endpointUrl: "",
  };

  form: any = null;
  isSaving = false;
  router = useRouter();

  created() {
    this.form = useVuelidate(
      {
        path: { required: helpers.withMessage("required", required) },
        bucket: { required: helpers.withMessage("required", required) },
        endpointUrl: {
          required: helpers.withMessage("required", required),
          url: helpers.withMessage("not a valid URL address", url),
        },
      },
      this.s3State,
    );
    this.form.$validate();
  }

  async onSave(data: any) {
    try {
      this.isSaving = true;
      const savedDatasetId = await User.submitS3(data, this.s3State);
      this.isSaving = false;

      if (savedDatasetId) {
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
}
export default toNative(CdRegisterS3);
</script>

<style lang="scss" scoped></style>
