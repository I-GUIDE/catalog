<template>
  <v-container class="cd-register-dataset">
    <div class="text-h4">Register Dataset</div>
    <v-divider class="mb-4" />

    <v-alert border="left" colored-border type="info" elevation="1">
      <div class="d-flex justify-space-between flex-sm-row flex-column">
        <div>
          Use this form to register existing datasets from
          <a href="https://www.hydroshare.org/">HydroShare</a>.
        </div>
        <v-img
          max-width="200"
          contain
          :src="require('@/assets/img/hydroshare.png')"
        ></v-img>
      </div>
    </v-alert>

    <div class="mt-8">What is the URL to or identifier for the resource?</div>

    <v-form
      ref="form"
      v-model="isValid"
      lazy-validation
      class="pb-2"
      @submit.prevent
    >
      <v-text-field
        v-model.trim="url"
        ref="txtIdentifier"
        :disabled="isFetching"
        :required="true"
        :rules="[isValidUrlOrIdentifier()]"
        clearable
        class="my-4"
        label="URL or identifier*"
        type="url"
        hide-details="auto"
        persistent-hint
        outlined
        @keypress.enter="onReadDataset"
      >
      </v-text-field>

      <div
        class="text-subtitle-1 text--secondary pl-3 mb-4 mt-1"
        style="word-break: break-word"
      >
        {{ `e.g. '${exampleUrl}' or '${exampleIdentifier}'` }}
      </div>
    </v-form>

    <v-btn
      color="primary"
      class="mr-4"
      @click="onReadDataset"
      :disabled="!canReadDataset"
    >
      Register
    </v-btn>

    <v-card v-if="isFetching" elevation="2" outlined class="my-8">
      <div class="table-item">
        <table
          class="text-body-1"
          :class="{ 'is-xs-small': $vuetify.breakpoint.xs }"
        >
          <tr>
            <td colspan="2" class="text-h6 title">
              <v-skeleton-loader type="heading" />
            </td>
          </tr>
        </table>
      </div>

      <div
        class="table-item d-flex justify-space-between flex-column flex-md-row gap-1"
      >
        <table
          class="text-body-1"
          :class="{ 'is-xs-small': $vuetify.breakpoint.xs }"
        >
          <tr>
            <th class="pr-4 body-2 text-right">
              <v-skeleton-loader type="text" />
            </th>
            <td><v-skeleton-loader type="text" /></td>
          </tr>
          <tr>
            <th class="pr-4 body-2 text-right">
              <v-skeleton-loader type="text" />
            </th>
            <td><v-skeleton-loader type="text" /></td>
          </tr>
          <tr>
            <th class="pr-4 body-2 text-right">
              <v-skeleton-loader type="text" />
            </th>
            <td><v-skeleton-loader type="text" /></td>
          </tr>
        </table>

        <div class="text-right d-flex">
          <v-skeleton-loader type="heading" width="450" />
        </div>
      </div>
    </v-card>

    <template v-else-if="submission">
      <div class="d-flex align-center mt-8 mb-4">
        <v-icon
          class="mr-2"
          color="green darken-2"
          aria-label="Check"
          role="img"
          aria-hidden="false"
        >
          mdi-check-circle
        </v-icon>
        <div class="text-h6 text--secondary">
          Your dataset has been registered:
        </div>
      </div>
      <v-card elevation="2" outlined class="mb-8">
        <v-card-title>{{ submission.title }}</v-card-title>
        <v-divider></v-divider>
        <div
          class="table-item d-flex justify-space-between flex-column flex-md-row"
        >
          <table
            class="text-body-1"
            :class="{ 'is-xs-small': $vuetify.breakpoint.xs }"
          >
            <tr v-if="submission.authors && submission.authors.length">
              <th class="pr-4 body-2">Authors:</th>
              <td>{{ submission.authors.join(" | ") }}</td>
            </tr>
            <tr>
              <th class="pr-4 body-2">Submission Date:</th>
              <td>{{ getDateInLocalTime(submission.date) }}</td>
            </tr>
            <!-- <tr>
              <th class="pr-4 body-2">Identifier:</th>
              <td>{{ submission.identifier }}</td>
            </tr> -->
          </table>
        </div>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn v-if="submission.url" :href="submission.url" target="_blank">
            <v-icon class="mr-1">mdi-open-in-new</v-icon> View In Repository
          </v-btn>
          <v-btn class="mr-4" @click="goToViewDataset">
            View landing page
          </v-btn>
        </v-card-actions>
      </v-card>
    </template>

    <template v-else-if="!submission && wasNotFound">
      <v-alert
        class="text-subtitle-1 ma-2 mt-8"
        border="left"
        colored-border
        type="warning"
        elevation="2"
        icon="mdi-magnify-remove-outline"
      >
        We could not find a resource matching the criteria above. Please make
        sure that the URL or identifier is correct and try again.
      </v-alert>
    </template>
    <template v-else-if="!submission && isDuplicate">
      <v-alert
        class="text-subtitle-1 ma-2 mt-8"
        border="left"
        colored-border
        type="warning"
        elevation="2"
        icon="mdi-content-duplicate"
      >
        The resource provided has already been registered.
      </v-alert>
    </template>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import Submission from "@/models/submission.model";
