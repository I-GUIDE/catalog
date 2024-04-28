import type { ViteSSGContext } from "vite-ssg";

export type UserModule = (ctx: ViteSSGContext) => void;

export interface IResult {
  id: string;
  creator: string[];
  dateCreated: string;
  datePublished: string;
  description: string;
  highlights: {
    path: string;
    score: number;
    texts: {
      type: string;
      value: string;
    }[];
  }[];
  license: string;
  keywords: string[];
  name: string;
  score: number; // unused for now...
  url: string;
  funding: string[];
  spatialCoverage: any;
}

export interface IHint {
  type: "db" | "local";
  key: string;
}

export interface ISearchFilter {
  publicationYear: {
    min: number;
    max: number;
    isActive: boolean;
  };
  dataCoverage: {
    min: number;
    max: number;
    isActive: boolean;
  };
  // contentType: {
  //   options: string[],
  //   value: string[]
  // },
  repository: {
    options: string[];
    value: string;
  };
  // project: {
  //   // options: string[],
  //   value: string[];
  // };
  creatorName: string;
}

export interface ISearchParams {
  term: string;
  pageSize: number;
  pageNumber: number;
  publishedStart?: number;
  publishedEnd?: number;
  dataCoverageStart?: number;
  dataCoverageEnd?: number;
  creatorName?: string;
  providerName?: string;
  // clusters?: string[];
  sortBy?: "name" | "dateCreated" | "relevance" | "registrationDate";
}

export interface ITypeaheadParams {
  term: string;
}
