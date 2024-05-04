<template>
  <div class="cd-submissions">
    <div>
      <div class="text-h4">My Submissions</div>
      <v-divider class="mb-4" />
      <div class="d-flex align-sm-center flex-column flex-sm-row">
        <v-text-field
          id="my_submissions_search"
          class="ma-1 my-2 my-sm-0"
          v-model="searchStr"
          density="compact"
          clearable
          variant="outlined"
          hide-details
          prepend-inner-icon="mdi-magnify"
          label="Search..."
        />

        <v-spacer></v-spacer>

        <v-btn
          color="primary"
          class="mr-2"
          rounded
          @click="router.push({ name: 'register' })"
        >
          <v-icon class="mr-2">mdi-link-plus</v-icon>
          Register Dataset
        </v-btn>

        <v-btn
          color="primary"
          rounded
          @click="router.push({ name: 'contribute' })"
        >
          <v-icon class="mr-2">mdi-text-box-plus</v-icon>
          New Submission
        </v-btn>
      </div>
    </div>

    <template v-if="isFetching">
      <div class="d-flex justify-center align-center mt-16">
        <v-progress-circular indeterminate color="primary" />
      </div>
    </template>
    <template v-else>
      <div v-if="submissions.length" class="mt-4">
        <div>
          <div id="total_submissions" class="mb-4 text-h6">
            {{ submissions.length }} Total Submissions
          </div>
          <p v-if="isAnyFilterAcitve" class="text-medium-emphasis">
            {{ currentItems.length }} Results
          </p>
        </div>

        <v-card>
          <div v-if="!isFetching">
            <v-data-iterator
              @current-items="currentItems = $event"
              :items="filteredSubmissions"
              :items-per-page.sync="itemsPerPage"
              :page.sync="page"
              :search="searchStr"
              :sort-by="[sortBy]"
              item-key="id"
              hide-default-footer
            >
              <template #header>
                <div elevation="0" class="has-bg-light-gray pa-4">
                  <div
                    class="d-flex justify-space-between full-width flex-column flex-md-row"
                  >
                    <v-btn
                      class="mb-md-0 mb-4"
                      rounded
                      @click="exportSubmissions"
                      :disabled="!filteredSubmissions.length"
                      >Export Submissions</v-btn
                    >
                    <v-spacer></v-spacer>
                    <div class="sort-controls d-flex flex-column flex-sm-row">
                      <v-select
                        id="sort-by"
                        :items="sortOptions"
                        v-model="sortBy.key"
                        item-title="label"
                        item-value="key"
                        class="sort-control mr-2"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        label="Sort by"
                      />

                      <v-select
                        id="sort-order"
                        :items="sortDirectionOptions"
                        v-model="sortBy.order"
                        item-title="label"
                        item-value="key"
                        class="sort-control"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        label="Order"
                      />
                    </div>
                  </div>
                </div>
              </template>

              <template #default="{ items }">
                <v-divider />
                <div
                  :id="`submission-${index}`"
                  v-for="(item, index) in items"
                  :key="item.raw.id"
                >
                  <div
                    class="table-item d-flex justify-space-between flex-column flex-md-row"
                  >
                    <div class="flex-grow-1 mr-4">
                      <table
                        class="text-body-1"
                        :class="{ 'is-xs-small': $vuetify.display.xs }"
                      >
                        <tr>
                          <td
                            colspan="2"
                            :id="`sub-${index}-title`"
                            class="text-h6 title"
                          >
                            {{ item.raw.title }}
                          </td>
                        </tr>
                        <tr v-if="item.raw.authors?.length">
                          <th class="pr-4 body-2">Authors:</th>
                          <td>{{ item.raw.authors.join(" | ") }}</td>
                        </tr>

                        <tr>
                          <th class="pr-4 body-2">Submission Date:</th>
                          <td :id="`sub-${index}-date`">
                            {{ getDateInLocalTime(item.raw.date) }}
                          </td>
                        </tr>
                        <!-- TODO: get the identifier in the schema, not the db identifier -->
                        <!-- <tr>
                          <th class="pr-4 body-2">Identifier:</th>
                          <td>{{ item.identifier }}</td>
                        </tr> -->
                      </table>
                    </div>

                    <div class="d-flex flex-column mt-4 mt-md-0 actions">
                      <!-- VIEW -->
                      <v-btn
                        :id="`sub-${index}-view`"
                        target="_blank"
                        color="blue-grey lighten-4"
                        rounded
                        @click="
                          router.push({
                            name: 'dataset',
                            params: { id: item.raw.identifier },
                          })
                        "
                      >
                        <v-icon class="mr-1">mdi-text-box</v-icon> View
                      </v-btn>

                      <!-- VIEW IN REPOSITORY -->
                      <v-btn
                        v-if="item.raw.repoIdentifier"
                        :id="`sub-${index}-view-repo`"
                        :href="item.raw.url"
                        target="_blank"
                        color="blue-grey lighten-4"
                        rounded
                      >
                        <v-icon class="mr-1">mdi-open-in-new</v-icon> View in
                        repository
                      </v-btn>

                      <!-- UPDATE -->
                      <v-btn
                        v-if="
                          item.raw.repoIdentifier &&
                          item.raw.repository !== 'S3'
                        "
                        :id="`sub-${index}-update`"
                        @click="onUpdate(item.raw)"
                        :disabled="
                          isUpdating[item.raw.id] || isDeleting[item.raw.id]
                        "
                        rounded
                      >
                        <v-icon v-if="isUpdating[item.raw.id]"
                          >fas fa-circle-notch fa-spin</v-icon
                        >
                        <v-icon v-else>mdi-update</v-icon
                        ><span class="ml-1">
                          {{
                            isUpdating[item.raw.id]
                              ? "Updating Record..."
                              : "Update Record"
                          }}</span
                        >
                      </v-btn>

                      <!-- EDIT -->
                      <v-btn
                        v-else
                        :id="`sub-${index}-edit`"
                        @click="
                          router.push({
                            name: 'dataset-edit',
                            params: { id: item.raw.identifier },
                          })
                        "
                        :disabled="
                          isUpdating[item.raw.id] || isDeleting[item.raw.id]
                        "
                        rounded
                      >
                        <v-icon>mdi-pencil</v-icon
                        ><span class="ml-1">Edit</span>
                      </v-btn>

                      <!-- DELETE -->
                      <v-btn
                        :id="`sub-${index}-delete`"
                        @click="onDelete(item.raw)"
                        :disabled="
                          isUpdating[item.raw.id] || isDeleting[item.raw.id]
                        "
                        rounded
                      >
                        <v-icon v-if="isDeleting[item.raw.id]"
                          >fas fa-circle-notch fa-spin</v-icon
                        >
                        <v-icon v-else>mdi-delete</v-icon
                        ><span class="ml-1">
                          {{
                            isDeleting[item.raw.id] ? "Deleting..." : "Delete"
                          }}</span
                        >
                      </v-btn>
                    </div>
                  </div>
                  <v-divider />
                </div>
              </template>

              <template #footer>
                <div class="footer d-flex justify-space-between align-center">
                  <div>
                    <span class="grey--text text-body-2 mr-1"
                      >Items per page</span
                    >
                    <v-menu offset-y>
                      <template #activator="{ props }">
                        <v-btn variant="text" v-bind="props">
                          {{ itemsPerPage }}
                          <v-icon>mdi-chevron-down</v-icon>
                        </v-btn>
                      </template>
                      <v-list>
                        <v-list-item
                          v-for="(number, index) in itemsPerPageArray"
                          :key="index"
                          @click="itemsPerPage = number"
                        >
                          <v-list-item-title>{{ number }}</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </div>

                  <div
                    v-if="numberOfPages"
                    class="d-flex flex-sm-row flex-column align-center justify-center"
                    style="gap: 0.5rem"
                  >
                    <span class="grey--text text-body-2 text-center">
                      Page {{ page }} of {{ numberOfPages }}
                    </span>
                    <div>
                      <v-btn
                        class="mr-2"
                        small
                        fab
                        @click="formerPage"
                        :disabled="page <= 1"
                      >
                        <v-icon>mdi-chevron-left</v-icon>
                      </v-btn>
                      <v-btn
                        small
                        fab
                        @click="nextPage"
                        :disabled="page >= numberOfPages"
                      >
                        <v-icon>mdi-chevron-right</v-icon>
                      </v-btn>
                    </div>
                  </div>
                </div>
              </template>

              <template #no-data>
                <div class="text-subtitle-1 text-medium-emphasis ma-4">
                  You don't have any submissions that match the selected
                  criteria.
                </div>
              </template>

              <template #no-results>
                <div class="text-subtitle-1 text-medium-emphasis ma-4">
                  You don't have any submissions that match the selected
                  criteria.
                </div>
              </template>
            </v-data-iterator>
          </div>
        </v-card>
      </div>
      <div v-else class="text-body-2 text-center mt-8 d-flex flex-column">
        <template v-if="!submissions.length">
          <v-icon style="font-size: 6rem" class="mb-4"
            >mdi-text-box-remove</v-icon
          >
          You have not created any submissions yet
        </template>
        <template v-if="!isLoggedIn">
          You need to log in to view this page
        </template>
      </div>
    </template>

    <v-dialog
      id="dialog-delete-submission"
      v-model="isDeleteDialogActive"
      persistent
      width="500"
    >
      <v-card>
        <v-card-title>Delete this submission?</v-card-title>
        <v-card-text v-if="deleteDialogData" class="text-body-1">
          <p>
            This action will delete the metadata for this submission in the
            iGuide Portal.
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn class="dialog-cancel" @click="isDeleteDialogActive = false">
            Cancel
          </v-btn>

          <v-btn
            class="dialog-confirm"
            @click="
              isDeleteDialogActive = false;
              onDeleteSubmission();
            "
            color="red darken-1"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Component, Vue, toNative } from "vue-facing-decorator";
