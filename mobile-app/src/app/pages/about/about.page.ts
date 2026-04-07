import { Component } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { RouterModule } from '@angular/router';
import { addIcons } from 'ionicons';
import { shirtOutline, shieldCheckmarkOutline, documentTextOutline } from 'ionicons/icons';

@Component({
  selector: 'app-about',
  templateUrl: './about.page.html',
  styleUrls: ['./about.page.scss'],
  standalone: true,
  imports: [IonicModule, RouterModule],
})
export class AboutPage {
  constructor() {
    addIcons({ shirtOutline, shieldCheckmarkOutline, documentTextOutline });
  }
}
