from rest_framework import permissions, viewsets

from apps.workers.models import Worker
from .serializers import WorkerSerializer


class WorkerViewSet(viewsets.ModelViewSet):
    """Company-scoped CRUD for workers."""

    serializer_class = WorkerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Worker.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

