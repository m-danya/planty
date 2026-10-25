/* eslint-disable */
/* tslint:disable */
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

/** ArchivedTasksResponse */
export interface ArchivedTasksResponse {
  /**
   * Title
   * @default "Archived tasks"
   */
  title?: string;
  /** Tasks */
  tasks: TaskResponse[];
}

/** Body_auth_db_cookie_login_api_auth_login_post */
export interface BodyAuthDbCookieLoginApiAuthLoginPost {
  /** Grant Type */
  grant_type?: string | null;
  /** Username */
  username: string;
  /** Password */
  password: string;
  /**
   * Scope
   * @default ""
   */
  scope?: string;
  /** Client Id */
  client_id?: string | null;
  /** Client Secret */
  client_secret?: string | null;
}

/** ErrorModel */
export interface ErrorModel {
  /** Detail */
  detail: string | Record<string, string>;
}

/** HTTPValidationError */
export interface HTTPValidationError {
  /** Detail */
  detail?: ValidationError[];
}

/** RecurrenceInfo */
export interface RecurrenceInfo {
  /** Period */
  period: number;
  /** Type */
  type: "days" | "weeks" | "months" | "years";
  /** Flexible Mode */
  flexible_mode: boolean;
}

/** SectionCreateRequest */
export interface SectionCreateRequest {
  /** Title */
  title: string;
  /**
   * Parent Id
   * @format uuid
   */
  parent_id: string;
}

/** SectionCreateResponse */
export interface SectionCreateResponse {
  /**
   * Id
   * @format uuid
   */
  id: string;
}

/** SectionMoveRequest */
export interface SectionMoveRequest {
  /**
   * Section Id
   * @format uuid
   */
  section_id: string;
  /**
   * To Parent Id
   * @format uuid
   */
  to_parent_id: string;
  /**
   * Index
   * @min 0
   */
  index: number;
}

/** SectionResponse */
export interface SectionResponse {
  /**
   * Id
   * @format uuid
   */
  id: string;
  /** Title */
  title: string;
  /** Parent Id */
  parent_id: string | null;
  /**
   * Added At
   * @format date-time
   */
  added_at: string;
  /** Subsections */
  subsections: SectionResponse[];
  /** Tasks */
  tasks: TaskResponse[];
}

/** SectionUpdateRequest */
export interface SectionUpdateRequest {
  /**
   * Id
   * @format uuid
   */
  id: string;
  /** Title */
  title?: string;
}

/** SectionUpdateResponse */
export interface SectionUpdateResponse {
  section: SectionResponse;
}

/** ShuffleSectionRequest */
export interface ShuffleSectionRequest {
  /**
   * Section Id
   * @format uuid
   */
  section_id: string;
}

/** TaskCreateRequest */
export interface TaskCreateRequest {
  /**
   * Section Id
   * @format uuid
   */
  section_id: string;
  /** Title */
  title: string;
  /** Description */
  description?: string | null;
  /** Due To */
  due_to?: string | null;
  recurrence?: RecurrenceInfo | null;
}

/** TaskCreateResponse */
export interface TaskCreateResponse {
  /**
   * Id
   * @format uuid
   */
  id: string;
}

/** TaskMoveRequest */
export interface TaskMoveRequest {
  /**
   * Task Id
   * @format uuid
   */
  task_id: string;
  /**
   * Section To Id
   * @format uuid
   */
  section_to_id: string;
  /**
   * Index
   * @min 0
   */
  index: number;
}

/** TaskRemoveRequest */
export interface TaskRemoveRequest {
  /**
   * Task Id
   * @format uuid
   */
  task_id: string;
}

/** TaskResponse */
export interface TaskResponse {
  /**
   * Id
   * @format uuid
   */
  id: string;
  /**
   * Section Id
   * @format uuid
   */
  section_id: string;
  /** Title */
  title: string;
  /** Description */
  description: string | null;
  /** Content */
  content: string | null;
  /** Is Completed */
  is_completed: boolean;
  /** Is Archived */
  is_archived: boolean;
  /**
   * Added At
   * @format date-time
   */
  added_at: string;
  /** Due To */
  due_to: string | null;
  recurrence: RecurrenceInfo | null;
}

