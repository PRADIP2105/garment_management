from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import date
from apps.workers.models import Worker
from apps.work_management.models import WorkDistribution
from apps.stock.models import CurrentStock
from apps.materials.models import MaterialInward
from apps.companies.models import UserProfile


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    # Get company from user profile if not set by middleware
    company = getattr(request, 'company', None)
    if not company:
        try:
            profile = UserProfile.objects.select_related('company').get(user=request.user)
            company = profile.company
            request.company = company
            request.user_role = profile.role
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=400)
    
    today = date.today()
    
    # Total workers
    total_workers = Worker.objects.filter(company=company, status=True).count()
    
    # Pending work by worker
    pending_work = WorkDistribution.objects.filter(
        company=company,
        status__in=['pending', 'in_progress', 'partially_returned']
    ).values('worker__name').annotate(
        pending_lots=Count('id'),
        total_quantity=Sum('lot_size')
    ).order_by('worker__name')
    
    # Completed work today
    completed_today = WorkDistribution.objects.filter(
        company=company,
        status='completed',
        updated_at__date=today
    ).aggregate(
        count=Count('id'),
        total_quantity=Sum('lot_size')
    )
    
    # Low stock materials (less than 10 units)
    low_stock = CurrentStock.objects.filter(
        company=company,
        current_quantity__lt=10
    ).select_related('material').values(
        'material__material_name',
        'material__unit',
        'current_quantity'
    )
    
    # Today's inward
    todays_inward = MaterialInward.objects.filter(
        company=company,
        received_date=today
    ).aggregate(
        count=Count('id'),
        total_items=Count('material', distinct=True)
    )
    
    # Work distribution summary
    work_summary = WorkDistribution.objects.filter(
        company=company
    ).aggregate(
        total_distributions=Count('id'),
        pending=Count('id', filter=Q(status__in=['pending', 'in_progress'])),
        completed=Count('id', filter=Q(status='completed')),
        partially_returned=Count('id', filter=Q(status='partially_returned'))
    )
    
    return Response({
        'total_workers': total_workers,
        'pending_work_by_worker': list(pending_work),
        'completed_today': completed_today,
        'low_stock_materials': list(low_stock),
        'todays_inward': todays_inward,
        'work_summary': work_summary,
        'date': today
    })