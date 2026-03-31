import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { IonicModule, LoadingController, ToastController, ViewWillEnter } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { firstValueFrom, Observable } from 'rxjs';
import { ApiService } from '../../services/api.service';
import {
  ListItemCardComponent,
  PillBadge,
} from '../../components/list-item-card/list-item-card.component';
import { AddFormSheetComponent } from '../../components/add-form-sheet/add-form-sheet.component';

type ModuleKey =
  | 'workers'
  | 'materials'
  | 'suppliers'
  | 'material-inward'
  | 'work-types'
  | 'distributions'
  | 'work-received'
  | 'pending-work';

@Component({
  selector: 'app-module-list',
  templateUrl: './module-list.page.html',
  styleUrls: ['./module-list.page.scss'],
  standalone: true,
  imports: [
    IonicModule,
    CommonModule,
    FormsModule,
    ListItemCardComponent,
    AddFormSheetComponent,
  ],
})
export class ModuleListPage implements ViewWillEnter {
  key: ModuleKey | null = null;
  title = 'List';
  items: unknown[] = [];
  error: string | null = null;
  /** Client-side filter (all modules). */
  searchQuery = '';

  addModalOpen = false;

  workerForm = { name: '', mobile_number: '', city: '' };
  supplierForm = { name: '', mobile_number: '', city: '' };
  materialForm = { material_name: '', unit: '', description: '' };
  workTypeForm = { name: '' };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: ApiService,
    private loadingCtrl: LoadingController,
    private toastCtrl: ToastController
  ) {}

  ionViewWillEnter(): void {
    if (!this.api.getToken()) {
      this.router.navigate(['/login']);
      return;
    }
    this.addModalOpen = false;
    this.searchQuery = '';
    const k = this.route.snapshot.paramMap.get('key') as ModuleKey;
    this.key = k;
    this.title = this.titleFor(k);
    this.load();
  }

  /** Items after search filter. */
  get filteredItems(): unknown[] {
    const q = (this.searchQuery || '').trim().toLowerCase();
    if (!q) return this.items;
    return this.items.filter((item) => {
      const pillText = [...this.itemPills(item), ...this.itemEndPills(item)]
        .map((p) => p.label)
        .join(' ');
      const blob = [
        this.itemPrimary(item),
        this.itemSubtitle(item),
        pillText,
        ...this.itemSecondaryLines(item),
      ]
        .join(' ')
        .toLowerCase();
      return blob.includes(q);
    });
  }

  get addSheetTitle(): string {
    const map: Partial<Record<ModuleKey, string>> = {
      workers: 'Add worker',
      suppliers: 'Add supplier',
      materials: 'Add material',
      'work-types': 'Add work type',
    };
    return (this.key && map[this.key]) || 'Add';
  }

  get showAddFab(): boolean {
    return this.key !== null;
  }

  get hasAddFormSheet(): boolean {
    return (
      this.key === 'workers' ||
      this.key === 'suppliers' ||
      this.key === 'materials' ||
      this.key === 'work-types'
    );
  }

  private titleFor(k: ModuleKey): string {
    const map: Record<ModuleKey, string> = {
      workers: 'Workers',
      materials: 'Materials',
      suppliers: 'Suppliers',
      'material-inward': 'Material Inward',
      'work-types': 'Work types',
      distributions: 'Work distribution',
      'work-received': 'Work Received',
      'pending-work': 'Pending Work',
    };
    return map[k] || 'List';
  }

  async load(): Promise<void> {
    if (!this.key) return;
    this.error = null;
    const loading = await this.loadingCtrl.create({ message: 'Loading…' });
    await loading.present();
    const req = this.requestFor(this.key);
    if (!req) {
      loading.dismiss();
      this.error = 'Unknown module';
      return;
    }
    req.subscribe({
      next: (res) => {
        this.items = this.unwrapList(res);
        loading.dismiss();
      },
      error: (err) => {
        loading.dismiss();
        this.error = err?.error?.detail || err?.message || 'Failed to load';
      },
    });
  }

  private requestFor(k: ModuleKey): Observable<unknown> | null {
    switch (k) {
      case 'workers':
        return this.api.getWorkers();
      case 'materials':
        return this.api.getMaterials();
      case 'suppliers':
        return this.api.getSuppliers();
      case 'material-inward':
        return this.api.getMaterialInwards();
      case 'work-types':
        return this.api.getWorkTypes();
      case 'distributions':
        return this.api.getWorkDistributions();
      case 'work-received':
        return this.api.getWorkReturns();
      case 'pending-work':
        return this.api.getDashboard();
      default:
        return null;
    }
  }

  private unwrapList(res: unknown): unknown[] {
    if (this.key === 'pending-work' && res && typeof res === 'object') {
      const pending = (res as { pending_work_by_worker?: unknown[] }).pending_work_by_worker;
      return Array.isArray(pending) ? pending : [];
    }
    if (Array.isArray(res)) return res;
    if (res && typeof res === 'object' && Array.isArray((res as { results?: unknown[] }).results)) {
      return (res as { results: unknown[] }).results;
    }
    return [];
  }

  itemPrimary(item: unknown): string {
    if (!item || typeof item !== 'object') return String(item ?? '—');
    const o = item as Record<string, unknown>;
    switch (this.key) {
      case 'workers':
        return String(o['name'] ?? '—');
      case 'materials':
        return String(o['material_name'] ?? '—');
      case 'suppliers':
        return String(o['name'] ?? '—');
      case 'work-types':
        return String(o['name'] ?? o['id'] ?? '—');
      case 'distributions':
        return String(o['worker_name'] ?? 'Worker');
      case 'work-received':
        return `Completed ${o['completed_quantity'] ?? '—'} units`;
      case 'material-inward':
        return String(o['material_name'] ?? 'Material');
      case 'pending-work':
        return String(o['worker__name'] ?? 'Worker');
      default:
        return '—';
    }
  }

  itemSubtitle(item: unknown): string {
    if (!item || typeof item !== 'object') return '';
    const o = item as Record<string, unknown>;
    switch (this.key) {
      case 'workers':
        return o['mobile_number'] ? String(o['mobile_number']) : '';
      case 'suppliers':
        return o['mobile_number'] ? String(o['mobile_number']) : '';
      case 'materials':
        return o['unit'] ? `Unit · ${String(o['unit'])}` : '';
      case 'work-types':
        return '';
      case 'distributions':
        return '';
      case 'work-received':
        return o['return_date'] ? `Return · ${String(o['return_date'])}` : '';
      case 'material-inward':
        return o['supplier_name'] ? `Supplier · ${String(o['supplier_name'])}` : '';
      case 'pending-work':
        return 'Outstanding work';
      default:
        return '';
    }
  }

  itemPills(item: unknown): PillBadge[] {
    if (!item || typeof item !== 'object') return [];
    const o = item as Record<string, unknown>;
    switch (this.key) {
      case 'workers':
        return o['city'] ? [{ label: String(o['city']), tone: 'slate' }] : [];
      case 'materials':
        return [
          {
            label: `Stock ${o['closing_stock'] ?? '—'} ${o['unit'] ?? ''}`.trim(),
            tone: 'sky',
          },
        ];
      case 'suppliers':
        return o['city'] ? [{ label: String(o['city']), tone: 'slate' }] : [];
      case 'work-types':
        return o['id'] != null ? [{ label: `ID ${o['id']}`, tone: 'slate' }] : [];
      case 'distributions':
        return [
          { label: `Lot ${o['lot_size'] ?? '—'}`, tone: 'violet' },
          { label: String(o['work_type_name'] ?? 'Type'), tone: 'slate' },
        ];
      case 'work-received':
        return [{ label: `Dist #${o['distribution'] ?? '—'}`, tone: 'violet' }];
      case 'material-inward':
        return [{ label: `Qty ${o['quantity'] ?? '—'}`, tone: 'sky' }];
      case 'pending-work':
        return [{ label: `Pending ${o['total_pending'] ?? 0}`, tone: 'amber' }];
      default:
        return [];
    }
  }

  itemEndPills(item: unknown): PillBadge[] {
    if (!item || typeof item !== 'object') return [];
    const o = item as Record<string, unknown>;
    switch (this.key) {
      case 'workers': {
        const active = String(o['status'] || '').toLowerCase() === 'active';
        return [{ label: active ? 'Active' : 'Inactive', tone: active ? 'emerald' : 'slate' }];
      }
      case 'materials':
        return [{ label: 'Material', tone: 'violet' }];
      case 'suppliers':
        return [{ label: 'Supplier', tone: 'sky' }];
      case 'work-types':
        return [{ label: 'Type', tone: 'violet' }];
      case 'distributions': {
        const d = String(o['distributed_date'] ?? '').slice(0, 10);
        return d ? [{ label: d, tone: 'sky' }] : [];
      }
      case 'work-received': {
        const d = String(o['return_date'] ?? '').slice(0, 10);
        return d ? [{ label: d, tone: 'sky' }] : [];
      }
      case 'material-inward': {
        const d = String(o['received_date'] ?? '').slice(0, 10);
        return d ? [{ label: d, tone: 'sky' }] : [];
      }
      case 'pending-work':
        return [{ label: 'Open', tone: 'amber' }];
      default:
        return [];
    }
  }

  workerToggleOn(item: unknown): boolean {
    if (!item || typeof item !== 'object') return false;
    return String((item as Record<string, unknown>)['status'] || '').toLowerCase() === 'active';
  }

  itemSecondaryLines(item: unknown): string[] {
    if (!item || typeof item !== 'object') return [];
    const o = item as Record<string, unknown>;
    switch (this.key) {
      case 'workers': {
        const lines: string[] = [];
        if (o['mobile_number']) lines.push(String(o['mobile_number']));
        if (o['city']) lines.push(`City · ${o['city']}`);
        return lines;
      }
      case 'materials':
        return [`Stock · ${o['closing_stock'] ?? '—'} ${o['unit'] ?? ''}`.trim()];
      case 'suppliers': {
        const lines: string[] = [];
        if (o['mobile_number']) lines.push(String(o['mobile_number']));
        if (o['city']) lines.push(String(o['city']));
        return lines;
      }
      case 'work-types':
        return o['id'] != null ? [`ID · ${o['id']}`] : [];
      case 'distributions':
        return [
          String(o['work_type_name'] ?? 'Work type'),
          `Lot size · ${o['lot_size'] ?? '—'}`,
          String(o['distributed_date'] ?? ''),
        ].filter(Boolean);
      case 'work-received':
        return [
          o['return_date'] ? `Date · ${o['return_date']}` : '',
          o['distribution'] != null ? `Distribution #${o['distribution']}` : '',
        ].filter(Boolean);
      case 'material-inward':
        return [
          o['supplier_name'] ? `Supplier · ${o['supplier_name']}` : '',
          `Quantity · ${o['quantity'] ?? '—'}`,
          o['received_date'] ? `Received · ${o['received_date']}` : '',
        ].filter(Boolean);
      case 'pending-work':
        return [`Pending quantity · ${o['total_pending'] ?? 0}`];
      default:
        return [];
    }
  }

  openAddModal(): void {
    if (!this.key) return;
    if (!this.hasAddFormSheet) {
      void this.showToast('Add form for this module will be added next.');
      return;
    }
    this.resetAddForms();
    this.addModalOpen = true;
  }

  private resetAddForms(): void {
    this.workerForm = { name: '', mobile_number: '', city: '' };
    this.supplierForm = { name: '', mobile_number: '', city: '' };
    this.materialForm = { material_name: '', unit: '', description: '' };
    this.workTypeForm = { name: '' };
  }

  async submitAddForm(): Promise<void> {
    if (!this.key) return;
    try {
      switch (this.key) {
        case 'workers':
          if (!this.workerForm.name.trim() || !this.workerForm.mobile_number.trim()) {
            await this.showToast('Name and mobile are required');
            return;
          }
          await firstValueFrom(
            this.api.createWorker({
              name: this.workerForm.name.trim(),
              mobile_number: this.workerForm.mobile_number.trim(),
              city: this.workerForm.city?.trim() || '',
            })
          );
          await this.showToast('Worker added');
          break;
        case 'suppliers':
          if (!this.supplierForm.name.trim() || !this.supplierForm.mobile_number.trim()) {
            await this.showToast('Name and mobile are required');
            return;
          }
          await firstValueFrom(
            this.api.createSupplier({
              name: this.supplierForm.name.trim(),
              mobile_number: this.supplierForm.mobile_number.trim(),
              city: this.supplierForm.city?.trim() || '',
            })
          );
          await this.showToast('Supplier added');
          break;
        case 'materials':
          if (!this.materialForm.material_name.trim() || !this.materialForm.unit.trim()) {
            await this.showToast('Material name and unit are required');
            return;
          }
          await firstValueFrom(
            this.api.createMaterial({
              material_name: this.materialForm.material_name.trim(),
              unit: String(this.materialForm.unit).trim().toLowerCase(),
              description: this.materialForm.description?.trim() || '',
            })
          );
          await this.showToast('Material added');
          break;
        case 'work-types':
          if (!this.workTypeForm.name.trim()) {
            await this.showToast('Name is required');
            return;
          }
          await firstValueFrom(this.api.createWorkType({ name: this.workTypeForm.name.trim() }));
          await this.showToast('Work type added');
          break;
        default:
          return;
      }
      this.addModalOpen = false;
      this.load();
    } catch (e: any) {
      await this.showToast(e?.error?.detail || 'Save failed');
    }
  }

  private async showToast(message: string): Promise<void> {
    const toast = await this.toastCtrl.create({
      message,
      duration: 1800,
      position: 'bottom',
    });
    await toast.present();
  }
}
