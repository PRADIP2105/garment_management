import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { LoadingController, AlertController, IonicModule } from '@ionic/angular';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { environment } from '../../../environments/environment';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-login',
  templateUrl: 'login.page.html',
  standalone: true,
  imports: [IonicModule, FormsModule, CommonModule]
})
export class LoginPage implements OnInit {
  username = '';
  password = '';
  serverUrl = '';
  isLoading = false;
  showPassword = false;
  showAdvanced = false;

  constructor(
    private apiService: ApiService,
    private router: Router,
    private loadingController: LoadingController,
    private alertController: AlertController
  ) {}

  ngOnInit() {
    if (this.apiService.getToken()) {
      this.router.navigateByUrl('/dashboard', { replaceUrl: true });
      return;
    }
    this.serverUrl = this.apiService.getApiUrlStatic();
  }

  /** Typing 192.168.0.109 fails when this PC has no such address (bind error). Use ipconfig IPv4. */
  get showWrongLanWarning(): boolean {
    return (this.serverUrl || '').includes('192.168.0.109');
  }

  /** Reset saved URL to `environment.apiUrl` (update environment.ts to your PC’s IPv4 from ipconfig). */
  useDefaultServerFromEnv(): void {
    this.apiService.setApiUrl(environment.apiUrl);
    this.serverUrl = this.apiService.getApiUrlStatic();
  }

  async onLogin() {
    const username = (this.username || '').trim();
    const password = (this.password || '').trim();

    if (!username || !password) {
      this.showAlert('Error', 'Please enter username and password');
      return;
    }

    // Update API URL if user changed it in the input field
    if (this.serverUrl) {
      this.apiService.setApiUrl(this.serverUrl.trim());
    }

    this.isLoading = true;
    const loading = await this.loadingController.create({
      message: 'Logging in...'
    });
    await loading.present();

    const currentApiUrl = this.apiService.getApiUrlStatic();

    // Ping first: confirms TCP to PC (firewall / wrong IP) before attempting auth.
    this.apiService
      .ping()
      .pipe(switchMap(() => this.apiService.login(username, password)))
      .subscribe({
        next: async (data: any) => {
          const token = data?.tokens?.access;
          if (!token) {
            await loading.dismiss();
            this.isLoading = false;
            await this.showAlert('Login Failed', 'Unexpected response from server.');
            return;
          }
          this.apiService.setToken(token);
          await loading.dismiss();
          this.isLoading = false;
          this.router.navigateByUrl('/dashboard', { replaceUrl: true });
        },
        error: async (err: any) => {
          await loading.dismiss();
          this.isLoading = false;
          console.error('Login error', err);

          let title = 'Login Failed';
          let message = 'Invalid username or password';
          const isNetwork =
            err?.status === 0 ||
            err?.statusText === 'Timeout' ||
            /failed to fetch|network error|timeout|econnrefused|unreachable/i.test(
              String(err?.message || err?.error || '')
            );
          if (isNetwork) {
            title = 'Cannot reach server';
            message = this.connectionHelpText(currentApiUrl);
          } else if (err?.status === 401 || err?.status === 403) {
            message = err?.error?.detail || 'Invalid username or password';
          } else if (err?.error?.detail) {
            message = err.error.detail;
          }

          await this.showAlert(title, message);
        },
      });
  }

  /** Permanent connectivity checklist (Windows firewall is the usual blocker). */
  private connectionHelpText(apiUrl: string): string {
    return [
      `No response from ${apiUrl}`,
      '',
      'PC (must be running):',
      '• python manage.py runserver 0.0.0.0:8000',
      '   (or run run-django-lan.bat — do NOT use an IP that ipconfig does not show)',
      '• Server URL must be http://YOUR_IP:8000/api where YOUR_IP = ipconfig Wi‑Fi IPv4.',
      '• Windows Firewall: allow inbound TCP 8000 (run repo script scripts/windows-allow-django-8000.ps1 as Admin).',
      '',
      'Phone:',
      '• Same Wi‑Fi as the PC (not mobile data).',
      '• Android: Settings → Network → Private DNS → Automatic or Off.',
      '• Guest Wi‑Fi / AP isolation blocks phone→PC; use main LAN.',
    ].join('\n');
  }

  onRegister() {
    this.router.navigate(['/register']);
  }

  async onForgotPassword() {
    this.showAlert('Info', 'Please contact administrator to reset password.');
  }

  async showAlert(header: string, message: string) {
    const alert = await this.alertController.create({
      header,
      message,
      cssClass: 'alert-message-pre',
      buttons: ['OK'],
    });
    await alert.present();
  }
}
