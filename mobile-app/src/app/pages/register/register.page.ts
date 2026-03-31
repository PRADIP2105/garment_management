import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { IonicModule, AlertController, LoadingController } from '@ionic/angular';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.page.html',
  styleUrls: ['./register.page.scss'],
  standalone: true,
  imports: [IonicModule, FormsModule, CommonModule],
})
export class RegisterPage {
  registerData = {
    username: '',
    email: '',
    password: '',
    confirm_password: '',
    company_name: '',
    company_address: '',
    company_city: '',
    company_mobile: '',
  };

  isLoading = false;
  showPassword = false;

  constructor(
    private router: Router,
    private api: ApiService,
    private alertCtrl: AlertController,
    private loadingCtrl: LoadingController
  ) {}

  async onRegister() {
    const d = this.registerData;

    // Basic validation
    if (!d.username.trim() || !d.email.trim() || !d.password.trim()) {
      this.showAlert('Missing Fields', 'Username, email, and password are required.');
      return;
    }
    if (d.password !== d.confirm_password) {
      this.showAlert('Password Mismatch', 'Password and confirm password do not match.');
      return;
    }
    if (!d.company_name.trim()) {
      this.showAlert('Missing Fields', 'Company name is required.');
      return;
    }

    this.isLoading = true;
    const loading = await this.loadingCtrl.create({ message: 'Creating account...' });
    await loading.present();

    this.api.register(d).subscribe({
      next: async () => {
        await loading.dismiss();
        this.isLoading = false;
        const alert = await this.alertCtrl.create({
          header: 'Success',
          message: 'Account created successfully! Please sign in.',
          buttons: [
            {
              text: 'Sign In',
              handler: () => this.router.navigate(['/login']),
            },
          ],
        });
        await alert.present();
      },
      error: async (err: any) => {
        await loading.dismiss();
        this.isLoading = false;
        const message =
          err?.error?.detail ||
          err?.error?.username?.[0] ||
          err?.error?.email?.[0] ||
          err?.message ||
          'Registration failed. Please try again.';
        this.showAlert('Registration Failed', message);
      },
    });
  }

  onLogin() {
    this.router.navigate(['/login']);
  }

  private async showAlert(header: string, message: string) {
    const alert = await this.alertCtrl.create({
      header,
      message,
      buttons: ['OK'],
    });
    await alert.present();
  }
}
