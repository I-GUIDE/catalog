<template>
  <v-menu offset-y v-model="menu">
    <template v-slot:activator="{ on }">
      <v-text-field
        ref="search"
        @keydown.up="onDetectCrossover('up')"
        @keydown.down="onDetectCrossover('down')"
        @keyup.up="onHintHighlighted()"
        @keyup.down="onHintHighlighted()"
        @keydown.enter="onSearch"
        @click:clear="$emit('clear')"
        v-model.trim.lazy="valueInternal"
        class="cz-search white"
        prepend-inner-icon="mdi-magnify"
        :placeholder="$t(`home.search.inputPlaceholder`)"
        rounded
        full-width
        hide-details
        flat
        outlined
        dense
        clearable
        v-on="on"
      />
    </template>

    <v-progress-linear
      v-if="isFetchingHints"
      indeterminate
      absolute
      color="yellow darken-2"
    />

    <v-list max-height="20rem">
      <v-list-item-group v-if="showList">
        <v-list-item
          v-for="(hint, index) of hints"
          ref="hintElements"
          :key="index"
          dense
          @pointerdown="onHintSelected($event, hint)"
        >
          <v-list-item-icon>
            <v-icon dense v-if="hint.type === 'local'">mdi-history</v-icon>
            <v-icon dense v-else>mdi-magnify</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title
              :class="{ 'accent--text': hint.type === 'local' }"
              class="font-weight-regular"
              >{{ hint.key }}</v-list-item-title
            >
          </v-list-item-content>

          <v-list-item-action class="ma-0 pa-0" v-if="hint.type === 'local'">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  icon
                  x-small
                  v-bind="attrs"
                  v-on="on"
                  @click.stop="deleteHint(hint)"
                >
                  <v-icon ref="btnDeleteHint">mdi-close</v-icon>
                </v-btn>
              </template>
              <span>Delete</span>
            </v-tooltip>
          </v-list-item-action>
        </v-list-item>
      </v-list-item-group>
    </v-list>
  </v-menu>
</template>

<script lang="ts">
import { Component, Vue, Prop, Ref, Watch } from "vue-property-decorator";
import { APP_NAME, sameRouteNavigationErrorHandler } from "@/constants";
import { fromEvent, from } from "rxjs";
import { debounceTime, map, switchMap, tap } from "rxjs/operators";
import SearchHistory from "@/models/search-history.model";
import Search from "@/models/search.model";

const typeaheadDebounceTime = 500;

@Component({
  name: "cd-search",
  components: {},
})
export default class CdSearch extends Vue {
  @Prop() value!: string;
  @Ref("search") searchInput;
  @Ref("hintElements") hintElements;
  @Ref("btnDeleteHint") btnDeleteHint;

  protected appName = APP_NAME;

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
          t.value.toLowerCase().indexOf(valueInternal) >= 0
      )
      .map((t) => t.value.toLowerCase())
      .filter(
        (v: string) =>
          v !== valueInternal && !this.localHints.some((h) => h.key === v)
      );

    hints = [...new Set(hints)].slice(0, 10) as string[]; // get unique ones
    hints = hints.map((key) => ({ type: "db", key } as IHint));
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
    this.valueInternal = this.value;
    this.previousValueInternal = this.value;
    try {
      await this._onTypeahead();
    } catch (e) {}
    this.hints = this.typeaheadHints;
    this.searchInput?.focus();

    // https://www.learnrxjs.io/learn-rxjs/recipes/type-ahead
    fromEvent(this.searchInput.$el, "input")
      .pipe(
        tap(() => {
          this.isFetchingHints = !!this.valueInternal;
          // Show hints from local history while the database ones load
          this.hints = this.localHints;
          this.menu = true;
        }),
        debounceTime(typeaheadDebounceTime),
        map((e: any) => e.target.value),
        switchMap(() => from(this._onTypeahead()))
      )
      .subscribe(() => {
        this._handleTypeahead(false);
      });
  }

  public onSearch() {
    this._onChange();
    this.previousValueInternal = this.valueInternal;
    if (this.valueInternal && this.$route.name !== "search") {
      this.$router
        .push({ name: "search", query: { q: this.valueInternal } })
        .catch(sameRouteNavigationErrorHandler);
    }
    this.menu = false;
  }

  /** Detects when the user crosses over from the beginning or end of the list items.
   * Then restores original value, hide the menu, and focus the input
   */
  public onDetectCrossover(direction: "up" | "down") {
    const hintIndex = this.hintElements.findIndex((e) =>
      e.$el.classList.contains("v-list-item--highlighted")
    );
    if (this.detectCrossover) {
      const hasCrossedOver =
        (direction === "down" && hintIndex === this.hints.length - 1) ||
        (direction === "up" && hintIndex === 0);

      if (hasCrossedOver) {
        this.valueInternal = this.previousValueInternal;
        this.menu = false;
        this.detectCrossover = false;
        return;
      }
    } else {
      this.detectCrossover = true;
    }
  }

  /** Handles moving up and down the list of hints using the arrow keys */
  public onHintHighlighted() {
    const hintIndex = this.hintElements.findIndex((e) =>
      e.$el.classList.contains("v-list-item--highlighted")
    );

    if (hintIndex >= 0) {
      this.valueInternal = this.hints[hintIndex].key;
    }
  }

  public browse(term: string) {
    this.valueInternal = term;
    this.onSearch();
  }

  public async onHintSelected(event: PointerEvent, hint: IHint) {
    // We only act on 'pointerdown' event. The enter key is already captured in the input.
    // The value is already populated by onHintHighlighted.

    // Ignore clicks on the action buttons
    if (
      this.btnDeleteHint &&
      this.btnDeleteHint.map((btn) => btn.$el).includes(event.target)
    ) {
      return;
    }

    if (event.type === "pointerdown") {
      this.valueInternal = hint.key;
      this.isFetchingHints = !!this.valueInternal;
      this.onSearch();
      await this._onTypeahead();
      this._handleTypeahead(false);
    }
  }

  public deleteHint(hint: IHint) {
    SearchHistory.deleteHint(hint.key);
    this.hints = this.typeaheadHints;
  }

  private async _onTypeahead() {
    if (!this.valueInternal?.trim()) {
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

  private _handleTypeahead(bringUpHintsMenu = true) {
    this.hints = this.typeaheadHints;
    if (this.valueInternal) {
      this.menu = bringUpHintsMenu || this.menu;
      this.isFetchingHints = false;
    }
  }

  private _onChange() {
    this.$emit("input", this.valueInternal);
  }
}
</script>

<style lang="scss" scoped>
.cd-home-search {
  background: #ddd;
}

.search-container {
  max-width: 45rem;
}

.v-item-group {
  background: #fff;
}
</style>
