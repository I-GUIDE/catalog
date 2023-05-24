<template>
  <v-container class="cd-contribute">
    <submission-form
      :schema="schema"
      :uischema="uischema"
      :schemaDefaults="schemaDefaults"
    />
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { Notifications, SubmissionForm } from "@cznethub/cznet-vue-core";

const schema = require("@/schemas/schema.json");
const uischema = require("@/schemas/uischema.json");
const schemaDefaults = require("@/schemas/uischema.json");

@Component({
  name: "cd-contribute",
  components: { SubmissionForm },
})
export default class CdContribute extends Vue {
  protected schema;
  protected uischema;
  protected schemaDefaults;

  beforeCreate() {
    this.schema = schema;
    this.uischema = uischema;
    this.schemaDefaults = schemaDefaults;
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