const exampleUrl =
  "https://www.hydroshare.org/resource/9d3d437466764bb5b6668d2742cf9db2/";
const exampleIdentifier = "9d3d437466764bb5b6668d2742cf9db2";
const identifierUrlPattern = new RegExp(
  `(?:http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?(?:hydroshare.org\/resource\/)([0-9a-fA-F]{32})\/?$`
);
const identifierPattern = new RegExp(`^[0-9a-fA-F]{32}$`);

@Component({
  name: "cd-register-dataset",
  components: {},
})
export default class CzRegisterDataset extends Vue {
  protected url = "";
  protected isFetching = false;
  protected isValid = false;
  protected submission: Partial<Submission> | null = null;
  protected wasUnauthorized = false;
  protected wasNotFound = false;
  protected isDuplicate = false;
  protected isRegistering = false;
  protected exampleIdentifier = exampleIdentifier;
  protected exampleUrl = exampleUrl;

  protected get canReadDataset(): boolean {
    return !this.isFetching && this.isValid && !!this.url;
  }

  protected get identifierFromUrl(): string {
    if (identifierPattern?.test(this.url)) {
      return this.url;
    } else if (identifierUrlPattern?.test(this.url)) {
      const matches = identifierUrlPattern?.exec(this.url);

      if (matches && matches.length) {
        return matches[1];
      }
    }

    return this.url; // default
  }

  mounted() {
    // @ts-ignore
    this.$refs.txtIdentifier?.focus();
  }

  protected onReadDataset() {
    if (this.canReadDataset) {
      this._readDataset();
    }
  }

  protected goToViewDataset() {
    if (this.submission?.id) {
      this.$router.push({
        name: "dataset",
        params: {
          id: this.submission.id,
        },
      });
    }
  }

  protected getDateInLocalTime(date: number): string {
    const offset = new Date(date).getTimezoneOffset() * 60 * 1000;
    const localDateTime = date + offset;
    return new Date(localDateTime).toLocaleString();
  }

  protected isValidUrlOrIdentifier(): true | string {
    if (!this.url) {
      return "required";
    }

    return identifierPattern?.test(this.url) ||
      identifierUrlPattern?.test(this.url)
      ? true
      : "invalid URL or Identifier";
  }

  private async _readDataset() {
    this.submission = null;
    this.isFetching = true;
    this.wasUnauthorized = false;
    this.wasNotFound = false;
    this.isDuplicate = false;

    try {
      const response = await Submission.registerSubmission(
        this.identifierFromUrl
      );

      if (response && typeof response !== "number") {
        this.submission = response;
      } else {
        if (response === 400) {
          // Resource has already been submitted
          this.isDuplicate = true;
        } else {
          this.wasNotFound = true;
        }
      }
    } catch (e) {
      this.wasNotFound = true;
    } finally {
      this.isFetching = false;
    }
  }
}
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
