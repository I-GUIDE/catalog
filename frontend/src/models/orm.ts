import VuexORM from "@vuex-orm/core";
import User from "@/models/user.model";
import Submission from "@/models/submission.model";
import SearchHistory from "./search-history.model";
import SearchResults from "./search-results.model";
import Search from "./search.model";

/**
 * Register all the Models here.
 * https://vuex-orm.org/guide
 */
const db = new VuexORM.Database();
db.register(User);
db.register(Submission);
db.register(SearchResults);
db.register(SearchHistory);
db.register(Search);

export const orm = db;
