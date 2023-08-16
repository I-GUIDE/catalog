import { Model } from "@vuex-orm/core";
import { INITIAL_RANGE } from "@/constants";
export interface ISearchResultsState {
  publicationYear: [number, number];
  dataCoverage: [number, number];
}

export default class SearchResults extends Model {
  static entity = "search-results";

  static fields() {
    return {};
  }

  static get $state(): ISearchResultsState {
    return this.store().state.entities[this.entity];
  }

  static state() {
    return {
      publicationYear: INITIAL_RANGE,
      dataCoverage: INITIAL_RANGE,
    };
  }
}
