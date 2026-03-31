import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { IonicModule, LoadingController, ViewWillEnter } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.page.html',
  styleUrls: ['./dashboard.page.scss'],
  standalone: true,
  imports: [IonicModule, CommonModule],
})
export class DashboardPage implements ViewWillEnter {
  stats: Record<string, unknown> | null = null;
  loadError: string | null = null;

  constructor(
    private api: ApiService,
    private router: Router,
    private loadingCtrl: LoadingController
  ) {}

  ionViewWillEnter(): void {
    if (!this.api.getToken()) {
      this.router.navigate(['/login']);
      return;
    }
    this.loadDashboard();
  }

  async loadDashboard(): Promise<void> {
    this.loadError = null;
    const loading = await this.loadingCtrl.create({ message: 'Loading dashboard...' });
    await loading.present();
    this.api.getDashboard().subscribe({
      next: (data) => {
        this.stats = data as Record<string, unknown>;
        loading.dismiss();
      },
      error: (err) => {
        loading.dismiss();
        this.loadError =
          err?.error?.detail || err?.message || 'Could not load dashboard. Check server and login.';
      },
    });
  }

  openModule(key: string): void {
    this.router.navigate(['/module', key]);
  }

  logout(): void {
    this.api.clearToken();
    this.router.navigate(['/login']);
  }

  asPendingList(v: unknown): { worker__name: string; total_pending: number }[] {
    return Array.isArray(v) ? (v as { worker__name: string; total_pending: number }[]) : [];
  }

  asLowStock(v: unknown): { name: string; unit: string; closing_stock: number }[] {
    return Array.isArray(v) ? (v as { name: string; unit: string; closing_stock: number }[]) : [];
  }
}
