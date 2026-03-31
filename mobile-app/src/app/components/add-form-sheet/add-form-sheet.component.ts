import { Component, EventEmitter, Input, Output } from '@angular/core';
import { IonicModule } from '@ionic/angular';

/**
 * Bottom-anchored modal with header, scrollable form body (projected), and fixed Cancel / Save actions.
 */
@Component({
  selector: 'app-add-form-sheet',
  standalone: true,
  imports: [IonicModule],
  templateUrl: './add-form-sheet.component.html',
  styleUrls: ['./add-form-sheet.component.scss'],
})
export class AddFormSheetComponent {
  @Input() isOpen = false;
  @Output() isOpenChange = new EventEmitter<boolean>();
  @Input({ required: true }) title!: string;
  @Input() saveLabel = 'Save';
  @Output() cancel = new EventEmitter<void>();
  @Output() save = new EventEmitter<void>();

  onBackdropDismiss(): void {
    this.isOpenChange.emit(false);
  }

  onCancel(): void {
    this.cancel.emit();
    this.isOpenChange.emit(false);
  }

  onSave(): void {
    this.save.emit();
  }
}
