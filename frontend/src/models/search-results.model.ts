import { Model } from "@vuex-orm/core";

export default class SearchResults extends Model {
  static entity = "search-results";

  static fields() {
    return {};
  }

  static get $state() {
    return this.store().state.entities[this.entity];
  }

  static state() {
    return {
      // sort: null,
    };
  }
}
