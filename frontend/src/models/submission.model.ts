import { ISubmission } from "@/components/submissions/types";
import { Model } from "@vuex-orm/core";
import User from "./user.model";
import { EnumSubmissionSorts } from "@/components/submissions/types";
import { itemsPerPageArray } from "@/components/submissions/constants";
import { ENDPOINTS } from "@/constants";
import { Notifications } from "@cznethub/cznet-vue-core";

export interface ISubmisionState {
  sortBy: { key: string; label: string; order: "asc" | "desc" };
  itemsPerPage: number;
  isFetching: boolean;
}

export default class Submission extends Model implements ISubmission {
  // This is the name used as module name of the Vuex Store.
  static entity = "submissions";
  static primaryKey = ["id"];
  public title!: string;
  public authors!: string[];
  public date!: number;
  public identifier!: string;
  public repoIdentifier?: string;
  public url!: string;
  public id!: string;
  // public metadata!: any;

  static get $state(): ISubmisionState {
    return this.store().state.entities[this.entity];
  }

  static state() {
    return {
      sortBy: { key: "date", label: EnumSubmissionSorts.date, order: "desc" },
      itemsPerPage: itemsPerPageArray[0],
      isFetching: false,
    };
  }

  // List of all fields (schema) of the post model. `this.attr` is used
  // for the generic field type. The argument is the default value.
  static fields() {
    return {
      title: this.attr(""),
      authors: this.attr([]),
      // @ts-ignore
      date: this.number(0),
      identifier: this.attr(""),
      repoIdentifier: this.attr(""),
      url: this.attr(""),
      id: this.attr(""),
      // metadata: this.attr({}),
    };
  }

  static getInsertDataFromDb(dbSubmission: any) {
    return {
      title: dbSubmission.title,
      authors: dbSubmission.authors,
      date: new Date(dbSubmission.submitted).getTime(),
      identifier: dbSubmission.identifier, // TODO: we should call this something else. It is not the same as the schema's identifier
      repoIdentifier: dbSubmission.repository_identifier,
      url: dbSubmission.url,
      id: dbSubmission._id,
    };
  }

  /** Used to transform submission data that comes from the repository API and was transformed to our schema */
  static getInsertData(apiSubmission: any): ISubmission | Partial<Submission> {
    return {
      title: apiSubmission.name,
      authors: apiSubmission.creator.map((c) => c.name),
      date: new Date(apiSubmission.dateCreated).getTime(),
      identifier: Array.isArray(apiSubmission.identifier)
        ? apiSubmission.identifier[0]
        : apiSubmission.identifier,
      url: apiSubmission.url,
      id: apiSubmission._id,
    };
  }

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

  // TODO: modify endpoint so that it can perform the delete with the db id itself
  static async deleteSubmission(identifier: string, id: string) {
    console.log("Deleting submission...");
    try {
      const response: Response = await fetch(
        `${ENDPOINTS.deleteSubmission}/${identifier}/`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${User.$state.accessToken}`,
          },
        },
      );

      if (response.ok) {
        await Submission.delete([id]);
      } else {
        Notifications.toast({
          message: "Failed to delete submission",
          type: "error",
        });
      }

      return response.status;
    } catch (e: any) {
      // this.commit((state) => {
      //   return (state.isFetching = false);
      // });
      // return e.status;
    }
  }

  /**
   * Reads a submission from a repository that has not been saved to our database
   * @param {string} identifier - the identifier of the resource in the repository
   */
  static async registerSubmission(identifier: string) {
    const response: Response = await fetch(
      `${ENDPOINTS.register}/${identifier}/`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${User.$state.accessToken}`,
        },
      },
    );

    if (response.ok) {
      const result = await response.json();
      Notifications.toast({
        message: "Your dataset has been registered!",
        type: "success",
      });
      return Submission.getInsertData(result);
    } else {
      // this.wasNotFound = true;
      if (response.status === 400) {
        Notifications.toast({
          message: "The resource provided has already been registered",
          type: "error",
        });
      } else {
        Notifications.toast({
          message: "Failed to load existing submission",
          type: "error",
        });
      }

      return response.status;
    }
  }

  /**
   * Refreshes a submission by re-fetching the data from the repository
   * @param {string} repoIdentifier - the identifier of the resource in the repository
   */
  static async updateSubmission(repoIdentifier: string) {
    const response: Response = await fetch(
      `${ENDPOINTS.refresh}/${repoIdentifier}/`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${User.$state.accessToken}`,
        },
      },
    );

    if (response.ok) {
      const result = await response.json();
      Notifications.toast({
        message: "Your dataset has been updated!",
        type: "success",
      });
      return result;
    } else {
      Notifications.toast({
        message: "Failed to update dataset",
        type: "error",
      });
      return null;
    }
  }
}
