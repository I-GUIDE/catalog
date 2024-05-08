<template>
  <v-form>
    <v-text-field
      v-model.trim="modelValue.path"
      :error-messages="form.path.$errors.map((e) => e.$message)"
      @blur="form.path.$touch"
      @input="form.path.$touch"
      clearable
      class="my-4"
      label="Path*"
      hide-details="auto"
      persistent-hint
      variant="outlined"
    >
    </v-text-field>

    <div
      class="text-subtitle-1 text-medium-emphasis pl-3 mb-4 mt-1"
      style="word-break: break-word"
    >
      {{ `e.g. 'data/.hs/dataset_metadata.json'` }}
    </div>

    <v-text-field
      v-model.trim="modelValue.bucket"
      :error-messages="form.bucket.$errors.map((e) => e.$message)"
      @blur="form.bucket.$touch"
      @input="form.bucket.$touch"
      clearable
      class="my-4"
      label="Bucket*"
      type="url"
      hide-details="auto"
      persistent-hint
      variant="outlined"
    >
    </v-text-field>

    <div
      class="text-subtitle-1 text-medium-emphasis pl-3 mb-4 mt-1"
      style="word-break: break-word"
    >
      {{ `e.g. 'iguide-catalog'` }}
    </div>

    <v-text-field
      v-model.trim="modelValue.endpointUrl"
      :error-messages="form.endpointUrl.$errors.map((e) => e.$message)"
      @blur="form.endpointUrl.$touch"
      @input="form.endpointUrl.$touch"
      clearable
      class="my-4"
      label="Endpoint URL*"
      type="url"
      hide-details="auto"
      persistent-hint
      variant="outlined"
    >
    </v-text-field>

    <div
      class="text-subtitle-1 text-medium-emphasis pl-3 mb-4 mt-1"
      style="word-break: break-word"
    >
      {{ `e.g. 'https://iguide-catalog.s3.us-west-2.amazonaws.com/'` }}
    </div>
  </v-form>
</template>

<script lang="ts">
import { Component, Prop, Vue, toNative } from "vue-facing-decorator";
import { useVuelidate } from "@vuelidate/core";
import { url, required, helpers } from "@vuelidate/validators";
import { useRouter } from "vue-router";

@Component({
  name: "cd-register-s3-bucket",
  components: {},
})
class CdRegisterS3Bucket extends Vue {
  @Prop() modelValue!: { path: string; bucket: string; endpointUrl: string };

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
      this.modelValue,
    );
    this.form.$validate();
  }
}
export default toNative(CdRegisterS3Bucket);
</script>

<style lang="scss" scoped></style>
