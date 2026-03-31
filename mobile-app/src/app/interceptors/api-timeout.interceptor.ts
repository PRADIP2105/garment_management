import { Injectable } from '@angular/core';
import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Observable, TimeoutError, throwError } from 'rxjs';
import { catchError, timeout } from 'rxjs/operators';

/** Prevents endless spinners when the API host is wrong or unreachable (no default HttpClient timeout). */
@Injectable()
export class ApiTimeoutInterceptor implements HttpInterceptor {
  private readonly ms = 20000;

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    return next.handle(req).pipe(
      timeout(this.ms),
      catchError((err: unknown) => {
        if (err instanceof TimeoutError) {
          return throwError(
            () =>
              new HttpErrorResponse({
                status: 0,
                statusText: 'Timeout',
                url: req.url,
                error: {
                  detail:
                    'Connection timed out. Set Server URL to your PC IPv4 from ipconfig (e.g. 192.168.0.109), run: python manage.py runserver 0.0.0.0:8000, and allow port 8000 in Windows Firewall.',
                },
              })
          );
        }
        return throwError(() => err);
      })
    );
  }
}
