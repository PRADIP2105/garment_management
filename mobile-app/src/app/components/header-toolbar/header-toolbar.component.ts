import { Component, Input } from '@angular/core';
import { IonicModule } from '@ionic/angular';

/**
 * Shared app bar: readable title, icon-only back (Material / platform pattern).
 */
@Component({
  selector: 'app-header-toolbar',
  standalone: true,
  imports: [IonicModule],
  templateUrl: './header-toolbar.component.html',
  styleUrls: ['./header-toolbar.component.scss'],
})
export class HeaderToolbarComponent {
  /** Screen title (toolbar) */
  @Input({ required: true }) title!: string;
  /** Ionic router back target */
  @Input() defaultHref = '/dashboard';
}
