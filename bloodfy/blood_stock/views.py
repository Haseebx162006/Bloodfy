"""
Blood Stock app views.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
import csv
from io import StringIO

from .models import BloodStock, StockTransaction
from .serializers import (
    BloodStockSerializer, BloodStockListSerializer,
    BloodStockCreateSerializer, BloodStockUpdateSerializer,
    StockTransactionSerializer, StockStatisticsSerializer
)
from utils.responses import success_response, error_response, created_response
from utils.permissions import IsAdmin, IsAdminOrReadOnly, AdminWriteOnly


class BloodStockListView(APIView):
    """List and create blood stock."""
    
    permission_classes = [AdminWriteOnly]  # GET: all auth users, POST: admin only
    
    def get(self, request):
        """List all blood stock."""
        queryset = BloodStock.objects.all()
        
        # Apply filters
        blood_group = request.query_params.get('blood_group')
        hospital = request.query_params.get('hospital')
        city = request.query_params.get('city')
        status_filter = request.query_params.get('status')  # critical, low, normal
        
        if blood_group:
            queryset = queryset.filter(blood_group=blood_group)
        if hospital:
            queryset = queryset.filter(hospital_name__icontains=hospital)
        if city:
            queryset = queryset.filter(hospital_city__icontains=city)
        if status_filter == 'critical':
            queryset = [s for s in queryset if s.is_critical]
        elif status_filter == 'low':
            queryset = [s for s in queryset if s.is_low and not s.is_critical]
        
        serializer = BloodStockListSerializer(queryset, many=True)
        
        return success_response(
            data={
                'blood_stock': serializer.data,
                'count': len(serializer.data)
            },
            message="Blood stock retrieved"
        )
    
    def post(self, request):
        """Create or update blood stock entry (Admin only - enforced by permission class)."""
        # Admin check handled by AdminWriteOnly permission class
            
        serializer = BloodStockCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message="Failed to register stock entry",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if identical stock entry exists (same blood group + hospital)
        # to avoid duplicates and update instead
        blood_group = serializer.validated_data['blood_group']
        hospital_name = serializer.validated_data['hospital_name']
        
        stock, created = BloodStock.objects.update_or_create(
            blood_group=blood_group,
            hospital_name=hospital_name,
            defaults={
                'hospital_city': serializer.validated_data.get('hospital_city', ''),
                'units_available': serializer.validated_data.get('units_available', 0),
                'critical_threshold': serializer.validated_data.get('critical_threshold', 5),
            }
        )
        
        return created_response(
            data=BloodStockSerializer(stock).data,
            message="Blood stock entry registered successfully" if created else "Blood stock entry updated"
        )


class BloodStockDetailView(APIView):
    """Get and update blood stock."""
    
    permission_classes = [AdminWriteOnly]  # GET: all auth users, PUT/DELETE: admin only
    
    def get(self, request, stock_id):
        """Get blood stock details."""
        try:
            stock = BloodStock.objects.get(id=stock_id)
        except BloodStock.DoesNotExist:
            return error_response(
                message="Blood stock not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = BloodStockSerializer(stock)
        return success_response(
            data=serializer.data,
            message="Blood stock retrieved"
        )
    
    def put(self, request, stock_id):
        """Update blood stock (Admin only - enforced by permission class)."""
        # Admin check handled by AdminWriteOnly permission class
        
        try:
            stock = BloodStock.objects.get(id=stock_id)
        except BloodStock.DoesNotExist:
            return error_response(
                message="Blood stock not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        old_units = stock.units_available
        
        serializer = BloodStockUpdateSerializer(
            stock,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return error_response(
                message="Update failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        # Log transaction
        new_units = stock.units_available
        if old_units != new_units:
            StockTransaction.objects.create(
                blood_stock=stock,
                transaction_type='adjustment',
                units=new_units - old_units,
                units_before=old_units,
                units_after=new_units,
                performed_by=request.user,
                notes=request.data.get('notes', 'Manual adjustment')
            )
        
        return success_response(
            data=BloodStockSerializer(stock).data,
            message="Blood stock updated"
        )

    def delete(self, request, stock_id):
        """Delete blood stock entry (Admin only - enforced by permission class)."""
        # Admin check handled by AdminWriteOnly permission class
            
        try:
            stock = BloodStock.objects.get(id=stock_id)
        except BloodStock.DoesNotExist:
            return error_response(
                message="Blood stock not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        stock.delete()
        return success_response(message="Blood stock entry deleted successfully")


class BloodStockStatisticsView(APIView):
    """Get blood stock statistics."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive stock statistics."""
        stocks = BloodStock.objects.all()
        
        # Aggregate data
        total_available = stocks.aggregate(total=Sum('units_available'))['total'] or 0
        total_reserved = stocks.aggregate(total=Sum('units_reserved'))['total'] or 0
        total_expired = stocks.aggregate(total=Sum('units_expired'))['total'] or 0
        
        # Prepare by_blood_group as an object for the frontend
        by_blood_group_map = {}
        max_capacity_per_group = 100  # Threshold for percentage calculation
        
        for bg in ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']:
            units = stocks.filter(blood_group=bg).aggregate(
                total=Sum('units_available')
            )['total'] or 0
            
            percentage = min(100, (units / max_capacity_per_group) * 100)
            by_blood_group_map[bg] = {
                'units': units,
                'percentage': percentage
            }
        
        # Calculate overall inventory health percentage
        inventory_percentage = (total_available / (len(by_blood_group_map) * max_capacity_per_group)) * 100
        inventory_percentage = min(100, inventory_percentage)

        # Build critical and low stock lists
        critical_stocks = []
        low_stocks = []
        for stock in stocks:
            if stock.is_critical:
                critical_stocks.append({
                    'blood_group': stock.blood_group,
                    'hospital': stock.hospital_name,
                    'units': stock.units_available,
                })
            elif stock.is_low:
                low_stocks.append({
                    'blood_group': stock.blood_group,
                    'hospital': stock.hospital_name,
                    'units': stock.units_available,
                })

        data = {
            'total_units': total_available + total_reserved,
            'total_available': total_available,
            'total_reserved': total_reserved,
            'total_expired': total_expired,
            'inventory_percentage': inventory_percentage,
            'by_blood_group': by_blood_group_map,
            'critical_stocks': critical_stocks,
            'low_stocks': low_stocks
        }
        
        return success_response(
            data=data,
            message="Stock statistics retrieved"
        )


