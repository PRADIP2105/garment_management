import { Component } from '@angular/core';
import { IonicModule, NavController } from '@ionic/angular';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-page-one',
  templateUrl: './page-one.page.html',
  standalone: true,
  imports: [IonicModule, CommonModule]
})
export class PageOnePage {
  constructor(private navCtrl: NavController) {}

  goToPage(path: string) {
    console.log('Navigating to:', path);
    this.navCtrl.navigateForward(path);
  }
}
