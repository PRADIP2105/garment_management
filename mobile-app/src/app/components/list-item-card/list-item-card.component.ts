import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';

export type BadgeTone = 'slate' | 'emerald' | 'amber' | 'sky' | 'violet' | 'rose';

export interface PillBadge {
  label: string;
  tone: BadgeTone;
}

/**
 * Premium list row: ion-card + ion-item + ion-avatar + pill ion-badges.
 */
@Component({
  selector: 'app-list-item-card',
  standalone: true,
  imports: [CommonModule, IonicModule],
  templateUrl: './list-item-card.component.html',
  styleUrls: ['./list-item-card.component.scss'],
})
export class ListItemCardComponent {
  @Input({ required: true }) title!: string;
  @Input() subtitle = '';
  /** Row of pill badges under subtitle (lot, stock, pending, etc.). */
  @Input() pills: PillBadge[] = [];
  /** Trailing badges (dates, status). */
  @Input() endPills: PillBadge[] = [];
  @Input() showToggle = false;
  @Input() toggleChecked = false;

  get avatarLetter(): string {
    const t = (this.title || '?').trim();
    return (t[0] || '?').toUpperCase();
  }

  get avatarBg(): string {
    let h = 0;
    const s = this.title || '';
    for (let i = 0; i < s.length; i++) {
      h = s.charCodeAt(i) + ((h << 5) - h);
    }
    const hue = Math.abs(h) % 360;
    return `linear-gradient(145deg, hsl(${hue} 85% 72%) 0%, hsl(${(hue + 35) % 360} 80% 68%) 100%)`;
  }

  pillClass(tone: BadgeTone): string {
    return `pill pill-${tone}`;
  }
}
