<template>
  <v-container class="cd-contact d-flex full-height pa-0">
    <div
      id="panel-left"
      class="flex-grow-1 hidden-sm-and-down"
      :style="{
        'background-image':
          'linear-gradient(rgb(0 52 82 / 31%), rgba(0, 0, 0, 0)), url(' +
          '@/img/bg1.jpg' +
          ')',
      }"
    ></div>
    <v-container id="panel-right" class="pa-8">
      <div class="text-h4">How to Contact Us</div>
      <v-divider class="mb-3" />

      <p class="text-subtitle-1">
        If you need help with data management or have questions about the
        guidance provided here, you can contact us in a number of ways.
      </p>

      <div class="text-h6 mb-3 mt-6">Join Us in the CZNet Slack Workspace</div>

      <p class="text-body-1">
        The CZNet Slack workspace was established to foster communication
        between the thematic clusters and with the CZNet Hub team. If you
        haven’t joined the CZNet Slack workspace, we encourage you to join us
        there. There are specific channels set up within the workspace for
        topical discussions. If you would like to join the CZNet Slack
        workspace, please email us at
        <a href="mailto:help@cuahsi.org">help@cuahsi.org</a>.
      </p>

      <div class="text-h6 mb-3 mt-6">Contact Us Directly via Email</div>

      <p class="text-body-1">
        For specific questions about CZNet data management, please contact us at
        <a href="mailto:help@cuahsi.org?subject=(CZNet)">help@cuahsi.org</a>. Be
        sure to include “CZNet” in the subject line of the email you send. We
        will route these emails to the person(s) who we think can best answer
        your questions.
      </p>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, toNative } from "vue-facing-decorator";

@Component({
  name: "cd-contact",
  components: {},
})
class CdContact extends Vue {}
export default toNative(CdContact);
</script>

<style lang="scss" scoped>
#panel-left {
  padding-top: 8rem;
  background-size: cover;
  flex: 3;
}

#panel-right {
  flex: 1;
  flex-direction: column;
}
</style>
