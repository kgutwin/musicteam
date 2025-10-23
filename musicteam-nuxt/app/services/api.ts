/* eslint-disable */
/* tslint:disable */
// @ts-nocheck
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

/** Comment */
export interface Comment {
  /** Comment */
  comment: string;
  /** Id */
  id: string;
  /**
   * Created On
   * @format date-time
   */
  created_on: string;
  /** Creator Id */
  creator_id: string;
  /** Resource Id */
  resource_id: string;
}

/** CommentList */
export interface CommentList {
  /** Comments */
  comments: Comment[];
}

/** LoginResponse */
export interface LoginResponse {
  /** Token */
  token: string;
}

/** NewComment */
export interface NewComment {
  /** Comment */
  comment: string;
}

/** NewSetlist */
export interface NewSetlist {
  /** Leader Name */
  leader_name: string;
  /**
   * Service Date
   * @default null
   */
  service_date?: string | null;
  /**
   * Tags
   * @default []
   */
  tags?: string[];
}

/** NewSetlistPosition */
export interface NewSetlistPosition {
  /** Index */
  index: number;
  /** Label */
  label: string;
  /** Is Music */
  is_music: boolean;
  /**
   * Presenter
   * @default null
   */
  presenter?: string | null;
  /**
   * Status
   * @default null
   */
  status?: "open" | "in-progress" | "final" | null;
}

/** NewSetlistSheet */
export interface NewSetlistSheet {
  /** Type */
  type:
    | "1:primary"
    | "2:secondary"
    | "3:extra"
    | "4:candidate-high"
    | "5:candidate"
    | "6:candidate-low";
  /** Song Sheet Id */
  song_sheet_id: string;
  /**
   * Setlist Position Id
   * @default null
   */
  setlist_position_id?: string | null;
}

/** NewSetlistTemplate */
export interface NewSetlistTemplate {
  /** Title */
  title: string;
  /**
   * Tags
   * @default []
   */
  tags?: string[];
}

/** NewSetlistTemplatePosition */
export interface NewSetlistTemplatePosition {
  /** Index */
  index: number;
  /** Label */
  label: string;
  /** Is Music */
  is_music: boolean;
  /**
   * Presenter
   * @default null
   */
  presenter?: string | null;
}

/** NewSong */
export interface NewSong {
  /** Title */
  title: string;
  /** Authors */
  authors: string[];
  /** CCLI Number */
  ccli_num: number | null;
  /**
   * Tags
   * @default []
   */
  tags?: string[];
}

/** NewSongSheet */
export interface NewSongSheet {
  /** Type */
  type: "pdf" | "text" | "musicxml";
  /** Key */
  key: string;
  /**
   * Tags
   * @default []
   */
  tags?: string[];
  /** Object Id */
  object_id: string;
}

/** NewSongVersion */
export interface NewSongVersion {
  /** Label */
  label: string;
  /**
   * Verse Order
   * @default null
   */
  verse_order?: string | null;
  /**
   * Lyrics
   * @default null
   */
  lyrics?: string | null;
  /**
   * Tags
   * @default []
   */
  tags?: string[];
}

/** ServerError */
export interface ServerError {
  /** Code */
  Code: string;
  /** Message */
  Message: string;
}

/** Setlist */
export interface Setlist {
  /** Leader Name */
  leader_name: string;
  /**
   * Service Date
   * @default null
   */
  service_date?: string | null;
  /**
   * Tags
   * @default []
   */
  tags?: string[];
  /** Id */
  id: string;
  /**
   * Created On
   * @format date-time
   */
  created_on: string;
  /** Creator Id */
  creator_id: string;
}

/** SetlistList */
export interface SetlistList {
  /** Setlists */
  setlists: Setlist[];
}

/** SetlistPosition */
export interface SetlistPosition {
  /** Index */
  index: number;
  /** Label */
  label: string;
  /** Is Music */
  is_music: boolean;
  /**
   * Presenter
   * @default null
   */
  presenter?: string | null;
  /**
   * Status
   * @default null
   */
  status?: "open" | "in-progress" | "final" | null;
  /** Id */
  id: string;
  /** Setlist Id */
  setlist_id: string;
}

/** SetlistPositionList */
export interface SetlistPositionList {
  /** Positions */
  positions: SetlistPosition[];
}