/** TaskToggleArchivedRequest */
export interface TaskToggleArchivedRequest {
  /**
   * Task Id
   * @format uuid
   */
  task_id: string;
}

/** TaskToggleCompletedRequest */
export interface TaskToggleCompletedRequest {
  /**
   * Task Id
   * @format uuid
   */
  task_id: string;
  /**
   * Auto Archive
   * @default true
   */
  auto_archive?: boolean;
}

/** TaskUpdateRequest */
export interface TaskUpdateRequest {
  /**
   * Id
   * @format uuid
   */
  id: string;
  /** Title */
  title?: string;
  /** Description */
  description?: string | null;
  /** Due To */
  due_to?: string | null;
  recurrence?: RecurrenceInfo | null;
}

/** TaskUpdateResponse */
export interface TaskUpdateResponse {
  task: TaskResponse;
}

/** TasksByDateResponse */
export interface TasksByDateResponse {
  /**
   * Date
   * @format date
   */
  date: string;
  /** Tasks */
  tasks: TaskResponse[];
}

/** TasksByDatesResponse */
export interface TasksByDatesResponse {
  /** By Dates */
  by_dates: TasksByDateResponse[];
  /** Overdue */
  overdue: TaskResponse[];
}

/** UserCreate */
export interface UserCreate {
  /**
   * Email
   * @format email
   */
  email: string;
  /** Password */
  password: string;
  /**
   * Is Active
   * @default true
   */
  is_active?: boolean | null;
  /**
   * Is Superuser
   * @default false
   */
  is_superuser?: boolean | null;
  /**
   * Is Verified
   * @default false
   */
  is_verified?: boolean | null;
}

/** UserRead */
export interface UserRead {
  /**
   * Id
   * @format uuid
   */
  id: string;
  /**
   * Email
   * @format email
   */
  email: string;
  /**
   * Is Active
   * @default true
   */
  is_active?: boolean;
  /**
   * Is Superuser
   * @default false
   */
  is_superuser?: boolean;
  /**
   * Is Verified
   * @default false
   */
  is_verified?: boolean;
}

/** UserUpdate */
export interface UserUpdate {
  /** Password */
  password?: string | null;
  /** Email */
  email?: string | null;
  /** Is Active */
  is_active?: boolean | null;
  /** Is Superuser */
  is_superuser?: boolean | null;
  /** Is Verified */
  is_verified?: boolean | null;
}

/** ValidationError */
export interface ValidationError {
  /** Location */
  loc: (string | number)[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
}

import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, HeadersDefaults, ResponseType } from "axios";
import axios from "axios";

export type QueryParamsType = Record<string | number, any>;

export interface FullRequestParams extends Omit<AxiosRequestConfig, "data" | "params" | "url" | "responseType"> {
  /** set parameter to `true` for call `securityWorker` for this request */
  secure?: boolean;
  /** request path */
  path: string;
  /** content type of request body */
  type?: ContentType;
  /** query params */
  query?: QueryParamsType;
  /** format of response (i.e. response.json() -> format: "json") */
  format?: ResponseType;
  /** request body */
  body?: unknown;
}

export type RequestParams = Omit<FullRequestParams, "body" | "method" | "query" | "path">;

export interface ApiConfig<SecurityDataType = unknown> extends Omit<AxiosRequestConfig, "data" | "cancelToken"> {
  securityWorker?: (
    securityData: SecurityDataType | null,
  ) => Promise<AxiosRequestConfig | void> | AxiosRequestConfig | void;
  secure?: boolean;
  format?: ResponseType;
}

export enum ContentType {
  Json = "application/json",
  FormData = "multipart/form-data",
  UrlEncoded = "application/x-www-form-urlencoded",
  Text = "text/plain",
}

export class HttpClient<SecurityDataType = unknown> {
  public instance: AxiosInstance;
  private securityData: SecurityDataType | null = null;
  private securityWorker?: ApiConfig<SecurityDataType>["securityWorker"];
  private secure?: boolean;
  private format?: ResponseType;

