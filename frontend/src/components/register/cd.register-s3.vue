<template>
  <div class="d-flex align-center mb-4">
    <v-badge color="primary" content="2" inline class="mr-2"></v-badge>
    <div>Where is the resource stored?</div>
  </div>

  <cd-register-s3-bucket v-model="s3State" ref="s3Form" />

  <div class="d-flex align-center mt-16">
    <v-badge color="primary" content="3" inline class="mr-2"></v-badge>
    <div>Describe your resource</div>
  </div>
  <CdRegisterS3Form :isSaving="isSaving || !isS3Valid" @save="onSave" />
</template>

<script lang="ts">
import { Component, Ref, Vue, Watch, toNative } from "vue-facing-decorator";
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
  @Ref("s3Form") s3Form!: InstanceType<typeof CdRegisterS3Bucket>;
  s3State = {
    path: "",
    bucket: "",
    endpointUrl: "",
  };
  isS3Valid = false;
  isSaving = false;
  router = useRouter();

  @Watch("s3State", { deep: true })
  onS3FormChange() {
    if (this.s3Form?.form) {
      this.isS3Valid = !this.s3Form.form.$invalid;
    }
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
