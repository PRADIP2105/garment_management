import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlertController, ModalController, Platform, ToastController } from '@ionic/angular';
import { Subscription } from 'rxjs';
import { ApiService } from './services/api.service';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  styleUrls: ['app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy {
  private lastRootBackHint = 0;
  private backSub?: Subscription;

  constructor(
    private router: Router,
    private platform: Platform,
    private toastCtrl: ToastController,
    private api: ApiService,
    private alertCtrl: AlertController,
    private modalCtrl: ModalController
  ) {}

  ngOnInit() {
    // High priority so we fully control Android back (avoid IonRouterOutlet.pop() exiting WebView).
    this.backSub = this.platform.backButton.subscribeWithPriority(10000, async () => {
      await this.handleHardwareBack();
    });
  }

  private async handleHardwareBack(): Promise<void> {
    const topAlert = await this.alertCtrl.getTop();
    if (topAlert) {
      await topAlert.dismiss();
      return;
    }
    const topModal = await this.modalCtrl.getTop();
    if (topModal) {
      await topModal.dismiss();
      return;
    }

    const path = this.normalizePath(this.router.url);
    const hasToken = !!this.api.getToken();

    if (path.startsWith('/module/')) {
      await this.router.navigateByUrl('/dashboard');
      return;
    }

    if (path === '/register') {
      await this.router.navigateByUrl('/login');
      return;
    }

    if (path === '/dashboard' && hasToken) {
      const now = Date.now();
      if (now - this.lastRootBackHint < 2200) {
        this.lastRootBackHint = 0;
        return;
      }
      this.lastRootBackHint = now;
      const toast = await this.toastCtrl.create({
        message: 'Already on dashboard. Use Home to leave the app.',
        duration: 2200,
        position: 'bottom',
      });
      await toast.present();
      return;
    }

    if (path === '/login' || path === '/') {
      const now = Date.now();
      if (now - this.lastRootBackHint < 2200) {
        this.lastRootBackHint = 0;
        return;
      }
      this.lastRootBackHint = now;
      const toast = await this.toastCtrl.create({
        message: 'Use Home to leave the app.',
        duration: 2200,
        position: 'bottom',
      });
      await toast.present();
      return;
    }

    if (hasToken) {
      await this.router.navigateByUrl('/dashboard');
    } else {
      await this.router.navigateByUrl('/login');
    }
  }

  private normalizePath(url: string): string {
    const p = url.split('?')[0].split('#')[0] || '/';
    if (p === '') return '/';
    return p.startsWith('/') ? p : `/${p}`;
  }

  ngOnDestroy(): void {
    this.backSub?.unsubscribe();
  }
}
