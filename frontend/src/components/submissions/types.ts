export interface ISubmission {
  title: string;
  authors: string[];
  date: number;
  identifier: string;
  url: string;
  metadata: any;
}

export enum EnumSubmissionSorts {
  title = "Title",
  date = "Submission Date",
}

export enum EnumSortDirections {
  asc = "Ascending",
  desc = "Descending",
}