/** SetlistSheet */
export interface SetlistSheet {
  /** Type */
  type:
    | "1:primary"
    | "2:secondary"
    | "3:extra"
    | "4:candidate-high"
    | "5:candidate"
    | "6:candidate-low";
  /** Song Sheet Id */
  song_sheet_id: string;
  /**
   * Setlist Position Id
   * @default null
   */
  setlist_position_id?: string | null;
  /** Id */
  id: string;
  /** Setlist Id */
  setlist_id: string;
  /** Title */
  title: string;
  /** Key */
  key: string;
}

/** SetlistSheetList */
export interface SetlistSheetList {
  /** Sheets */
  sheets: SetlistSheet[];
}

/** SetlistTemplate */
export interface SetlistTemplate {
  /** Title */
  title: string;
  /**
   * Tags
   * @default []
   */
  tags?: string[];
  /** Id */
  id: string;
  /**
   * Created On
   * @format date-time
   */
  created_on: string;
  /** Creator Id */
  creator_id: string;
}

/** SetlistTemplateList */
export interface SetlistTemplateList {
  /** Templates */
  templates: SetlistTemplate[];
}

/** SetlistTemplatePosition */
export interface SetlistTemplatePosition {
  /** Index */
  index: number;
  /** Label */
  label: string;
  /** Is Music */
  is_music: boolean;
  /**
   * Presenter
   * @default null
   */
  presenter?: string | null;
  /** Id */
  id: string;
  /** Template Id */
  template_id: string;
}

/** SetlistTemplatePositionList */
export interface SetlistTemplatePositionList {
  /** Positions */
  positions: SetlistTemplatePosition[];
}

/** Song */
export interface Song {
  /** Title */
  title: string;
  /** Authors */
  authors: string[];
  /** CCLI Number */
  ccli_num: number | null;
  /**
   * Tags
   * @default []
   */
  tags?: string[];
  /** Id */
  id: string;
  /**
   * Created On
   * @format date-time
   */
  created_on: string;
  /** Creator Id */
  creator_id: string;
}

/** SongList */
export interface SongList {
  /** Songs */
  songs: Song[];
}

/** SongSheet */
export interface SongSheet {
  /** Type */
  type: "pdf" | "text" | "musicxml";
  /** Key */
  key: string;
  /**
   * Tags
   * @default []
   */
  tags?: string[];
  /** Object Id */
  object_id: string;
  /** Id */
  id: string;
  /**
   * Created On
   * @format date-time
   */
  created_on: string;
  /** Creator Id */
  creator_id: string;
  /** Song Version Id */
  song_version_id: string;
}

/** SongSheetList */
export interface SongSheetList {
  /** Song Sheets */
  song_sheets: SongSheet[];
}

/** SongVersion */
export interface SongVersion {
  /** Label */
  label: string;
  /**
   * Verse Order
   * @default null
   */
  verse_order?: string | null;
  /**
   * Lyrics
   * @default null
   */
  lyrics?: string | null;
  /**
   * Tags
   * @default []
   */
  tags?: string[];
  /** Id */
  id: string;
  /**
   * Created On
   * @format date-time
   */
  created_on: string;
  /** Creator Id */
  creator_id: string;
  /** Song Id */
  song_id: string;
}

/** SongVersionList */
export interface SongVersionList {
  /** Song Versions */
  song_versions: SongVersion[];
}

/** UpdateComment */
export interface UpdateComment {
  /**
   * Comment
   * @default null
   */
  comment?: string | null;
}

/** UpdateSetlist */
export interface UpdateSetlist {
  /**
   * Leader Name
   * @default null
   */
  leader_name?: string | null;
  /**
   * Service Date
   * @default null
   */
  service_date?: string | null;
  /**
   * Tags
   * @default null
   */
  tags?: string[] | null;
  /**
   * Music Packet Object Id
   * @default null
   */
  music_packet_object_id?: string | null;
  /**
   * Lyric Packet Object Id
   * @default null
   */
  lyric_packet_object_id?: string | null;
}

/** UpdateSetlistPosition */
export interface UpdateSetlistPosition {
  /**
   * Index
   * @default null
   */
  index?: number | null;
  /**
   * Label
   * @default null
   */
  label?: string | null;
  /**
   * Is Music
   * @default null
   */
  is_music?: boolean | null;
  /**
   * Presenter
   * @default null
   */
  presenter?: string | null;
  /**
   * Status
   * @default null
   */
  status?: "open" | "in-progress" | "final" | null;
}

