import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { IonicModule, LoadingController, NavController, ToastController, ViewWillEnter } from '@ionic/angular';
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
  imports: [IonicModule, CommonModule, FormsModule, ListItemCardComponent, AddFormSheetComponent],
})
export class ModuleListPage implements ViewWillEnter {
  key: ModuleKey | null = null;
  title = 'List';
  items: unknown[] = [];
  error: string | null = null;
  searchQuery = '';
  addModalOpen = false;

  // Lookup lists for dropdowns
  workersList: { id: number; name: string }[] = [];
  suppliersList: { id: number; name: string }[] = [];
  materialsList: { id: number; material_name: string; unit: string }[] = [];
  workTypesList: { id: number; name: string }[] = [];
  distributionsList: { id: number; worker_name?: string; work_type_name?: string; lot_size?: number; distributed_date?: string }[] = [];

  // Forms
  workerForm = { name: '', mobile_number: '', city: '', skill_type: 'stitching', machine_type: 'simple' };
  supplierForm = { name: '', mobile_number: '', city: '' };
  materialForm = { material_name: '', unit: 'meter', description: '' };
  workTypeForm = { name: '' };
  inwardForm = { supplier: 0, material: 0, quantity: '', received_date: '', remarks: '' };
  distributionForm = { worker: 0, work_type: 0, lot_size: '', distributed_date: '', expected_return_date: '' };
  workReceivedForm = { distribution: 0, received_quantity: '', received_date: '', remarks: '' };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: ApiService,
    private loadingCtrl: LoadingController,
    private toastCtrl: ToastController,
    private navCtrl: NavController
  ) {}

  goBack(): void {
    this.navCtrl.back();
  }

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
      ].join(' ').toLowerCase();
      return blob.includes(q);
    });
  }

  get addSheetTitle(): string {
    const map: Partial<Record<ModuleKey, string>> = {
      workers: 'Add worker',
      suppliers: 'Add supplier',
      materials: 'Add material',
      'work-types': 'Add work type',
      'material-inward': 'Add material inward',
      distributions: 'Add distribution',
      'work-received': 'Record work received',
    };
    return (this.key && map[this.key]) || 'Add';
  }

  get showAddFab(): boolean {
    return this.key !== null && this.key !== 'pending-work';
  }

  get hasAddFormSheet(): boolean {
    return (
      this.key === 'workers' ||
      this.key === 'suppliers' ||
      this.key === 'materials' ||
      this.key === 'work-types' ||
      this.key === 'material-inward' ||
      this.key === 'distributions' ||
      this.key === 'work-received'
    );
  }

  private titleFor(k: ModuleKey): string {
    const map: Record<ModuleKey, string> = {
      workers: 'Workers',
      materials: 'Materials',
      suppliers: 'Suppliers',
      'material-inward': 'Material Inward',
      'work-types': 'Work Types',
      distributions: 'Work Distribution',
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
      error: (err: any) => {
        loading.dismiss();
        this.error = err?.error?.detail || err?.message || 'Failed to load';
      },
    });
  }

  private requestFor(k: ModuleKey): Observable<unknown> | null {
    switch (k) {
      case 'workers': return this.api.getWorkers();
      case 'materials': return this.api.getMaterials();
      case 'suppliers': return this.api.getSuppliers();
      case 'material-inward': return this.api.getMaterialInwards();
      case 'work-types': return this.api.getWorkTypes();
      case 'distributions': return this.api.getWorkDistributions();
      case 'work-received': return this.api.getWorkReturns();
      case 'pending-work': return this.api.getDashboard();
      default: return null;
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
      case 'workers': return String(o['name'] ?? '—');
      case 'materials': return String(o['material_name'] ?? '—');
      case 'suppliers': return String(o['name'] ?? '—');
      case 'work-types': return String(o['name'] ?? o['id'] ?? '—');
      case 'distributions': return String(o['worker_name'] ?? 'Worker');
      case 'work-received': return `Received ${o['completed_quantity'] ?? o['received_quantity'] ?? '—'} units`;
      case 'material-inward': return String(o['material_name'] ?? 'Material');
      case 'pending-work': return String(o['worker__name'] ?? 'Worker');
      default: return '—';
    }
  }

  itemSubtitle(item: unknown): string {
    if (!item || typeof item !== 'object') return '';
    const o = item as Record<string, unknown>;
    switch (this.key) {
      case 'workers': return o['mobile_number'] ? String(o['mobile_number']) : '';
      case 'suppliers': return o['mobile_number'] ? String(o['mobile_number']) : '';
      case 'materials': return o['unit'] ? `Unit · ${String(o['unit'])}` : '';
      case 'work-types': return '';
      case 'distributions': return o['work_type_name'] ? String(o['work_type_name']) : '';
      case 'work-received': return o['return_date'] ? `Date · ${String(o['return_date'])}` : '';
      case 'material-inward': return o['supplier_name'] ? `Supplier · ${String(o['supplier_name'])}` : '';
      case 'pending-work': return 'Outstanding work';
      default: return '';
    }
  }

  itemPills(item: unknown): PillBadge[] {
    if (!item || typeof item !== 'object') return [];
    const o = item as Record<string, unknown>;
    switch (this.key) {
      case 'workers': return o['city'] ? [{ label: String(o['city']), tone: 'slate' }] : [];
      case 'materials': return [{ label: `Stock ${o['closing_stock'] ?? '—'} ${o['unit'] ?? ''}`.trim(), tone: 'sky' }];
      case 'suppliers': return o['city'] ? [{ label: String(o['city']), tone: 'slate' }] : [];
      case 'work-types': return o['id'] != null ? [{ label: `ID ${o['id']}`, tone: 'slate' }] : [];
      case 'distributions': return [
        { label: `Lot ${o['lot_size'] ?? '—'}`, tone: 'violet' },
        { label: String(o['work_type_name'] ?? 'Type'), tone: 'slate' },
      ];
      case 'work-received': return [{ label: `Dist #${o['distribution'] ?? '—'}`, tone: 'violet' }];
      case 'material-inward': return [{ label: `Qty ${o['quantity'] ?? '—'}`, tone: 'sky' }];
      case 'pending-work': return [{ label: `Pending ${o['total_pending'] ?? 0}`, tone: 'amber' }];
      default: return [];
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
      case 'materials': return [{ label: 'Material', tone: 'violet' }];
      case 'suppliers': return [{ label: 'Supplier', tone: 'sky' }];
      case 'work-types': return [{ label: 'Type', tone: 'violet' }];
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
      case 'pending-work': return [{ label: 'Open', tone: 'amber' }];
      default: return [];
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
      case 'materials': return [`Stock · ${o['closing_stock'] ?? '—'} ${o['unit'] ?? ''}`.trim()];
      case 'suppliers': {
        const lines: string[] = [];
        if (o['mobile_number']) lines.push(String(o['mobile_number']));
        if (o['city']) lines.push(String(o['city']));
        return lines;
      }
      case 'work-types': return o['id'] != null ? [`ID · ${o['id']}`] : [];
      case 'distributions': return [
        String(o['work_type_name'] ?? 'Work type'),
        `Lot size · ${o['lot_size'] ?? '—'}`,
        String(o['distributed_date'] ?? ''),
      ].filter(Boolean);
      case 'work-received': return [
        o['return_date'] ? `Date · ${o['return_date']}` : '',
        o['distribution'] != null ? `Distribution #${o['distribution']}` : '',
      ].filter(Boolean);
      case 'material-inward': return [
        o['supplier_name'] ? `Supplier · ${o['supplier_name']}` : '',
        `Quantity · ${o['quantity'] ?? '—'}`,
        o['received_date'] ? `Received · ${o['received_date']}` : '',
      ].filter(Boolean);
      case 'pending-work': return [`Pending quantity · ${o['total_pending'] ?? 0}`];
      default: return [];
    }
  }

  async openAddModal(): Promise<void> {
    if (!this.key || !this.hasAddFormSheet) return;
    this.resetAddForms();
    // Load dropdown data for forms that need it
    if (this.key === 'material-inward' || this.key === 'distributions') {
      await this.loadDropdowns();
    }
    if (this.key === 'work-received') {
      await this.loadDistributions();
    }
    this.addModalOpen = true;
  }

  private async loadDropdowns(): Promise<void> {
    try {
      const [workers, materials, suppliers, workTypes] = await Promise.all([
        firstValueFrom(this.api.getWorkers()),
        firstValueFrom(this.api.getMaterials()),
        firstValueFrom(this.api.getSuppliers()),
        firstValueFrom(this.api.getWorkTypes()),
      ]);
      this.workersList = this.unwrapList(workers) as { id: number; name: string }[];
      this.materialsList = this.unwrapList(materials) as { id: number; material_name: string; unit: string }[];
      this.suppliersList = this.unwrapList(suppliers) as { id: number; name: string }[];
      this.workTypesList = this.unwrapList(workTypes) as { id: number; name: string }[];
    } catch {
      await this.showToast('Could not load dropdown data');
    }
  }

  private async loadDistributions(): Promise<void> {
    try {
      const res = await firstValueFrom(this.api.getWorkDistributions());
      this.distributionsList = this.unwrapList(res) as typeof this.distributionsList;
    } catch {
      await this.showToast('Could not load distributions');
    }
  }

  private resetAddForms(): void {
    this.workerForm = { name: '', mobile_number: '', city: '', skill_type: 'stitching', machine_type: 'simple' };
    this.supplierForm = { name: '', mobile_number: '', city: '' };
    this.materialForm = { material_name: '', unit: 'meter', description: '' };
    this.workTypeForm = { name: '' };
    this.inwardForm = { supplier: 0, material: 0, quantity: '', received_date: '', remarks: '' };
    this.distributionForm = { worker: 0, work_type: 0, lot_size: '', distributed_date: '', expected_return_date: '' };
    this.workReceivedForm = { distribution: 0, received_quantity: '', received_date: '', remarks: '' };
  }

  async submitAddForm(): Promise<void> {
    if (!this.key) return;
    try {
      switch (this.key) {
        case 'workers':
          if (!this.workerForm.name.trim() || !this.workerForm.mobile_number.trim()) {
            await this.showToast('Name and mobile are required'); return;
          }
          await firstValueFrom(this.api.createWorker({
            name: this.workerForm.name.trim(),
            mobile_number: this.workerForm.mobile_number.trim(),
            city: this.workerForm.city?.trim() || '',
            skill_type: this.workerForm.skill_type,
            machine_type: this.workerForm.machine_type,
          }));
          await this.showToast('Worker added');
          break;

        case 'suppliers':
          if (!this.supplierForm.name.trim() || !this.supplierForm.mobile_number.trim()) {
            await this.showToast('Name and mobile are required'); return;
          }
          await firstValueFrom(this.api.createSupplier({
            name: this.supplierForm.name.trim(),
            mobile_number: this.supplierForm.mobile_number.trim(),
            city: this.supplierForm.city?.trim() || '',
          }));
          await this.showToast('Supplier added');
          break;

        case 'materials':
          if (!this.materialForm.material_name.trim() || !this.materialForm.unit.trim()) {
            await this.showToast('Material name and unit are required'); return;
          }
          await firstValueFrom(this.api.createMaterial({
            material_name: this.materialForm.material_name.trim(),
            unit: this.materialForm.unit.trim().toLowerCase(),
            description: this.materialForm.description?.trim() || '',
          }));
          await this.showToast('Material added');
          break;

        case 'work-types':
          if (!this.workTypeForm.name.trim()) {
            await this.showToast('Name is required'); return;
          }
          await firstValueFrom(this.api.createWorkType({ name: this.workTypeForm.name.trim() }));
          await this.showToast('Work type added');
          break;

        case 'material-inward':
          if (!this.inwardForm.supplier || !this.inwardForm.material || !this.inwardForm.quantity || !this.inwardForm.received_date) {
            await this.showToast('Supplier, material, quantity and date are required'); return;
          }
          await firstValueFrom(this.api.createMaterialInward({
            supplier: Number(this.inwardForm.supplier),
            material: Number(this.inwardForm.material),
            quantity: String(this.inwardForm.quantity),
            received_date: this.inwardForm.received_date,
            remarks: this.inwardForm.remarks?.trim() || '',
          }));
          await this.showToast('Material inward recorded');
          break;

        case 'distributions':
          if (!this.distributionForm.worker || !this.distributionForm.work_type || !this.distributionForm.lot_size || !this.distributionForm.distributed_date) {
            await this.showToast('Worker, work type, lot size and date are required'); return;
          }
          await firstValueFrom(this.api.createWorkDistribution({
            worker: Number(this.distributionForm.worker),
            work_type: Number(this.distributionForm.work_type),
            lot_size: Number(this.distributionForm.lot_size),
            distributed_date: this.distributionForm.distributed_date,
            expected_return_date: this.distributionForm.expected_return_date || undefined,
            issued_materials: [],
          }));
          await this.showToast('Work distributed');
          break;

        case 'work-received':
          if (!this.workReceivedForm.distribution || !this.workReceivedForm.received_quantity || !this.workReceivedForm.received_date) {
            await this.showToast('Distribution, quantity and date are required'); return;
          }
          await firstValueFrom(this.api.createWorkReturn({
            distribution: Number(this.workReceivedForm.distribution),
            completed_quantity: Number(this.workReceivedForm.received_quantity),
            pending_quantity: 0,
            return_date: this.workReceivedForm.received_date,
            returned_materials: [],
          }));
          await this.showToast('Work received recorded');
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
    const toast = await this.toastCtrl.create({ message, duration: 2000, position: 'bottom' });
    await toast.present();
  }
}
