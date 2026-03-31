import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { IonicModule } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { WorkersPage } from './workers.page';

@NgModule({
  declarations: [WorkersPage],
  imports: [CommonModule, FormsModule, ReactiveFormsModule, IonicModule],
  exports: [WorkersPage],
})
export class WorkersPageModule {}