  constructor({ securityWorker, secure, format, ...axiosConfig }: ApiConfig<SecurityDataType> = {}) {
    this.instance = axios.create({ ...axiosConfig, baseURL: axiosConfig.baseURL || "" });
    this.secure = secure;
    this.format = format;
    this.securityWorker = securityWorker;
  }

  public setSecurityData = (data: SecurityDataType | null) => {
    this.securityData = data;
  };

  protected mergeRequestParams(params1: AxiosRequestConfig, params2?: AxiosRequestConfig): AxiosRequestConfig {
    const method = params1.method || (params2 && params2.method);

    return {
      ...this.instance.defaults,
      ...params1,
      ...(params2 || {}),
      headers: {
        ...((method && this.instance.defaults.headers[method.toLowerCase() as keyof HeadersDefaults]) || {}),
        ...(params1.headers || {}),
        ...((params2 && params2.headers) || {}),
      },
    };
  }

  protected stringifyFormItem(formItem: unknown) {
    if (typeof formItem === "object" && formItem !== null) {
      return JSON.stringify(formItem);
    } else {
      return `${formItem}`;
    }
  }

  protected createFormData(input: Record<string, unknown>): FormData {
    if (input instanceof FormData) {
      return input;
    }
    return Object.keys(input || {}).reduce((formData, key) => {
      const property = input[key];
      const propertyContent: any[] = property instanceof Array ? property : [property];

      for (const formItem of propertyContent) {
        const isFileType = formItem instanceof Blob || formItem instanceof File;
        formData.append(key, isFileType ? formItem : this.stringifyFormItem(formItem));
      }

      return formData;
    }, new FormData());
  }

  public request = async <T = any, _E = any>({
    secure,
    path,
    type,
    query,
    format,
    body,
    ...params
  }: FullRequestParams): Promise<AxiosResponse<T>> => {
    const secureParams =
      ((typeof secure === "boolean" ? secure : this.secure) &&
        this.securityWorker &&
        (await this.securityWorker(this.securityData))) ||
      {};
    const requestParams = this.mergeRequestParams(params, secureParams);
    const responseFormat = format || this.format || undefined;

    if (type === ContentType.FormData && body && body !== null && typeof body === "object") {
      body = this.createFormData(body as Record<string, unknown>);
    }

    if (type === ContentType.Text && body && body !== null && typeof body !== "string") {
      body = JSON.stringify(body);
    }

    return this.instance.request({
      ...requestParams,
      headers: {
        ...(requestParams.headers || {}),
        ...(type ? { "Content-Type": type } : {}),
      },
      params: query,
      responseType: responseFormat,
      data: body,
      url: path,
    });
  };
}

/**
 * @title Planty
 * @version 0.1.0
 */