class BloodStockExportView(APIView):
    """Export blood stock to CSV."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """Export stock data as CSV."""
        from django.http import HttpResponse
        
        stocks = BloodStock.objects.all()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="blood_stock.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Blood Group', 'Hospital', 'City', 'Available',
            'Reserved', 'Total', 'Status', 'Last Updated'
        ])
        
        for stock in stocks:
            writer.writerow([
                stock.blood_group,
                stock.hospital_name,
                stock.hospital_city,
                stock.units_available,
                stock.units_reserved,
                stock.total_units,
                stock.stock_status.upper(),
                stock.last_updated.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response


class BloodStockImportView(APIView):
    """Import blood stock from CSV."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        """Import stock data from CSV."""
        file = request.FILES.get('file')
        
        if not file:
            return error_response(
                message="No file provided",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not file.name.endswith('.csv'):
            return error_response(
                message="Only CSV files are supported",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content = file.read().decode('utf-8')
            reader = csv.DictReader(StringIO(content))
            
            created = 0
            updated = 0
            errors = []
            
            for row in reader:
                try:
                    stock, is_created = BloodStock.objects.update_or_create(
                        blood_group=row.get('blood_group', row.get('Blood Group')),
                        hospital_name=row.get('hospital_name', row.get('Hospital')),
                        defaults={
                            'units_available': int(row.get('units_available', row.get('Available', 0))),
                            'hospital_city': row.get('hospital_city', row.get('City', '')),
                        }
                    )
                    if is_created:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    errors.append(str(e))
            
            return success_response(
                data={
                    'created': created,
                    'updated': updated,
                    'errors': errors
                },
                message=f"Import completed: {created} created, {updated} updated"
            )
            
        except Exception as e:
            return error_response(
                message=f"Failed to import: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
