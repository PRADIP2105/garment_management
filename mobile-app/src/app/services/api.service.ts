import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, from } from 'rxjs';
import { Capacitor, CapacitorHttp, HttpResponse as CapHttpResponse } from '@capacitor/core';
import { environment } from '../../environments/environment';

/**
 * On native (Android/iOS), uses Capacitor native HTTP so LAN `http://` calls work reliably
 * (WebView XHR/fetch can fail with status 0 even when the server is reachable).
 * Browser / `ionic serve` keeps using Angular HttpClient.
 */
@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private apiUrl: string;
  private accessToken: string | null = null;

  constructor(private http: HttpClient) {
    this.apiUrl = this.resolveApiUrl();
  }

  private resolveApiUrl(): string {
    const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('api_url') : null;
    if (stored?.trim()) {
      return this.normalizeApiBaseUrl(stored);
    }
    return this.normalizeApiBaseUrl(environment.apiUrl);
  }

  normalizeApiBaseUrl(raw: string): string {
    let u = raw.trim().replace(/\/+$/, '');
    if (!u) {
      return environment.apiUrl.replace(/\/+$/, '');
    }
    if (!/^https?:\/\//i.test(u)) {
      u = `http://${u}`;
    }
    if (!/\/api$/i.test(u)) {
      u = `${u}/api`;
    }
    return u;
  }

  setApiUrl(url: string): void {
    this.apiUrl = this.normalizeApiBaseUrl(url);
    localStorage.setItem('api_url', this.apiUrl);
  }

  getApiUrlStatic(): string {
    return this.apiUrl;
  }

  setToken(token: string): void {
    this.accessToken = token;
    localStorage.setItem('token', token);
  }

  getToken(): string | null {
    if (!this.accessToken) {
      this.accessToken = localStorage.getItem('token');
    }
    return this.accessToken;
  }

  clearToken(): void {
    this.accessToken = null;
    localStorage.removeItem('token');
  }

  private getHeaders(): HttpHeaders {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });
    const token = this.getToken();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  }

  private nativeHeaderRecord(auth = true): Record<string, string> {
    const h: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    };
    if (auth) {
      const token = this.getToken();
      if (token) {
        h['Authorization'] = `Bearer ${token}`;
      }
    }
    return h;
  }

  private useNativeHttp(): boolean {
    return typeof Capacitor !== 'undefined' && Capacitor.isNativePlatform();
  }

  private static readonly TIMEOUT = { readTimeout: 25000, connectTimeout: 20000 };

  private rejectNative(res: CapHttpResponse): never {
    const err: any = new Error('HTTP error');
    err.status = res.status;
    let body: unknown = res.data;
    if (typeof body === 'string') {
      try {
        body = JSON.parse(body);
      } catch {
        /* leave as string */
      }
    }
    err.error = body ?? { detail: `HTTP ${res.status}` };
    throw err;
  }

  private makeNetworkError(err: unknown): any {
    const e: any = err;
    const msg = e?.message ?? String(err);
    const out: any = new Error(msg);
    out.status = 0;
    out.error = {
      detail:
        msg.includes('timeout') || msg.includes('Timeout')
          ? 'Connection timed out. Check PC IP, firewall (port 8000), and that Django is running on 0.0.0.0:8000.'
          : `Cannot reach server. ${msg}`,
    };
    return out;
  }

  /** Parse CapacitorHttp body (sometimes a JSON string on Android). */
  private static parseNativeData(data: unknown): unknown {
    if (data == null) return data;
    if (typeof data === 'string') {
      try {
        return JSON.parse(data);
      } catch {
        return data;
      }
    }
    return data;
  }

  /** Public connectivity check — same host as API (`/api/ping/`). */
  ping(): Observable<unknown> {
    const url = this.pingUrl();
    if (this.useNativeHttp()) {
      return from(
        CapacitorHttp.get({
          url,
          headers: { Accept: 'application/json' },
          ...ApiService.TIMEOUT,
        })
          .then((res) => {
            if (res.status >= 400) {
              this.rejectNative(res);
            }
            return ApiService.parseNativeData(res.data);
          })
          .catch((e) => {
            if (e?.status != null) {
              throw e;
            }
            throw this.makeNetworkError(e);
          })
      );
    }
    return this.http.get(url, {
      headers: new HttpHeaders({ Accept: 'application/json' }),
    });
  }

  private pingUrl(): string {
    const b = this.apiUrl.replace(/\/+$/, '');
    return b.endsWith('/api') ? `${b}/ping/` : `${b}/api/ping/`;
  }

  private nativeGet(url: string): Observable<unknown> {
    return from(
      CapacitorHttp.get({
        url,
        headers: this.nativeHeaderRecord(true),
        ...ApiService.TIMEOUT,
      })
        .then((res) => {
          if (res.status >= 400) {
            this.rejectNative(res);
          }
          return ApiService.parseNativeData(res.data);
        })
        .catch((e) => {
          if (e?.status != null) {
            throw e;
          }
          throw this.makeNetworkError(e);
        })
    );
  }

  private nativePost(url: string, data: unknown, auth = true): Observable<unknown> {
    return from(
      CapacitorHttp.post({
        url,
        data,
        headers: this.nativeHeaderRecord(auth),
        ...ApiService.TIMEOUT,
      })
        .then((res) => {
          if (res.status >= 400) {
            this.rejectNative(res);
          }
          return ApiService.parseNativeData(res.data);
        })
        .catch((e) => {
          if (e?.status != null) {
            throw e;
          }
          throw this.makeNetworkError(e);
        })
    );
  }

  private getReq(url: string): Observable<unknown> {
    if (this.useNativeHttp()) {
      return this.nativeGet(url);
    }
    return this.http.get(url, { headers: this.getHeaders() });
  }

  private postReq(url: string, body: unknown): Observable<unknown> {
    if (this.useNativeHttp()) {
      return this.nativePost(url, body, true);
    }
    return this.http.post(url, body, { headers: this.getHeaders() });
  }

  /** Public auth endpoints (no bearer yet). */
  private postPublic(url: string, body: unknown): Observable<unknown> {
    if (this.useNativeHttp()) {
      return this.nativePost(url, body, false);
    }
    return this.http.post(url, body, {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    });
  }

  login(username: string, password: string): Observable<unknown> {
    const url = `${this.apiUrl}/auth/login/`;
    return this.postPublic(url, { username, password });
  }

  register(data: unknown): Observable<unknown> {
    return this.postPublic(`${this.apiUrl}/auth/register/`, data);
  }

  getDashboard(): Observable<unknown> {
    return this.getReq(`${this.apiUrl}/dashboard/summary/`);
  }

  getWorkers(): Observable<unknown> {
    return this.getReq(`${this.apiUrl}/workers/`);
  }

  createWorker(data: {
    name: string;
    mobile_number: string;
    address?: string;
    city?: string;
    skill_type?: string;
    machine_type?: string;
    status?: string;
    language_preference?: string;
  }): Observable<unknown> {
    return this.postReq(`${this.apiUrl}/workers/`, data);
  }

  getMaterials(): Observable<unknown> {
    return this.getReq(`${this.apiUrl}/materials/`);
  }

  createMaterial(data: { material_name: string; unit: string; description?: string }): Observable<unknown> {
    return this.postReq(`${this.apiUrl}/materials/`, data);
  }

  getWorkTypes(): Observable<unknown> {
    return this.getReq(`${this.apiUrl}/work/types/`);
  }

  createWorkType(data: { name: string }): Observable<unknown> {
    return this.postReq(`${this.apiUrl}/work/types/`, data);
  }

  getSuppliers(): Observable<unknown> {
    return this.getReq(`${this.apiUrl}/suppliers/`);
  }

  createSupplier(data: {
    name: string;
    mobile_number: string;
    address?: string;
    city?: string;
  }): Observable<unknown> {
    return this.postReq(`${this.apiUrl}/suppliers/`, data);
  }

  getWorkDistributions(): Observable<unknown> {
    return this.getReq(`${this.apiUrl}/work/distributions/`);
  }

  getMaterialInwards(): Observable<unknown> {
    return this.getReq(`${this.apiUrl}/work/inwards/`);
  }

  getWorkReturns(): Observable<unknown> {
    return this.getReq(`${this.apiUrl}/work/returns/`);
  }

  getWorkReceived(): Observable<unknown> {
    return this.getWorkReturns();
  }
}
