import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { LoadingController } from '@ionic/angular';

@Component({
  selector: 'app-workers',
  templateUrl: 'workers.page.html',
  styleUrls: ['workers.page.scss']
})
export class WorkersPage implements OnInit {
  workers: any[] = [];
  isLoading: boolean = true;

  constructor(
    private apiService: ApiService,
    private router: Router,
    private loadingController: LoadingController
  ) {}

  ngOnInit() {
    this.loadWorkers();
  }

  async loadWorkers() {
    this.isLoading = true;
    const loading = await this.loadingController.create({
      message: 'Loading workers...'
    });
    await loading.present();

    this.apiService.getWorkers().subscribe({
      next: async (data) => {
        this.workers = data as any[];
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
