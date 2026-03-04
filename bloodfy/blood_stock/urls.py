"""
Blood Stock app URL routes.
"""

from django.urls import path
from .views import (
    BloodStockListView,
    BloodStockDetailView,
    BloodStockStatisticsView,
    BloodStockExportView,
    BloodStockImportView,
)

urlpatterns = [
    path('', BloodStockListView.as_view(), name='blood-stock-list'),
    path('statistics/', BloodStockStatisticsView.as_view(), name='blood-stock-statistics'),
    path('export/', BloodStockExportView.as_view(), name='blood-stock-export'),
    path('import/', BloodStockImportView.as_view(), name='blood-stock-import'),
    path('<uuid:stock_id>/', BloodStockDetailView.as_view(), name='blood-stock-detail'),
]