import {
  ISubmission,
  EnumSubmissionSorts,
  EnumSortDirections,
} from "@/components/submissions/types";
import { Subscription } from "rxjs";
import { itemsPerPageArray } from "@/components/submissions/constants";
import Submission from "@/models/submission.model";
import User from "@/models/user.model";
import { Collection } from "@vuex-orm/core";
import { useRouter } from "vue-router";

@Component({
  name: "cd-submissions",
  components: {},
})
class CdSubmissions extends Vue {
  isUpdating: { [key: string]: boolean } = {};
  isDeleting: { [key: string]: boolean } = {};
  isDeleteDialogActive = false;
  deleteDialogData: {
    submission: ISubmission;
  } | null = null;

  searchStr: string = "";

  itemsPerPageArray = itemsPerPageArray;
  page = 1;
  enumSubmissionSorts = EnumSubmissionSorts;
  currentItems = [];
  loggedInSubject = new Subscription();
  router = useRouter();

  get sortBy() {
    return Submission.$state.sortBy;
  }

  set sortBy(sortBy: { key: string; order: "asc" | "desc" }) {
    Submission.commit((state) => {
      state.sortBy = sortBy;
    });
  }

  get sortOptions() {
    return Object.keys(EnumSubmissionSorts).map((key) => {
      // @ts-ignore
      return { key, label: EnumSubmissionSorts[key] as string };
    });
  }

