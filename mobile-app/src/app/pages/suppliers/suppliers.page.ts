import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { LoadingController } from '@ionic/angular';

@Component({
  selector: 'app-suppliers',
  templateUrl: 'suppliers.page.html',
  styleUrls: ['suppliers.page.scss']
})
export class SuppliersPage implements OnInit {
  suppliers: any[] = [];
  isLoading: boolean = true;

  constructor(
    private apiService: ApiService,
    private router: Router,
    private loadingController: LoadingController
  ) {}

  ngOnInit() {
    this.loadSuppliers();
  }

  async loadSuppliers() {
    this.isLoading = true;
    const loading = await this.loadingController.create({
      message: 'Loading suppliers...'
    });
    await loading.present();

    this.apiService.getSuppliers().subscribe({
      next: async (data) => {
        this.suppliers = data as any[];
        await loading.dismiss();
        this.isLoading = false;
      },
      error: async (error) => {
        await loading.dismiss();
        this.isLoading = false;
        if (error.status === 401) {
          this.router.navigate(['/login']);
        }
      }
    });
  }

  goBack() {
    this.router.navigate(['/dashboard']);
  }
}
