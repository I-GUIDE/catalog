<template>
  <v-autocomplete
    :items="hints"
    @keydown.enter="onSearch"
    @click:clear="$emit('clear')"
    v-model:search="valueInternal"
    ref="searchInput"
    prepend-inner-icon="mdi-magnify"
    item-props
    item-title="key"
    item-value="key"
    rounded
    :placeholder="$t(`home.search.inputPlaceholder`)"
    variant="outlined"
    density="compact"
    clearable
    hide-no-data
    v-bind="inputAttrs"
  >
    <template #item="{ props, item }">
      <v-list-item
        v-bind="props"
        @pointerdown="onHintSelected($event, item.raw)"
        @keydown.enter="onHintSelected($event, item.raw)"
        density="compact"
      >
        <template #prepend>
          <v-icon size="x-small">{{
            item.raw.type === "local" ? "mdi-history" : "mdi-magnify"
          }}</v-icon>
        </template>
        <template #title>
          <v-list-item-title
            :class="{ 'text-accent': item.raw.type === 'local' }"
            class="font-weight-regular"
            >{{ item.raw.key }}</v-list-item-title
          >
        </template>
        <template #append>
          <v-list-item-action
            tabindex="-1"
            class="ma-0 pa-0"
            v-if="item.raw.type === 'local'"
          >
            <v-btn
              tabindex="-1"
              icon
              flat
              size="x-small"
              @click.stop="deleteHint(item.raw)"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-list-item-action>
        </template>
      </v-list-item>
    </template>
  </v-autocomplete>

  <!-- <v-menu offset-y v-model="menu">
    <template #activator="{ props }">
      <v-text-field
        class="cz-search"
        variant="solo"
        v-bind="{ ...props, ...inputAttrs }"
        ref="searchInput"
        @keydown.up="onDetectCrossover('up')"
        @keydown.down="onDetectCrossover('down')"
        @keyup.up="onHintHighlighted()"
        @keyup.down="onHintHighlighted()"
        @keydown.enter="onSearch"
        @click:clear="$emit('clear')"
        v-model.trim.lazy="valueInternal"
        prepend-inner-icon="mdi-magnify"
        :placeholder="$t(`home.search.inputPlaceholder`)"
        rounded
        full-width
        hide-details
        flat
        density="compact"
        clearable
      />
    </template>

    <v-progress-linear
      v-if="isFetchingHints"
      indeterminate
      absolute
      color="yellow darken-2"
    />

    <v-list>
      <v-list-item
        v-if="showList"
        v-for="(hint, index) of hints"
        ref="hintElements"
        :key="index"
        density="compact"
        @pointerdown="onHintSelected($event, hint)"
      >
        <template #prepend>
          <v-icon size="x-small">{{
            hint.type === "local" ? "mdi-history" : "mdi-magnify"
          }}</v-icon>
        </template>
        <template #title>
          <v-list-item-title
            :class="{ 'text-accent': hint.type === 'local' }"
            class="font-weight-regular"
            >{{ hint.key }}</v-list-item-title
          >
        </template>
        <template #append>
          <v-list-item-action class="ma-0 pa-0" v-if="hint.type === 'local'">
            <v-btn icon flat size="x-small" @click.stop="deleteHint(hint)">
              <v-icon ref="btnDeleteHint">mdi-close</v-icon>
            </v-btn>
          </v-list-item-action>
        </template>
      </v-list-item>
    </v-list>
  </v-menu> -->
</template>

<script lang="ts">
import {
  Component,
  Vue,
  Prop,
  Ref,
  Watch,
  toNative,
} from "vue-facing-decorator";
import { APP_NAME, sameRouteNavigationErrorHandler } from "@/constants";
import { fromEvent, from } from "rxjs";
import { debounceTime, map, switchMap, tap } from "rxjs/operators";
import SearchHistory from "@/models/search-history.model";
import Search from "@/models/search.model";
import type {
  VBtn,
  VListItem,
  VTextField,
} from "vuetify/lib/components/index.mjs";
import { IHint } from "@/types";

const typeaheadDebounceTime = 500;

@Component({
  name: "cd-search",
  components: {},
  emits: ["update:model-value", "clear"],
})
class CdSearch extends Vue {
  @Prop() modelValue!: string;
  @Prop({ default: () => ({}) }) inputAttrs: any;
  @Ref("searchInput") searchInput!: InstanceType<typeof VTextField>;

  appName = APP_NAME;