  get sortDirectionOptions() {
    return Object.keys(EnumSortDirections).map((key) => {
      return {
        key,
        // @ts-ignore
        label: EnumSortDirections[key],
      };
    });
  }

  get itemsPerPage() {
    return Submission.$state.itemsPerPage;
  }

  set itemsPerPage(itemsPerPage: number) {
    Submission.commit((state) => {
      state.itemsPerPage = itemsPerPage;
    });
  }

  get isFetching() {
    return Submission.$state.isFetching;
  }

  get isLoggedIn() {
    return User.$state.isLoggedIn;
  }

  get isAnyFilterAcitve() {
    return !!this.searchStr.length;
  }

  get filteredSubmissions(): Collection<Submission> {
    return Submission.all();
  }

  get submissions(): Collection<Submission> {
    return Submission.all();
  }

  get numberOfPages() {
    if (this.isAnyFilterAcitve) {
      return Math.ceil(this.currentItems.length / this.itemsPerPage);
    }
    return Math.ceil(this.submissions.length / this.itemsPerPage);
  }

  created() {
    if (User.$state.isLoggedIn) {
      Submission.fetchSubmissions();
    }

    this.loggedInSubject = User.loggedIn$.subscribe(() => {
      Submission.fetchSubmissions();
    });
  }

