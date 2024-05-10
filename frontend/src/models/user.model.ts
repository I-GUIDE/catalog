import { Model } from "@vuex-orm/core";
import { Subject } from "rxjs";
import { RouteLocationRaw, Router } from "vue-router";
import { getQueryString } from "@/util";
import { APP_URL, ENDPOINTS, LOGIN_URL, CLIENT_ID } from "@/constants";
import { Notifications } from "@cznethub/cznet-vue-core";

export interface ICurrentUserState {
  accessToken: string;
}

export interface IUserState {
  isLoggedIn: boolean;
  accessToken: string;
  next: string;
  hasUnsavedChanges: boolean;
  schema: any;
  uiSchema: any;
  schemaDefaults: any;
}

export default class User extends Model {
  static entity = "users";
  static isLoginListenerSet = false;
  static logInDialog$ = new Subject<RouteLocationRaw | undefined>();
  static loggedIn$ = new Subject<void>();
  static controller = new AbortController();

  static fields() {
    return {};
  }

  static get $state(): IUserState {
    return this.store().state.entities[this.entity];
  }

  static get next() {
    return;
  }

  static get accessToken() {
    return this.$state?.accessToken;
  }

  static state(): IUserState {
    return {
      isLoggedIn: false,
      accessToken: "",
      next: "",
      hasUnsavedChanges: false,
      schema: null,
      uiSchema: null,
      schemaDefaults: null,
    };
  }

  static openLogInDialog(redirectTo?: RouteLocationRaw) {
    this.logInDialog$.next(redirectTo);
  }

  static async _____logIn(callback?: () => any) {
    const params = {
      response_type: "token",
      client_id: `${CLIENT_ID}`,
      redirect_uri: `${APP_URL}/auth-redirect`,
      window_close: "True",
      scope: "openid",
    };

    window.open(
      `${LOGIN_URL}?${getQueryString(params)}`,
      "_blank",
      "location=1, status=1, scrollbars=1, width=800, height=800",
    );

    if (!this.isLoginListenerSet) {
      this.isLoginListenerSet = true; // Prevents registering the listener more than once
      window.addEventListener("message", async (event: MessageEvent) => {
        if (
          event.origin !== APP_URL ||
          !event.data.hasOwnProperty("accessToken")
        ) {
          return;
        }

        if (event.data.accessToken) {
          Notifications.toast({
            message: "You have logged in!",
            type: "success",
          });
          await User.commit((state) => {
            state.isLoggedIn = true;
            state.accessToken = event.data.accessToken;
          });
          this.loggedIn$.next();
          this.isLoginListenerSet = false;
          callback?.();
        } else {
          Notifications.toast({
            message: "Failed to Log In",
            type: "error",
          });
        }
      });
    }
  }

  static async logIn(callback?: () => any) {
    const handleMessage = async (event: MessageEvent) => {
      if (
        event.origin !== APP_URL ||
        !Object.prototype.hasOwnProperty.call(event.data, "accessToken")
      ) {
        return;
      }

      if (event.data.accessToken) {
        Notifications.toast({
          message: "You have logged in!",
          type: "success",
        });
        await User.commit((state) => {
          state.isLoggedIn = true;
          state.accessToken = event.data.accessToken;
        });
        this.controller.abort();
        this.loggedIn$.next();
        callback?.();
      } else {
        Notifications.toast({
          message: "Failed to Log In",
          type: "error",
        });
      }
    };

    const params = {
      response_type: "token",
      client_id: `${CLIENT_ID}`,
      redirect_uri: `${APP_URL}/auth-redirect`,
      window_close: "True",
      scope: "openid",
    };

    window.open(
      `${LOGIN_URL}?${getQueryString(params)}`,
      "_blank",
      "location=1, status=1, scrollbars=1, width=800, height=800",
    );

    this.controller.abort();
    this.controller = new AbortController();
    window.addEventListener("message", handleMessage, {
      signal: this.controller.signal, // Used to remove the listener
    });
    console.info(`[User]: listening to login window...`);
  }

  static async checkAuthorization() {
    try {
      // TODO: find endpoint to verify authentication
      const response: Response = await fetch(
        `${ENDPOINTS.search}?${getQueryString({
          access_token: User.$state.accessToken,
        })}`,
      );

      if (response.status !== 200) {
        // Something went wrong, authorization may be invalid
        User.commit((state) => {
          state.isLoggedIn = false;
        });
      }
    } catch (e: any) {
      User.commit((state) => {
        state.isLoggedIn = false;
      });
    }
  }