/** UpdateSetlistSheet */
export interface UpdateSetlistSheet {
  /**
   * Type
   * @default null
   */
  type?:
    | "1:primary"
    | "2:secondary"
    | "3:extra"
    | "4:candidate-high"
    | "5:candidate"
    | "6:candidate-low"
    | null;
  /**
   * Setlist Position Id
   * @default null
   */
  setlist_position_id?: string | null;
}

/** UpdateSetlistTemplate */
export interface UpdateSetlistTemplate {
  /**
   * Title
   * @default null
   */
  title?: string | null;
  /**
   * Tags
   * @default null
   */
  tags?: string[] | null;
}

/** UpdateSetlistTemplatePosition */
export interface UpdateSetlistTemplatePosition {
  /**
   * Index
   * @default null
   */
  index?: number | null;
  /**
   * Label
   * @default null
   */
  label?: string | null;
  /**
   * Is Music
   * @default null
   */
  is_music?: boolean | null;
  /**
   * Presenter
   * @default null
   */
  presenter?: string | null;
}

/** UpdateSong */
export interface UpdateSong {
  /**
   * Title
   * @default null
   */
  title?: string | null;
  /**
   * Authors
   * @default null
   */
  authors?: string[] | null;
  /**
   * CCLI Number
   * @default null
   */
  ccli_num?: number | null;
  /**
   * Tags
   * @default null
   */
  tags?: string[] | null;
}

/** UpdateSongSheet */
export interface UpdateSongSheet {
  /**
   * Key
   * @default null
   */
  key?: string | null;
  /**
   * Tags
   * @default null
   */
  tags?: string[] | null;
  /**
   * Object Id
   * @default null
   */
  object_id?: string | null;
}

/** UpdateSongVersion */
export interface UpdateSongVersion {
  /**
   * Label
   * @default null
   */
  label?: string | null;
  /**
   * Verse Order
   * @default null
   */
  verse_order?: string | null;
  /**
   * Lyrics
   * @default null
   */
  lyrics?: string | null;
  /**
   * Tags
   * @default null
   */
  tags?: string[] | null;
}

/** User */
export interface User {
  /** Id */
  id: string;
  /** Name */
  name: string;
  /** Provider Id */
  provider_id: string;
  /** Email */
  email: string;
  /** Picture */
  picture: string;
  /** Role */
  role: "admin" | "manager" | "leader" | "viewer" | "pending" | "inactive";
  /**
   * Api Key
   * @default null
   */
  api_key?: string | null;
}

/** UserList */
export interface UserList {
  /** Users */
  users: User[];
}

export type QueryParamsType = Record<string | number, any>;
export type ResponseFormat = keyof Omit<Body, "body" | "bodyUsed">;

export interface FullRequestParams extends Omit<RequestInit, "body"> {
  /** set parameter to `true` for call `securityWorker` for this request */
  secure?: boolean;
  /** request path */
  path: string;
  /** content type of request body */
  type?: ContentType;
  /** query params */
  query?: QueryParamsType;
  /** format of response (i.e. response.json() -> format: "json") */
  format?: ResponseFormat;
  /** request body */
  body?: unknown;
  /** base url */
  baseUrl?: string;
  /** request cancellation token */
  cancelToken?: CancelToken;
}

export type RequestParams = Omit<
  FullRequestParams,
  "body" | "method" | "query" | "path"
>;

export interface ApiConfig<SecurityDataType = unknown> {
  baseUrl?: string;
  baseApiParams?: Omit<RequestParams, "baseUrl" | "cancelToken" | "signal">;
  securityWorker?: (
    securityData: SecurityDataType | null,
  ) => Promise<RequestParams | void> | RequestParams | void;
  customFetch?: typeof fetch;
}

export interface HttpResponse<D extends unknown, E extends unknown = unknown>
  extends Response {
  data: D;
  error: E;
}

type CancelToken = Symbol | string | number;

export enum ContentType {
  Json = "application/json",
  JsonApi = "application/vnd.api+json",
  FormData = "multipart/form-data",
  UrlEncoded = "application/x-www-form-urlencoded",
  Text = "text/plain",
}

export class HttpClient<SecurityDataType = unknown> {
  public baseUrl: string = "";
  private securityData: SecurityDataType | null = null;
  private securityWorker?: ApiConfig<SecurityDataType>["securityWorker"];
  private abortControllers = new Map<CancelToken, AbortController>();
  private customFetch = (...fetchParams: Parameters<typeof fetch>) =>
    fetch(...fetchParams);