  beforeDestroy() {
    this.loggedInSubject.unsubscribe();
  }

  nextPage() {
    if (this.page + 1 <= this.numberOfPages) this.page += 1;
  }

  formerPage() {
    if (this.page - 1 >= 1) this.page -= 1;
  }

  getDateInLocalTime(date: number): string {
    const offset = new Date(date).getTimezoneOffset() * 60 * 1000;
    // TODO: subtracting offset because db stored dates seem to have the time shifted
    const localDateTime = date - offset;
    const localizedDate = new Date(localDateTime).toLocaleString();
    // const ago = formatDistanceToNow(new Date(localDateTime), { addSuffix: true })
    return localizedDate;
  }

  exportSubmissions() {
    const parsedSubmissions = this.filteredSubmissions.map((s) => {
      return {
        authors: s.authors.join("; "),
        date: new Date(s.date).toISOString(),
        title: s.title,
        url: s.url,
      };
    });

    const columnLabels = ["Authors", "Publication Date", "Title", "URL"];

    const headerRow = columnLabels.join(",") + "\n";
    const rows = parsedSubmissions.map((s) => {
      // @ts-ignore
      return Object.keys(s).map((key) => `"${s[key]}"`);
    });

    const csvContent = headerRow + rows.map((c) => c.join(",")).join("\n");

    // Download as CSV
    const filename = `iGuide_submissions.csv`;

    const element = document.createElement("a");
    element.setAttribute(
      "href",
      "data:text/plain;charset=utf-8," + encodeURIComponent(csvContent),
    );
    element.setAttribute("download", filename);

    element.style.display = "none";
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
  }

  onDelete(submission: ISubmission) {
    this.deleteDialogData = { submission };
    this.isDeleteDialogActive = true;
  }

  async onUpdate(submission: ISubmission) {
    if (submission.repoIdentifier) {
      this.isUpdating[submission.id] = true;
      await Submission.updateSubmission(submission.repoIdentifier);
      this.isUpdating[submission.id] = false;
    }
  }

  async onDeleteSubmission() {
    if (this.deleteDialogData?.submission.id) {
      this.isDeleting[this.deleteDialogData.submission.id] = true;
    }

    if (this.deleteDialogData) {
      await Submission.deleteSubmission(
        this.deleteDialogData.submission.identifier,
        this.deleteDialogData?.submission.id,
      );
    }

    if (this.deleteDialogData?.submission.id) {
      this.isDeleting[this.deleteDialogData.submission.id] = false;
    }
    this.deleteDialogData = null;
  }
}
export default toNative(CdSubmissions);
</script>

<style lang="scss" scoped>
.cd-submissions {
  padding: 1rem;
  min-height: 30rem;
}

.v-card {
  margin: 0;
}

.footer {
  padding: 1rem;
}

.table-item {
  padding: 1rem;

  table {
    width: 100%;

    &.is-xs-small {
      tr,
      td,
      th {
        display: block;
        text-align: left;
      }

      th {
        padding-top: 1rem;
      }
    }

    th {
      text-align: right;
      width: 11rem;
      font-weight: normal;
    }

    td {
      word-break: break-word;

      &.title {
        padding-left: 1.25rem;
        border-left: 4px solid #ddd;
      }
    }
  }
}

.actions {
  align-content: flex-end;
  min-width: 16rem;
}

.actions .v-btn {
  margin: 0.5rem 0;
  // max-width: 30rem;
}

.sort-controls {
  // max-width: 30rem;
  display: flex;

  > * {
    width: 15rem;
  }
}

.v-speed-dial {
  :deep(.v-speed-dial__list) {
    width: auto;

    .v-btn {
      min-width: 12rem;
    }
  }
}
</style>
