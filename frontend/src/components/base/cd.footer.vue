<template>
  <v-container
    flat
    class="footer d-flex flex-column align-center full-width text-body-2 font-weight-light"
  >
    <div class="d-lg-flex justify-space-between full-width">
      <div class="mb-4">
        <div class="mb-4 text-h6 mb-1 text-medium-emphasis">Contact Us</div>
        <!-- <p><router-link to="/contact">Contact</router-link></p> -->
        <!-- <p>
          <a :href="'mailto:' + $t('footer.supportEmail')">Email Support</a>
        </p> -->
        <p>
          Learn more about
          <a href="https://i-guide.io/" target="_blank">I-GUIDE</a>
        </p>
        <p>
          Visit
          <a href="https://i-guide.io/" target="_blank">i-guide.org</a>
        </p>
      </div>

      <div>
        <div class="mb-4 text-h6 text-medium-emphasis">Open Source</div>
        <p>
          The I-GUIDE Catalog and Discover system are Open Source. Find us on
          <a href="https://github.com/I-GUIDE/catalog" target="_blank">GitHub</a
          >.
        </p>
        <p>
          Report a bug
          <a href="https://github.com/I-GUIDE/catalog/issues" target="_blank"
            >here</a
          >
        </p>
        <p>This is Version {{ version }} of the I-GUIDE catalog</p>
      </div>
    </div>

    <v-divider></v-divider>

    <div class="text-center d-flex flex-column align-center mt-4">
      <p>
        © {{ year }} I-GUIDE Developers. This material is based upon work
        supported by the National Science Foundation (NSF) under award 2118329.
        Any opinions, findings, conclusions, or recommendations expressed in
        this material are those of the authors and do not necessarily reflect
        the views of the NSF.
      </p>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, toNative } from "vue-facing-decorator";

@Component({
  name: "cd-footer",
  components: {},
})
class CdFooter extends Vue {
  get version() {
    return APP_VERSION;
  }

  get year() {
    return new Date().getFullYear();
  }
}
export default toNative(CdFooter);
</script>

<style lang="scss" scoped>
.footer {
  padding: 2rem 0;
}

p {
  margin-bottom: 1rem;
}
</style>