  public valueInternal = "";
  public previousValueInternal = "";
  public hints: IHint[] = []; // used to reactively bind to template
  public menu = false;
  public isFetchingHints = false;
  public showList = true;
  public detectCrossover = false;
  public rawDbHints: any[] = [];

  public get typeaheadHints(): IHint[] {
    if (!this.rawDbHints || !this.valueInternal) {
      return this.localHints;
    }

    return [...this.localHints, ...this.dbHints];
  }

  public get localHints(): IHint[] {
    return SearchHistory.searchHints(this.valueInternal);
  }

  public get dbHints(): IHint[] {
    const minCharacters = 3;
    const valueInternal = this.valueInternal.toLocaleLowerCase();
    let hints = this.rawDbHints
      .map((h) => h.highlights)
      .flat()
      .map((h) => h.texts)
      .flat()
      .filter(
        (t) =>
          t.type === "hit" &&
          t.value.length > minCharacters &&
          t.value.toLowerCase().indexOf(valueInternal) >= 0,
      )
      .map((t) => t.value.toLowerCase())
      .filter(
        (v: string) =>
          v !== valueInternal && !this.localHints.some((h) => h.key === v),
      );

    hints = [...new Set(hints)].slice(0, 10) as string[]; // get unique ones
    hints = hints.map((key) => ({ type: "db", key }) as IHint);
    return hints;
  }

  // Buetify doesn't handle well reasigning list items array
  @Watch("hints", { deep: true })
  public onHintsChanged() {
    // Reinstantiate component to reset state.
    this.showList = false;
    this.detectCrossover = false;
    this.$nextTick(() => {
      this.showList = true;
    });
  }

  @Watch("valueInternal")
  onValueInternalChanged() {
    if (!this.valueInternal) {
      this.hints = this.localHints;
    }
  }

  async mounted() {
    this.valueInternal = this.modelValue;
    this.previousValueInternal = this.modelValue;
    try {
      await this._onTypeahead();
    } catch (e) {}
    this.hints = this.typeaheadHints;
    this.searchInput?.focus();

    // https://www.learnrxjs.io/learn-rxjs/recipes/type-ahead
    fromEvent(this.searchInput?.$el, "input")
      .pipe(
        tap(() => {
          this.isFetchingHints = !!this.valueInternal;
          // Show hints from local history while the database ones load
          this.hints = this.localHints;
          this.menu = true;
        }),
        debounceTime(typeaheadDebounceTime),
        map((e: any) => e.target.value),
        switchMap(() => from(this._onTypeahead())),
      )
      .subscribe(() => {
        this._handleTypeahead(false);
      });
  }

  public onSearch() {
    this._onChange();
    this.previousValueInternal = this.valueInternal;
    if (this.valueInternal && this.$route?.name !== "search") {
      this.$router
        .push({ name: "search", query: { q: this.valueInternal } })
        .catch(sameRouteNavigationErrorHandler);
    }
    this.menu = false;
  }

  public async onHintSelected(event: PointerEvent, hint: IHint) {
    // We only act on 'pointerdown' event. The enter key is already captured in the input.
    // The value is already populated by onHintHighlighted.

    // Ignore clicks on the action buttons
    // if (
    //   this.btnDeleteHint &&
    //   this.btnDeleteHint.map((btn) => btn.$el).includes(event.target)
    // ) {
    //   return;
    // }

    // if (event.type === "pointerdown") {
    this.valueInternal = hint.key;
    this.isFetchingHints = !!this.valueInternal;
    this.onSearch();
    // await this._onTypeahead();
    // this._handleTypeahead(false);
    // }
  }

  public deleteHint(hint: IHint) {
    SearchHistory.deleteHint(hint.key);
    this.hints = this.typeaheadHints;
  }

  async _onTypeahead() {
    if (!this.valueInternal?.trim?.()) {
      this.isFetchingHints = false;
      this.hints = this.typeaheadHints;
      return;
    }

    try {
      this.previousValueInternal = this.valueInternal;
      this.rawDbHints = await Search.typeahead({ term: this.valueInternal });
      this.isFetchingHints = false;
    } catch (e) {
      console.log(e);
    }
  }

  _handleTypeahead(bringUpHintsMenu = true) {
    this.hints = this.typeaheadHints;
    if (this.valueInternal) {
      this.menu = bringUpHintsMenu || this.menu;
      this.isFetchingHints = false;
    }
  }

  _onChange() {
    this.$emit("update:model-value", this.valueInternal);
  }
}
export default toNative(CdSearch);
</script>

<style lang="scss" scoped>
.cd-home-search {
  background: #ddd;
}

.search-container {
  max-width: 45rem;
}
</style>
