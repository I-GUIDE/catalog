export interface ISubmission {
  title: string;
  authors: string[];
  date: number;
  identifier: string;
  url: string;
  id: string;
  repoIdentifier?: string;
  repository: string;
  // metadata: any;
}

export enum EnumSubmissionSorts {
  title = "Title",
  date = "Submission Date",
}

export enum EnumSortDirections {
  asc = "Ascending",
  desc = "Descending",
}

export enum EnumRepositoryKeys {
  hydroshare = "hydroshare",
  zenodo = "zenodo",
  earthchem = "earthchem",
  external = "external",
  openTopography = "openTopography",
  sesar = "sesar",
  dryad = "dryad",
  pangaea = "pangaea",
  edi = "edi",
  scienceBase = "scienceBase",
  osf = "osf",
  geo = "geo",
  bioSample = "bioSample",
  sra = "sra",
  itrdb = "itrdb",
  mgds = "mgds",
  harvardDataverse = "harvardDataverse",
  figshare = "figshare",
  magIc = "magIc",
  ornlDaac = "ornlDaac",
  bcoDmo = "bcoDmo",
  vegBank = "vegBank",
  essDive = "geo",
  socib = "socib",
  polarRock = "polarRock",
  crystalography = "crystalography",
  digitalRocksPortal = "digitalRocksPortal",
  doe = "doe",
  scienceDataBank = "scienceDataBank",
  tpdc = "tpdc",
  dataOne = "dataOne",
  gitHub = "github",
  ameriFlux = "ameriflux",
  hydrolearn = "hydrolearn",
  // other = 'other'
}

export interface IRepositoryUrls {
  schemaUrl: string;
  uischemaUrl: string;
  schemaDefaultsUrl: string;
  createUrl: string;
  updateUrl: string; // To update metadata
  readUrl: string;
  deleteUrl: string;
  fileCreateUrl: string;
  fileDeleteUrl: string;
  fileReadUrl: string;
  folderCreateUrl?: string;
  folderReadUrl?: string;
  folderDeleteUrl?: string;
  moveOrRenameUrl?: string;
  accessTokenUrl: string;
  authorizeUrl: string;
  viewUrl: string;
}

export interface IRepository {
  key: EnumRepositoryKeys;
  name: string;
  dropdownName?: string;
  logoSrc: string;
  description: string;
  submitLabel?: string;
  exampleUrl?: string;
  exampleIdentifier?: string;
  identifierUrlPattern?: RegExp;
  identifierPattern?: RegExp;
  urls?: IRepositoryUrls;
  schema?: any;
  uischema?: any;
  schemaDefaults?: any;
  isDisabled?: boolean;
  isSupported?: boolean;
  isComingSoon?: boolean;
  isExternal?: boolean;
  hasFolderStructure?: boolean;
  supportedFileTypes?: string[];
  /** Largest size per file allowed for upload. In KibiBytes. https://web.archive.org/web/20150324153922/https://pacoup.com/2009/05/26/kb-kb-kib-whats-up-with-that/ */
  maxUploadSizePerFile?: number;
  /** Maximum allowed total upload size */
  maxTotalUploadSize?: number;
  maxNumberOfFiles?: number;
  fileNameRegex?: any;
  url?: string;
  supportUrl?: string;
  submitTooltip?: string;
}