  static async logOut(router?: Router) {
    await User.commit((state) => {
      (state.isLoggedIn = false), (state.accessToken = "");
    });
    this.isLoginListenerSet = false;

    Notifications.toast({
      message: "You have logged out!",
      type: "info",
    });

    // @ts-ignore
    if (router?.currentRoute?.meta?.hasLoggedInGuard) {
      router.push({ path: "/" });
    }
  }

  static async fetchSchemas() {
    const responses: PromiseSettledResult<any>[] = await Promise.allSettled([
      fetch(`${ENDPOINTS.schemaUrl}/`),
      fetch(`${ENDPOINTS.uiSchemaUrl}/`),
      fetch(`${ENDPOINTS.schemaDefaultsUrl}/`),
    ]);

    const results = responses.map((r: PromiseSettledResult<any>) => {
      if (r.status === "fulfilled") {
        return r.value;
      }
    });

    let schema: any = null;
    let uiSchema: any = null;
    let schemaDefaults: any = null;

    if (results[0]?.ok) {
      try {
      } catch (e) {}
      schema = await results[0]?.json();
      User.commit((state) => {
        state.schema = schema;
      });
    }
    if (results[1]?.ok) {
      uiSchema = await results[1]?.json();
      User.commit((state) => {
        state.uiSchema = uiSchema;
      });
    }
    if (results[2]?.ok) {
      schemaDefaults = await results[2]?.json();
      User.commit((state) => {
        state.schemaDefaults = schemaDefaults;
      });
    }
  }

  static async submit(data: any) {
    const response: Response = await fetch(`${ENDPOINTS.submit}/`, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.accessToken}`,
      },
    });
    const result = await response.json();
    return response.ok ? result._id : false;
  }

  static async submitS3(
    data: any,
    s3Data: { path: string; bucket: string; endpointUrl: string },
  ) {
    const formData = {
      s3_path: {
        path: s3Data.path,
        bucket: s3Data.bucket,
        endpoint_url: s3Data.endpointUrl,
      },
      document: data,
    };
    const response: Response = await fetch(`${ENDPOINTS.submitS3}/`, {
      method: "POST",
      body: JSON.stringify(formData),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.accessToken}`,
      },
    });
    const result = await response.json();
    return response.ok ? result._id : false;
  }

  /**
   * Updates an Amazon S3 submission
   * @param {string} identifier - the identifier of the resource in our database
   * @param {any} data - the form data to be saved
   * @param {any} s3 - the S3 bucket information to be saved
   */
  static async updateS3Dataset(
    identifier: string,
    data: any,
    s3Data: {
      path: string;
      bucket: string;
      endpointUrl: string;
    },
  ) {
    const formData = {
      s3_path: {
        path: s3Data.path,
        bucket: s3Data.bucket,
        endpoint_url: s3Data.endpointUrl,
      },
      document: data,
    };
    const response: Response = await fetch(
      `${ENDPOINTS.submitS3}/${identifier}`,
      {
        method: "PUT",
        body: JSON.stringify(formData),
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.accessToken}`,
        },
      },
    );

    if (response.ok) {
      return true;
    } else {
      Notifications.toast({
        message: "Failed to save changes",
        type: "error",
      });
    }
  }

  /**
   * Updates a submission
   * @param {string} identifier - the identifier of the resource in our database
   * @param {any} data - the form data to be saved
   */
  static async updateDataset(id: string, data: any) {
    const response: Response = await fetch(`${ENDPOINTS.dataset}/${id}/`, {
      method: "PUT",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.accessToken}`,
      },
    });

    if (response.ok) {
      return true;
    } else {
      Notifications.toast({
        message: "Failed to save changes",
        type: "error",
      });
    }
  }

  static async fetchDataset(id: string) {
    const response: Response = await fetch(`${ENDPOINTS.dataset}/${id}/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.accessToken}`,
      },
    });

    // TODO: need to get `repoIdentifier` as part of response from this endpoint.

    if (response.ok) {
      const result = await response.json();
      return result;
    } else {
      Notifications.toast({
        message: "Failed to load dataset",
        type: "error",
      });
    }
  }
}