  private baseApiParams: RequestParams = {
    credentials: "same-origin",
    headers: {},
    redirect: "follow",
    referrerPolicy: "no-referrer",
  };

  constructor(apiConfig: ApiConfig<SecurityDataType> = {}) {
    Object.assign(this, apiConfig);
  }

  public setSecurityData = (data: SecurityDataType | null) => {
    this.securityData = data;
  };

  protected encodeQueryParam(key: string, value: any) {
    const encodedKey = encodeURIComponent(key);
    return `${encodedKey}=${encodeURIComponent(typeof value === "number" ? value : `${value}`)}`;
  }

  protected addQueryParam(query: QueryParamsType, key: string) {
    return this.encodeQueryParam(key, query[key]);
  }

  protected addArrayQueryParam(query: QueryParamsType, key: string) {
    const value = query[key];
    return value.map((v: any) => this.encodeQueryParam(key, v)).join("&");
  }

  protected toQueryString(rawQuery?: QueryParamsType): string {
    const query = rawQuery || {};
    const keys = Object.keys(query).filter(
      (key) => "undefined" !== typeof query[key],
    );
    return keys
      .map((key) =>
        Array.isArray(query[key])
          ? this.addArrayQueryParam(query, key)
          : this.addQueryParam(query, key),
      )
      .join("&");
  }

  protected addQueryParams(rawQuery?: QueryParamsType): string {
    const queryString = this.toQueryString(rawQuery);
    return queryString ? `?${queryString}` : "";
  }

  private contentFormatters: Record<ContentType, (input: any) => any> = {
    [ContentType.Json]: (input: any) =>
      input !== null && (typeof input === "object" || typeof input === "string")
        ? JSON.stringify(input)
        : input,
    [ContentType.JsonApi]: (input: any) =>
      input !== null && (typeof input === "object" || typeof input === "string")
        ? JSON.stringify(input)
        : input,
    [ContentType.Text]: (input: any) =>
      input !== null && typeof input !== "string"
        ? JSON.stringify(input)
        : input,
    [ContentType.FormData]: (input: any) => {
      if (input instanceof FormData) {
        return input;
      }

      return Object.keys(input || {}).reduce((formData, key) => {
        const property = input[key];
        formData.append(
          key,
          property instanceof Blob
            ? property
            : typeof property === "object" && property !== null
              ? JSON.stringify(property)
              : `${property}`,
        );
        return formData;
      }, new FormData());
    },
    [ContentType.UrlEncoded]: (input: any) => this.toQueryString(input),
  };

  protected mergeRequestParams(
    params1: RequestParams,
    params2?: RequestParams,
  ): RequestParams {
    return {
      ...this.baseApiParams,
      ...params1,
      ...(params2 || {}),
      headers: {
        ...(this.baseApiParams.headers || {}),
        ...(params1.headers || {}),
        ...((params2 && params2.headers) || {}),
      },
    };
  }

  protected createAbortSignal = (
    cancelToken: CancelToken,
  ): AbortSignal | undefined => {
    if (this.abortControllers.has(cancelToken)) {
      const abortController = this.abortControllers.get(cancelToken);
      if (abortController) {
        return abortController.signal;
      }
      return void 0;
    }

    const abortController = new AbortController();
    this.abortControllers.set(cancelToken, abortController);
    return abortController.signal;
  };

  public abortRequest = (cancelToken: CancelToken) => {
    const abortController = this.abortControllers.get(cancelToken);

    if (abortController) {
      abortController.abort();
      this.abortControllers.delete(cancelToken);
    }
  };

