<template>
  <v-combobox
    :items="hints"
    @keydown.enter="onSearch"
    @click:clear="$emit('clear')"
    @click="menu = true"
    v-model="valueInternal"
    v-model:menu="menu"
    ref="searchInput"
    prepend-inner-icon="mdi-magnify"
    item-props
    item-title="key"
    item-value="key"
    rounded
    :placeholder="$t(`home.search.inputPlaceholder`)"
    density="compact"
    clearable
    :loading="isFetchingHints"
    hide-no-data
    variant="solo"
    v-bind="inputAttrs"
    no-filter
  >
    <template #item="{ props, item }">
      <v-list-item
        v-bind="props"
        density="compact"
        @pointerdown="onHintSelected($event, item.raw)"
        @keydown.enter="onHintSelected($event, item.raw)"
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
              variant="elevated"
              size="x-small"
              @click.stop="deleteHint(item.raw)"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-list-item-action>
        </template>
      </v-list-item>
    </template>
  </v-combobox>
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

    // Initially, set focus on the input, but hide menu.
    setTimeout(() => {
      this.searchInput?.focus();
      this.menu = false;
    }, 0);

    // https://www.learnrxjs.io/learn-rxjs/recipes/type-ahead
    if (this.searchInput) {
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
          this._handleTypeahead();
        });
    }
  }

  public onSearch() {
    this._onChange();
    this.previousValueInternal = this.valueInternal;
    if (this.valueInternal && useRoute().name !== "search") {
      useRouter()
        .push({ name: "search", query: { q: this.valueInternal } })
        .catch(sameRouteNavigationErrorHandler);
    }
    this.menu = false;
  }

  public async onHintSelected(event: PointerEvent, hint: IHint) {
    // Ignore clicks on the action buttons
    if (
      // @ts-ignore
      event.target?.classList.contains("mdi-close")
    ) {
      return;
    }

    this.valueInternal = hint.key;
    this.isFetchingHints = !!this.valueInternal;
    this.onSearch();
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

  _handleTypeahead() {
    this.hints = this.typeaheadHints;
    if (this.valueInternal) {
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
