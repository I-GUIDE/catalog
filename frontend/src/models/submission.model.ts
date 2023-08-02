import { ISubmission } from "@/components/submissions/types";
import { Model } from "@vuex-orm/core";
import User from "./user.model";
import {
  EnumSubmissionSorts,
  EnumSortDirections,
} from "@/components/submissions/types";
import { itemsPerPageArray } from "@/components/submissions/constants";
import { ENDPOINTS } from "@/constants";

export interface ISubmisionState {
  sortBy: { key: string; label: string };
  sortDirection: { key: string; label: string };
  itemsPerPage: number;
  isFetching: boolean;
}

export default class Submission extends Model implements ISubmission {
  // This is the name used as module name of the Vuex Store.
  static entity = "submissions";
  static primaryKey = ["identifier"];
  public title!: string;
  public authors!: string[];
  public date!: number;
  public identifier!: string;
  public url!: string;
  public metadata!: any;

  static get $state(): ISubmisionState {
    return this.store().state.entities[this.entity];
  }

  static state() {
    return {
      sortBy: { key: "date", label: EnumSubmissionSorts.date },
      sortDirection: { key: "desc", label: EnumSortDirections.desc },
      itemsPerPage: itemsPerPageArray[0],
      isFetching: false,
    };
  }

  // List of all fields (schema) of the post model. `this.attr` is used
  // for the generic field type. The argument is the default value.
  static fields() {
    return {
      id: this.number(0),
      title: this.attr(""),
      authors: this.attr([]),
      // @ts-ignore
      date: this.number(0),
      identifier: this.attr(""),
      url: this.attr(""),
      metadata: this.attr({}),
    };
  }

  static getInsertDataFromDb(dbSubmission) {
    return {
      title: dbSubmission.title,
      authors: dbSubmission.authors,
      date: new Date(dbSubmission.submitted).getTime(),
      identifier: dbSubmission.identifier,
      // metadata: JSON.parse(dbSubmission.metadata_json),
      url: dbSubmission.url,
    };
  }

  // Note: Do not override the date we stored on creation unless specified. Submissions fetched from repositories might return dates localized to another timezone.
  // TODO: this should be refactored as a dedicated method on each repository model
  /** Used to transform submission data that comes from the repository API */
  // static getInsertData(apiSubmission, identifier: string, overrideDate?: boolean): ISubmission | Partial<Submission> {
  //   return {
  //     title: apiSubmission.title,
  //     authors: apiSubmission.authors,
  //     date: new Date(apiSubmission.submitted).getTime(),
  //     identifier: apiSubmission.identifier,
  //     metadata: {}
  //   }
  // }

  static async fetchSubmissions() {
    console.log("Fetching submissions...");
    try {
      this.commit((state) => {
        return (state.isFetching = true);
      });

      const response: Response = await fetch(ENDPOINTS.submissions, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${User.$state.accessToken}`,
        },
      });

      if (response.ok) {
        let data = await response.json();
        data = data.map(this.getInsertDataFromDb);
        this.insertOrUpdate({ data });
      } else if (response.status === 401) {
        // User has been logged out
        User.logOut();
      }
      this.commit((state) => {
        return (state.isFetching = false);
      });
      return response.status;
    } catch (e: any) {
      this.commit((state) => {
        return (state.isFetching = false);
      });

      // return response.status;
    }
  }

  static async deleteSubmission(identifier: string) {
    console.log("Deleting submission...");
    try {
      const response: Response = await fetch(
        `${ENDPOINTS.deleteSubmission}/${identifier}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${User.$state.accessToken}`,
          },
        }
      );

      if (response.ok) {
        let data = await response.json();
        console.log(data);
        await Submission.delete([identifier]);
        // data = data.map(this.getInsertDataFromDb);
        // this.insertOrUpdate({ data });
      } else if (response.status === 401) {
        // User has been logged out
        // User.logOut();
      }

      return response.status;
    } catch (e: any) {
      // this.commit((state) => {
      //   return (state.isFetching = false);
      // });
      // return e.status;
    }
  }
}