  public request = async <T = any, E = any>({
    body,
    secure,
    path,
    type,
    query,
    format,
    baseUrl,
    cancelToken,
    ...params
  }: FullRequestParams): Promise<HttpResponse<T, E>> => {
    const secureParams =
      ((typeof secure === "boolean" ? secure : this.baseApiParams.secure) &&
        this.securityWorker &&
        (await this.securityWorker(this.securityData))) ||
      {};
    const requestParams = this.mergeRequestParams(params, secureParams);
    const queryString = query && this.toQueryString(query);
    const payloadFormatter = this.contentFormatters[type || ContentType.Json];
    const responseFormat = format || requestParams.format;

    return this.customFetch(
      `${baseUrl || this.baseUrl || ""}${path}${queryString ? `?${queryString}` : ""}`,
      {
        ...requestParams,
        headers: {
          ...(requestParams.headers || {}),
          ...(type && type !== ContentType.FormData
            ? { "Content-Type": type }
            : {}),
        },
        signal:
          (cancelToken
            ? this.createAbortSignal(cancelToken)
            : requestParams.signal) || null,
        body:
          typeof body === "undefined" || body === null
            ? null
            : payloadFormatter(body),
      },
    ).then(async (response) => {
      const r = response as HttpResponse<T, E>;
      r.data = null as unknown as T;
      r.error = null as unknown as E;

      const responseToParse = responseFormat ? response.clone() : response;
      const data = !responseFormat
        ? r
        : await responseToParse[responseFormat]()
            .then((data) => {
              if (r.ok) {
                r.data = data;
              } else {
                r.error = data;
              }
              return r;
            })
            .catch((e) => {
              r.error = e;
              return r;
            });

      if (cancelToken) {
        this.abortControllers.delete(cancelToken);
      }

      if (!response.ok) throw data;
      return data;
    });
  };
}

/**
 * @title MusicTeam
 * @version 0.1.0
 *
 * a music management tool
 */
