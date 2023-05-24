<template>
  <v-card class="cz-login">
    <v-card-title>Log In</v-card-title>
    <v-card-text>Please log in to access the contribution form</v-card-text>
    <v-divider></v-divider>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn @click="onCancel">Cancel</v-btn>
      <v-btn
        id="orcid_login_continue"
        @click="openLogInDialog()"
        color="primary"
      >
        <span>Log In</span>
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import User from "@/models/user.model";

@Component({
  name: "cz-login",
  components: {},
})
export default class CzLogin extends Vue {
  protected async openLogInDialog() {
    User.logIn(this.onLoggedIn);
  }

  protected onCancel() {
    this.$emit("cancel");
  }

  protected onLoggedIn() {
    this.$emit("logged-in");
  }
}
</script>

<style lang="scss" scoped>
::v-deep .v-card__text img {
  max-width: 12rem;
}
</style>
