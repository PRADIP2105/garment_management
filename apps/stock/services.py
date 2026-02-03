from decimal import Decimal
from django.db import transaction
from .models import StockLedger, CurrentStock


class StockService:
    @staticmethod
    @transaction.atomic
    def add_inward_stock(company, material, quantity, reference_type, reference_id, remarks=""):
        """Add stock from material inward"""
        # Get or create current stock
        current_stock, created = CurrentStock.objects.get_or_create(
            company=company,
            material=material,
            defaults={'current_quantity': Decimal('0')}
        )
        
        # Update current stock
        new_balance = current_stock.current_quantity + Decimal(str(quantity))
        current_stock.current_quantity = new_balance
        current_stock.save()
        
        # Create ledger entry
        StockLedger.objects.create(
            company=company,
            material=material,
            transaction_type='inward',
            quantity=quantity,
            balance_quantity=new_balance,
            reference_type=reference_type,
            reference_id=reference_id,
            remarks=remarks
        )
        
        return current_stock

    @staticmethod
    @transaction.atomic
    def issue_stock(company, material, quantity, reference_type, reference_id, remarks=""):
        """Issue stock for work distribution"""
        try:
            current_stock = CurrentStock.objects.get(company=company, material=material)
        except CurrentStock.DoesNotExist:
            raise ValueError(f"No stock available for {material.material_name}")
        
        if current_stock.current_quantity < Decimal(str(quantity)):
            raise ValueError(f"Insufficient stock. Available: {current_stock.current_quantity}, Required: {quantity}")
        
        # Update current stock
        new_balance = current_stock.current_quantity - Decimal(str(quantity))
        current_stock.current_quantity = new_balance
        current_stock.save()
        
        # Create ledger entry
        StockLedger.objects.create(
            company=company,
            material=material,
            transaction_type='issued',
            quantity=quantity,
            balance_quantity=new_balance,
            reference_type=reference_type,
            reference_id=reference_id,
            remarks=remarks
        )
        
        return current_stock

    @staticmethod
    @transaction.atomic
    def return_stock(company, material, quantity, reference_type, reference_id, remarks=""):
        """Return stock from work completion"""
        # Get or create current stock
        current_stock, created = CurrentStock.objects.get_or_create(
            company=company,
            material=material,
            defaults={'current_quantity': Decimal('0')}
        )
        
        # Update current stock
        new_balance = current_stock.current_quantity + Decimal(str(quantity))
        current_stock.current_quantity = new_balance
        current_stock.save()
        
        # Create ledger entry
        StockLedger.objects.create(
            company=company,
            material=material,
            transaction_type='returned',
            quantity=quantity,
            balance_quantity=new_balance,
            reference_type=reference_type,
            reference_id=reference_id,
            remarks=remarks
        )
        
        return current_stock

    @staticmethod
    @transaction.atomic
    def record_wastage(company, material, quantity, reference_type, reference_id, remarks=""):
        """Record material wastage"""
        try:
            current_stock = CurrentStock.objects.get(company=company, material=material)
        except CurrentStock.DoesNotExist:
            raise ValueError(f"No stock available for {material.material_name}")
        
        if current_stock.current_quantity < Decimal(str(quantity)):
            raise ValueError(f"Insufficient stock for wastage. Available: {current_stock.current_quantity}")
        
        # Update current stock
        new_balance = current_stock.current_quantity - Decimal(str(quantity))
        current_stock.current_quantity = new_balance
        current_stock.save()
        
        # Create ledger entry
        StockLedger.objects.create(
            company=company,
            material=material,
            transaction_type='wastage',
            quantity=quantity,
            balance_quantity=new_balance,
            reference_type=reference_type,
            reference_id=reference_id,
            remarks=remarks
        )
        
        return current_stock