export class Api<
  SecurityDataType extends unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name Index
   * @request GET:/
   */
  index = (params: RequestParams = {}) =>
    this.request<object, ServerError>({
      path: `/`,
      method: "GET",
      format: "json",
      ...params,
    });

  admin = {
    /**
     * No description
     *
     * @name DbUpgrade
     * @request POST:/admin/db-upgrade/{ver}
     */
    dbUpgrade: (ver: string, params: RequestParams = {}) =>
      this.request<object, ServerError>({
        path: `/admin/db-upgrade/${ver}`,
        method: "POST",
        format: "json",
        ...params,
      }),
  };
  auth = {
    /**
     * No description
     *
     * @name AuthCallback
     * @request GET:/auth/callback
     */
    authCallback: (params: RequestParams = {}) =>
      this.request<any, ServerError>({
        path: `/auth/callback`,
        method: "GET",
        ...params,
      }),

    /**
     * No description
     *
     * @name AuthGoogle
     * @request GET:/auth/google
     */
    authGoogle: (params: RequestParams = {}) =>
      this.request<any, ServerError>({
        path: `/auth/google`,
        method: "GET",
        ...params,
      }),

    /**
     * No description
     *
     * @name AuthLogin
     * @request POST:/auth/login
     */
    authLogin: (params: RequestParams = {}) =>
      this.request<LoginResponse, ServerError>({
        path: `/auth/login`,
        method: "POST",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name AuthLogout
     * @request POST:/auth/logout
     */
    authLogout: (params: RequestParams = {}) =>
      this.request<any, ServerError>({
        path: `/auth/logout`,
        method: "POST",
        ...params,
      }),

    /**
     * No description
     *
     * @name AuthSession
     * @request GET:/auth/session
     */
    authSession: (params: RequestParams = {}) =>
      this.request<User, ServerError>({
        path: `/auth/session`,
        method: "GET",
        format: "json",
        ...params,
      }),
  };
  comments = {
    /**
     * No description
     *
     * @name ListComments
     * @request GET:/comments/{resource_id}
     */
    listComments: (resourceId: string, params: RequestParams = {}) =>
      this.request<CommentList, ServerError>({
        path: `/comments/${resourceId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name NewComment
     * @request POST:/comments/{resource_id}
     */
    newComment: (
      resourceId: string,
      data: NewComment,
      params: RequestParams = {},
    ) =>
      this.request<Comment, ServerError>({
        path: `/comments/${resourceId}`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetComment
     * @request GET:/comments/{resource_id}/{comment_id}
     */
    getComment: (
      resourceId: string,
      commentId: string,
      params: RequestParams = {},
    ) =>
      this.request<Comment, ServerError>({
        path: `/comments/${resourceId}/${commentId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name UpdateComment
     * @request PUT:/comments/{resource_id}/{comment_id}
     */
    updateComment: (
      resourceId: string,
      commentId: string,
      data: UpdateComment,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/comments/${resourceId}/${commentId}`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        ...params,
      }),

    /**
     * No description
     *
     * @name DeleteComment
     * @request DELETE:/comments/{resource_id}/{comment_id}
     */
    deleteComment: (
      resourceId: string,
      commentId: string,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/comments/${resourceId}/${commentId}`,
        method: "DELETE",
        ...params,
      }),
  };
  setlistTemplates = {
    /**
     * No description
     *
     * @name ListSetlistTemplates
     * @request GET:/setlistTemplates
     */
    listSetlistTemplates: (params: RequestParams = {}) =>
      this.request<SetlistTemplateList, ServerError>({
        path: `/setlistTemplates`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name NewSetlistTemplate
     * @request POST:/setlistTemplates
     */
    newSetlistTemplate: (
      data: NewSetlistTemplate,
      params: RequestParams = {},
    ) =>
      this.request<SetlistTemplate, ServerError>({
        path: `/setlistTemplates`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetSetlistTemplate
     * @request GET:/setlistTemplates/{template_id}
     */
    getSetlistTemplate: (templateId: string, params: RequestParams = {}) =>
      this.request<SetlistTemplate, ServerError>({
        path: `/setlistTemplates/${templateId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name UpdateSetlistTemplate
     * @request PUT:/setlistTemplates/{template_id}
     */
    updateSetlistTemplate: (
      templateId: string,
      data: UpdateSetlistTemplate,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/setlistTemplates/${templateId}`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        ...params,
      }),

    /**
     * No description
     *
     * @name DeleteSetlistTemplate
     * @request DELETE:/setlistTemplates/{template_id}
     */
    deleteSetlistTemplate: (templateId: string, params: RequestParams = {}) =>
      this.request<any, ServerError>({
        path: `/setlistTemplates/${templateId}`,
        method: "DELETE",
        ...params,
      }),

    /**
     * No description
     *
     * @name ListSetlistTemplatePositions
     * @request GET:/setlistTemplates/{template_id}/pos
     */
    listSetlistTemplatePositions: (
      templateId: string,
      params: RequestParams = {},
    ) =>
      this.request<SetlistTemplatePositionList, ServerError>({
        path: `/setlistTemplates/${templateId}/pos`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name NewSetlistTemplatePosition
     * @request POST:/setlistTemplates/{template_id}/pos
     */
    newSetlistTemplatePosition: (
      templateId: string,
      data: NewSetlistTemplatePosition,
      params: RequestParams = {},
    ) =>
      this.request<SetlistTemplatePosition, ServerError>({
        path: `/setlistTemplates/${templateId}/pos`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetSetlistTemplatePosition
     * @request GET:/setlistTemplates/{template_id}/pos/{position_id}
     */
    getSetlistTemplatePosition: (
      templateId: string,
      positionId: string,
      params: RequestParams = {},
    ) =>
      this.request<SetlistTemplatePosition, ServerError>({
        path: `/setlistTemplates/${templateId}/pos/${positionId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name UpdateSetlistTemplatePosition
     * @request PUT:/setlistTemplates/{template_id}/pos/{position_id}
     */
    updateSetlistTemplatePosition: (
      templateId: string,
      positionId: string,
      data: UpdateSetlistTemplatePosition,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/setlistTemplates/${templateId}/pos/${positionId}`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        ...params,
      }),

    /**
     * No description
     *
     * @name DeleteSetlistTemplatePosition
     * @request DELETE:/setlistTemplates/{template_id}/pos/{position_id}
     */
    deleteSetlistTemplatePosition: (
      templateId: string,
      positionId: string,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/setlistTemplates/${templateId}/pos/${positionId}`,
        method: "DELETE",
        ...params,
      }),
  };
  setlists = {
    /**
     * No description
     *
     * @name ListSetlists
     * @request GET:/setlists
     */
    listSetlists: (params: RequestParams = {}) =>
      this.request<SetlistList, ServerError>({
        path: `/setlists`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name NewSetlist
     * @request POST:/setlists
     */
    newSetlist: (data: NewSetlist, params: RequestParams = {}) =>
      this.request<Setlist, ServerError>({
        path: `/setlists`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetSetlist
     * @request GET:/setlists/{setlist_id}
     */
    getSetlist: (setlistId: string, params: RequestParams = {}) =>
      this.request<Setlist, ServerError>({
        path: `/setlists/${setlistId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name UpdateSetlist
     * @request PUT:/setlists/{setlist_id}
     */
    updateSetlist: (
      setlistId: string,
      data: UpdateSetlist,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/setlists/${setlistId}`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        ...params,
      }),

    /**
     * No description
     *
     * @name DeleteSetlist
     * @request DELETE:/setlists/{setlist_id}
     */
    deleteSetlist: (setlistId: string, params: RequestParams = {}) =>
      this.request<any, ServerError>({
        path: `/setlists/${setlistId}`,
        method: "DELETE",
        ...params,
      }),

    /**
     * No description
     *
     * @name ListSetlistPositions
     * @request GET:/setlists/{setlist_id}/pos
     */
    listSetlistPositions: (setlistId: string, params: RequestParams = {}) =>
      this.request<SetlistPositionList, ServerError>({
        path: `/setlists/${setlistId}/pos`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name NewSetlistPosition
     * @request POST:/setlists/{setlist_id}/pos
     */
    newSetlistPosition: (
      setlistId: string,
      data: NewSetlistPosition,
      params: RequestParams = {},
    ) =>
      this.request<SetlistPosition, ServerError>({
        path: `/setlists/${setlistId}/pos`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetSetlistPosition
     * @request GET:/setlists/{setlist_id}/pos/{position_id}
     */
    getSetlistPosition: (
      setlistId: string,
      positionId: string,
      params: RequestParams = {},
    ) =>
      this.request<SetlistPosition, ServerError>({
        path: `/setlists/${setlistId}/pos/${positionId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name UpdateSetlistPosition
     * @request PUT:/setlists/{setlist_id}/pos/{position_id}
     */
    updateSetlistPosition: (
      setlistId: string,
      positionId: string,
      data: UpdateSetlistPosition,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/setlists/${setlistId}/pos/${positionId}`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        ...params,
      }),

    /**
     * No description
     *
     * @name DeleteSetlistPosition
     * @request DELETE:/setlists/{setlist_id}/pos/{position_id}
     */
    deleteSetlistPosition: (
      setlistId: string,
      positionId: string,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/setlists/${setlistId}/pos/${positionId}`,
        method: "DELETE",
        ...params,
      }),

    /**
     * No description
     *
     * @name ListSetlistSheets
     * @request GET:/setlists/{setlist_id}/sheets
     */
    listSetlistSheets: (setlistId: string, params: RequestParams = {}) =>
      this.request<SetlistSheetList, ServerError>({
        path: `/setlists/${setlistId}/sheets`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name NewSetlistSheet
     * @request POST:/setlists/{setlist_id}/sheets
     */
    newSetlistSheet: (
      setlistId: string,
      data: NewSetlistSheet,
      params: RequestParams = {},
    ) =>
      this.request<SetlistSheet, ServerError>({
        path: `/setlists/${setlistId}/sheets`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetSetlistSheet
     * @request GET:/setlists/{setlist_id}/sheets/{sheet_id}
     */
    getSetlistSheet: (
      setlistId: string,
      sheetId: string,
      params: RequestParams = {},
    ) =>
      this.request<SetlistSheet, ServerError>({
        path: `/setlists/${setlistId}/sheets/${sheetId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name UpdateSetlistSheet
     * @request PUT:/setlists/{setlist_id}/sheets/{sheet_id}
     */
    updateSetlistSheet: (
      setlistId: string,
      sheetId: string,
      data: UpdateSetlistSheet,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/setlists/${setlistId}/sheets/${sheetId}`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        ...params,
      }),

    /**
     * No description
     *
     * @name DeleteSetlistSheet
     * @request DELETE:/setlists/{setlist_id}/sheets/{sheet_id}
     */
    deleteSetlistSheet: (
      setlistId: string,
      sheetId: string,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/setlists/${setlistId}/sheets/${sheetId}`,
        method: "DELETE",
        ...params,
      }),
  };
  songs = {
    /**
     * No description
     *
     * @name ListSongs
     * @request GET:/songs
     */
    listSongs: (params: RequestParams = {}) =>
      this.request<SongList, ServerError>({
        path: `/songs`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name NewSong
     * @request POST:/songs
     */
    newSong: (data: NewSong, params: RequestParams = {}) =>
      this.request<Song, ServerError>({
        path: `/songs`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetSong
     * @request GET:/songs/{song_id}
     */
    getSong: (songId: string, params: RequestParams = {}) =>
      this.request<Song, ServerError>({
        path: `/songs/${songId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name UpdateSong
     * @request PUT:/songs/{song_id}
     */
    updateSong: (
      songId: string,
      data: UpdateSong,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/songs/${songId}`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        ...params,
      }),

    /**
     * No description
     *
     * @name DeleteSong
     * @request DELETE:/songs/{song_id}
     */
    deleteSong: (songId: string, params: RequestParams = {}) =>
      this.request<any, ServerError>({
        path: `/songs/${songId}`,
        method: "DELETE",
        ...params,
      }),

    /**
     * No description
     *
     * @name ListSongVersions
     * @request GET:/songs/{song_id}/versions
     */
    listSongVersions: (songId: string, params: RequestParams = {}) =>
      this.request<SongVersionList, ServerError>({
        path: `/songs/${songId}/versions`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name NewSongVersion
     * @request POST:/songs/{song_id}/versions
     */
    newSongVersion: (
      songId: string,
      data: NewSongVersion,
      params: RequestParams = {},
    ) =>
      this.request<SongVersion, ServerError>({
        path: `/songs/${songId}/versions`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetSongVersion
     * @request GET:/songs/{song_id}/versions/{version_id}
     */
    getSongVersion: (
      songId: string,
      versionId: string,
      params: RequestParams = {},
    ) =>
      this.request<SongVersion, ServerError>({
        path: `/songs/${songId}/versions/${versionId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name UpdateSongVersion
     * @request PUT:/songs/{song_id}/versions/{version_id}
     */
    updateSongVersion: (
      songId: string,
      versionId: string,
      data: UpdateSongVersion,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/songs/${songId}/versions/${versionId}`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        ...params,
      }),

    /**
     * No description
     *
     * @name DeleteSongVersion
     * @request DELETE:/songs/{song_id}/versions/{version_id}
     */
    deleteSongVersion: (
      songId: string,
      versionId: string,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/songs/${songId}/versions/${versionId}`,
        method: "DELETE",
        ...params,
      }),

    /**
     * No description
     *
     * @name ListSongSheets
     * @request GET:/songs/{song_id}/versions/{version_id}/sheets
     */
    listSongSheets: (
      songId: string,
      versionId: string,
      params: RequestParams = {},
    ) =>
      this.request<SongSheetList, ServerError>({
        path: `/songs/${songId}/versions/${versionId}/sheets`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name NewSongSheet
     * @request POST:/songs/{song_id}/versions/{version_id}/sheets
     */
    newSongSheet: (
      songId: string,
      versionId: string,
      data: NewSongSheet,
      params: RequestParams = {},
    ) =>
      this.request<SongSheet, ServerError>({
        path: `/songs/${songId}/versions/${versionId}/sheets`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetSongSheet
     * @request GET:/songs/{song_id}/versions/{version_id}/sheets/{sheet_id}
     */
    getSongSheet: (
      songId: string,
      versionId: string,
      sheetId: string,
      params: RequestParams = {},
    ) =>
      this.request<SongSheet, ServerError>({
        path: `/songs/${songId}/versions/${versionId}/sheets/${sheetId}`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name UpdateSongSheet
     * @request PUT:/songs/{song_id}/versions/{version_id}/sheets/{sheet_id}
     */
    updateSongSheet: (
      songId: string,
      versionId: string,
      sheetId: string,
      data: UpdateSongSheet,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/songs/${songId}/versions/${versionId}/sheets/${sheetId}`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        ...params,
      }),

    /**
     * No description
     *
     * @name DeleteSongSheet
     * @request DELETE:/songs/{song_id}/versions/{version_id}/sheets/{sheet_id}
     */
    deleteSongSheet: (
      songId: string,
      versionId: string,
      sheetId: string,
      params: RequestParams = {},
    ) =>
      this.request<any, ServerError>({
        path: `/songs/${songId}/versions/${versionId}/sheets/${sheetId}`,
        method: "DELETE",
        ...params,
      }),
  };
  users = {
    /**
     * No description
     *
     * @name ListUsers
     * @request GET:/users
     */
    listUsers: (params: RequestParams = {}) =>
      this.request<UserList, ServerError>({
        path: `/users`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * No description
     *
     * @name GetUser
     * @request GET:/users/{user_id}
     */
    getUser: (userId: string, params: RequestParams = {}) =>
      this.request<User, ServerError>({
        path: `/users/${userId}`,
        method: "GET",
        format: "json",
        ...params,
      }),
  };
}
