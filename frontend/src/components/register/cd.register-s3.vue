<template>
  <div class="d-flex align-center">
    <v-badge color="primary" content="2" inline class="mr-2"></v-badge>
    <div>Where is the resource stored?</div>
  </div>

  <v-form>
    <v-text-field
      v-model.trim="state.path"
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

    <v-text-field
      v-model.trim="state.bucket"
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

    <v-text-field
      v-model.trim="state.endpointUrl"
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

  <div class="text-right">
    <v-btn color="primary" :disabled="form.$invalid"> Continue </v-btn>
  </div>
</template>

<script lang="ts">
import { Component, Vue, toNative } from "vue-facing-decorator";

import { useVuelidate } from "@vuelidate/core";
import { url, required, helpers } from "@vuelidate/validators";

const rules = {
  path: { required: helpers.withMessage("required", required) },
  bucket: { required: helpers.withMessage("required", required) },
  endpointUrl: {
    required: helpers.withMessage("required", required),
    url: helpers.withMessage("not a valid URL address", url),
  },
};

@Component({
  name: "cd-register-s3",
  components: {},
})
class CdRegisterS3 extends Vue {
  state = {
    path: "",
    bucket: "",
    endpointUrl: "",
  };

  form: any = null;

  isRequired(value: string): true | string {
    if (!value.trim().length) {
      return "required";
    }

    return true;
  }

  created() {
    this.form = useVuelidate(rules, this.state);
  }
}
export default toNative(CdRegisterS3);
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