export class Api<SecurityDataType extends unknown> extends HttpClient<SecurityDataType> {
  api = {
    /**
     * No description
     *
     * @tags User tasks
     * @name CreateTaskApiTaskPost
     * @summary Create Task
     * @request POST:/api/task
     * @secure
     */
    createTaskApiTaskPost: (data: TaskCreateRequest, params: RequestParams = {}) =>
      this.request<TaskCreateResponse, HTTPValidationError>({
        path: `/api/task`,
        method: "POST",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name RemoveTaskApiTaskDelete
     * @summary Remove Task
     * @request DELETE:/api/task
     * @secure
     */
    removeTaskApiTaskDelete: (data: TaskRemoveRequest, params: RequestParams = {}) =>
      this.request<any, HTTPValidationError>({
        path: `/api/task`,
        method: "DELETE",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name UpdateTaskApiTaskPatch
     * @summary Update Task
     * @request PATCH:/api/task
     * @secure
     */
    updateTaskApiTaskPatch: (data: TaskUpdateRequest, params: RequestParams = {}) =>
      this.request<TaskUpdateResponse, HTTPValidationError>({
        path: `/api/task`,
        method: "PATCH",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name GetTasksByDateApiTaskByDateGet
     * @summary Get Tasks By Date
     * @request GET:/api/task/by_date
     * @secure
     */
    getTasksByDateApiTaskByDateGet: (
      query: {
        /**
         * Not Before
         * @format date
         */
        not_before: string;
        /**
         * Not After
         * @format date
         */
        not_after: string;
        /**
         * With Overdue
         * @default false
         */
        with_overdue?: boolean;
      },
      params: RequestParams = {},
    ) =>
      this.request<TasksByDatesResponse, HTTPValidationError>({
        path: `/api/task/by_date`,
        method: "GET",
        query: query,
        secure: true,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name GetTasksBySearchQueryApiTaskSearchGet
     * @summary Get Tasks By Search Query
     * @request GET:/api/task/search
     * @secure
     */
    getTasksBySearchQueryApiTaskSearchGet: (
      query: {
        /** Query */
        query: string;
      },
      params: RequestParams = {},
    ) =>
      this.request<TaskResponse[], HTTPValidationError>({
        path: `/api/task/search`,
        method: "GET",
        query: query,
        secure: true,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name MoveTaskApiTaskMovePost
     * @summary Move Task
     * @request POST:/api/task/move
     * @secure
     */
    moveTaskApiTaskMovePost: (data: TaskMoveRequest, params: RequestParams = {}) =>
      this.request<any, HTTPValidationError>({
        path: `/api/task/move`,
        method: "POST",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name ToggleTaskCompletedApiTaskToggleCompletedPost
     * @summary Toggle Task Completed
     * @request POST:/api/task/toggle_completed
     * @secure
     */
    toggleTaskCompletedApiTaskToggleCompletedPost: (data: TaskToggleCompletedRequest, params: RequestParams = {}) =>
      this.request<SectionResponse, HTTPValidationError>({
        path: `/api/task/toggle_completed`,
        method: "POST",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name ToggleTaskArchivedApiTaskToggleArchivedPost
     * @summary Toggle Task Archived
     * @request POST:/api/task/toggle_archived
     * @secure
     */
    toggleTaskArchivedApiTaskToggleArchivedPost: (data: TaskToggleArchivedRequest, params: RequestParams = {}) =>
      this.request<SectionResponse, HTTPValidationError>({
        path: `/api/task/toggle_archived`,
        method: "POST",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name GetArchivedTasksApiTasksArchivedGet
     * @summary Get Archived Tasks
     * @request GET:/api/tasks/archived
     * @secure
     */
    getArchivedTasksApiTasksArchivedGet: (params: RequestParams = {}) =>
      this.request<ArchivedTasksResponse, any>({
        path: `/api/tasks/archived`,
        method: "GET",
        secure: true,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name CreateSectionApiSectionPost
     * @summary Create Section
     * @request POST:/api/section
     * @secure
     */
    createSectionApiSectionPost: (data: SectionCreateRequest, params: RequestParams = {}) =>
      this.request<SectionCreateResponse, HTTPValidationError>({
        path: `/api/section`,
        method: "POST",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name PatchSectionApiSectionPatch
     * @summary Patch Section
     * @request PATCH:/api/section
     * @secure
     */
    patchSectionApiSectionPatch: (data: SectionUpdateRequest, params: RequestParams = {}) =>
      this.request<SectionUpdateResponse, HTTPValidationError>({
        path: `/api/section`,
        method: "PATCH",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name GetSectionApiSectionSectionIdGet
     * @summary Get Section
     * @request GET:/api/section/{section_id}
     * @secure
     */
    getSectionApiSectionSectionIdGet: (sectionId: string, params: RequestParams = {}) =>
      this.request<SectionResponse, HTTPValidationError>({
        path: `/api/section/${sectionId}`,
        method: "GET",
        secure: true,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name MoveSectionApiSectionMovePost
     * @summary Move Section
     * @request POST:/api/section/move
     * @secure
     */
    moveSectionApiSectionMovePost: (data: SectionMoveRequest, params: RequestParams = {}) =>
      this.request<any, HTTPValidationError>({
        path: `/api/section/move`,
        method: "POST",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name GetSectionsApiSectionsGet
     * @summary Get Sections
     * @request GET:/api/sections
     * @secure
     */
    getSectionsApiSectionsGet: (
      query?: {
        /**
         * Leaves Only
         * @default false
         */
        leaves_only?: boolean;
        /**
         * As Tree
         * @default true
         */
        as_tree?: boolean;
      },
      params: RequestParams = {},
    ) =>
      this.request<SectionResponse[], HTTPValidationError>({
        path: `/api/sections`,
        method: "GET",
        query: query,
        secure: true,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags User tasks
     * @name ShuffleSectionApiSectionShufflePost
     * @summary Shuffle Section
     * @request POST:/api/section/shuffle
     * @secure
     */
    shuffleSectionApiSectionShufflePost: (data: ShuffleSectionRequest, params: RequestParams = {}) =>
      this.request<SectionResponse, HTTPValidationError>({
        path: `/api/section/shuffle`,
        method: "POST",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags auth
     * @name AuthDbCookieLoginApiAuthLoginPost
     * @summary Auth:Db Cookie.Login
     * @request POST:/api/auth/login
     */
    authDbCookieLoginApiAuthLoginPost: (data: BodyAuthDbCookieLoginApiAuthLoginPost, params: RequestParams = {}) =>
      this.request<any, ErrorModel | HTTPValidationError>({
        path: `/api/auth/login`,
        method: "POST",
        body: data,
        type: ContentType.UrlEncoded,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags auth
     * @name AuthDbCookieLogoutApiAuthLogoutPost
     * @summary Auth:Db Cookie.Logout
     * @request POST:/api/auth/logout
     * @secure
     */
    authDbCookieLogoutApiAuthLogoutPost: (params: RequestParams = {}) =>
      this.request<any, void>({
        path: `/api/auth/logout`,
        method: "POST",
        secure: true,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags auth
     * @name RegisterRegisterApiAuthRegisterPost
     * @summary Register:Register
     * @request POST:/api/auth/register
     */
    registerRegisterApiAuthRegisterPost: (data: UserCreate, params: RequestParams = {}) =>
      this.request<UserRead, ErrorModel | HTTPValidationError>({
        path: `/api/auth/register`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags auth
     * @name UsersCurrentUserApiAuthMeGet
     * @summary Users:Current User
     * @request GET:/api/auth/me
     * @secure
     */
    usersCurrentUserApiAuthMeGet: (params: RequestParams = {}) =>
      this.request<UserRead, void>({
        path: `/api/auth/me`,
        method: "GET",
        secure: true,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags auth
     * @name UsersPatchCurrentUserApiAuthMePatch
     * @summary Users:Patch Current User
     * @request PATCH:/api/auth/me
     * @secure
     */
    usersPatchCurrentUserApiAuthMePatch: (data: UserUpdate, params: RequestParams = {}) =>
      this.request<UserRead, ErrorModel | void | HTTPValidationError>({
        path: `/api/auth/me`,
        method: "PATCH",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags auth
     * @name UsersUserApiAuthIdGet
     * @summary Users:User
     * @request GET:/api/auth/{id}
     * @secure
     */
    usersUserApiAuthIdGet: (id: string, params: RequestParams = {}) =>
      this.request<UserRead, void | HTTPValidationError>({
        path: `/api/auth/${id}`,
        method: "GET",
        secure: true,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags auth
     * @name UsersPatchUserApiAuthIdPatch
     * @summary Users:Patch User
     * @request PATCH:/api/auth/{id}
     * @secure
     */
    usersPatchUserApiAuthIdPatch: (id: string, data: UserUpdate, params: RequestParams = {}) =>
      this.request<UserRead, ErrorModel | void | HTTPValidationError>({
        path: `/api/auth/${id}`,
        method: "PATCH",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @tags auth
     * @name UsersDeleteUserApiAuthIdDelete
     * @summary Users:Delete User
     * @request DELETE:/api/auth/{id}
     * @secure
     */
    usersDeleteUserApiAuthIdDelete: (id: string, params: RequestParams = {}) =>
      this.request<void, void | HTTPValidationError>({
        path: `/api/auth/${id}`,
        method: "DELETE",
        secure: true,
        ...params,
      }),
  };
}
