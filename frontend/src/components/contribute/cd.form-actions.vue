<template>
  <div
    class="d-flex form-controls flex-column flex-sm-row flex-grow-1 flex-sm-grow-0 gap-1"
  >
    <v-spacer></v-spacer>
    <v-btn @click="$emit('cancel')">Cancel</v-btn>

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
              :color="canConfirm ? 'primary' : 'default'"
              block
              depressed
              @click="$emit('confirm')"
              :disabled="!canConfirm"
              >{{ confirmText }}</v-btn
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
</template>

<script lang="ts">
import { Component, Vue, toNative, Prop } from "vue-facing-decorator";
import { CzForm } from "@cznethub/cznet-vue-core";

@Component({
  name: "cd-form-actions",
  components: { CzForm },
  emits: ["save", "cancel"],
})
class CdFormActions extends Vue {
  @Prop({ default: true }) canConfirm!: boolean;
  @Prop({ default: "Save" }) confirmText!: boolean;
  @Prop({ default: () => [] }) errors!: { title: string; message: string }[];

  get isValid() {
    return !this.errors.length;
  }
}
export default toNative(CdFormActions);
</script>

<style lang="scss" scoped></style>
