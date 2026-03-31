import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { LoadingController } from '@ionic/angular';

@Component({
  selector: 'app-materials',
  templateUrl: 'materials.page.html',
  styleUrls: ['materials.page.scss']
})
export class MaterialsPage implements OnInit {
  materials: any[] = [];
  isLoading: boolean = true;

  constructor(
    private apiService: ApiService,
    private router: Router,
    private loadingController: LoadingController
  ) {}

  ngOnInit() {
    this.loadMaterials();
  }

  async loadMaterials() {
    this.isLoading = true;
    const loading = await this.loadingController.create({
      message: 'Loading materials...'
    });
    await loading.present();

    this.apiService.getMaterials().subscribe({
      next: async (data) => {
        this.materials = data as any[];
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
