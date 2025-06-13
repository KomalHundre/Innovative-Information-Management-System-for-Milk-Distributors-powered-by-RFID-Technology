from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import MilkCollection, Farmer, Payment
from datetime import datetime, timedelta
from decimal import Decimal
import razorpay
from twilio.rest import Client
from django.contrib import messages
from .forms import FarmerForm, MilkCollectionForm

# Initialize Twilio and Razorpay clients
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        recent_collections = MilkCollection.objects.select_related('farmer').all().order_by('-date')[:10]
        recent_payments = Payment.objects.select_related('farmer', 'farmer__user', 'payment_method').all().order_by('-created_at')[:10]
    else:
        farmer = get_object_or_404(Farmer, user=request.user)
        recent_collections = MilkCollection.objects.filter(farmer=farmer).order_by('-date')[:10]
        recent_payments = Payment.objects.select_related('payment_method').filter(farmer=farmer).order_by('-created_at')[:10]
    
    # Debug information
    print("\nDashboard Debug Info:")
    print(f"User: {request.user.username}")
    print(f"Is staff: {request.user.is_staff}")
    print(f"Is superuser: {request.user.is_superuser}")
    print(f"Number of recent payments: {recent_payments.count()}")
    
    for payment in recent_payments:
        print(f"\nPayment {payment.id}:")
        print(f"- Farmer: {payment.farmer}")
        print(f"- Amount: ₹{payment.amount}")
        print(f"- Status: {payment.status}")
        print(f"- Transaction ID: {payment.transaction_id}")
    
    context = {
        'recent_collections': recent_collections,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'dairyfarm/dashboard.html', context)

@login_required
def scan_rfid(request):
    if request.method == 'POST':
        rfid = request.POST.get('rfid')
        try:
            farmer = Farmer.objects.get(rfid_number=rfid)
            return JsonResponse({
                'success': True,
                'farmer_id': farmer.id,
                'name': f"{farmer.user.first_name} {farmer.user.last_name}",
                'phone': farmer.phone_number,
            })
        except Farmer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid RFID'})

@login_required
def get_farmer_details(request, rfid):
    farmer = get_object_or_404(Farmer, rfid_number=rfid)
    collections = MilkCollection.objects.filter(farmer=farmer).order_by('-date')[:5]
    
    return JsonResponse({
        'farmer': {
            'name': f"{farmer.user.first_name} {farmer.user.last_name}",
            'phone': farmer.phone_number,
            'address': farmer.address,
        },
        'recent_collections': list(collections.values())
    })

@login_required
def collect_milk(request):
    if request.method == 'POST':
        farmer_id = request.POST.get('farmer_id')
        quantity = Decimal(request.POST.get('quantity'))
        fat_content = Decimal(request.POST.get('fat_content'))
        session = request.POST.get('session')
        
        # Calculate price based on fat content
        base_price = Decimal('40.00')
        fat_premium = (fat_content - Decimal('3.0')) * Decimal('2.00')
        price_per_liter = base_price + fat_premium
        total_amount = quantity * price_per_liter
        
        farmer = get_object_or_404(Farmer, id=farmer_id)
        
        collection = MilkCollection.objects.create(
            farmer=farmer,
            quantity=quantity,
            fat_content=fat_content,
            price_per_liter=price_per_liter,
            total_amount=total_amount,
            session=session
        )
        
        return JsonResponse({'success': True, 'collection_id': collection.id})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def weekly_report(request):
    farmers = Farmer.objects.all()
    return render(request, 'dairyfarm/weekly_report.html', {'farmers': farmers})

@login_required
def process_payment(request):
    # Payment processing logic here
    return redirect('dashboard')

@login_required
def add_farmer(request):
    if request.method == 'POST':
        form = FarmerForm(request.POST)
        if form.is_valid():
            farmer = form.save()
            messages.success(request, f'Farmer {farmer.user.get_full_name()} added successfully!')
            return redirect('dashboard')
    else:
        form = FarmerForm()
    
    return render(request, 'dairyfarm/add_farmer.html', {'form': form})

@login_required
def add_collection(request):
    if request.method == 'POST':
        form = MilkCollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)

             # Calculate price_per_liter and total_amount
            base_price = Decimal('40.00')
            fat_premium = (collection.fat_content - Decimal('3.0')) * Decimal('2.00')
            collection.price_per_liter = base_price + fat_premium
            collection.total_amount = collection.quantity * collection.price_per_liter

            collection.save()
            messages.success(request, 'Milk collection recorded successfully!')
            return redirect('dashboard')
    else:
        form = MilkCollectionForm()
    
    return render(request, 'dairyfarm/add_collection.html', {'form': form})

@login_required
def farmer_list(request):
    farmers = Farmer.objects.all()
    return render(request, 'dairyfarm/farmer_list.html', {'farmers': farmers})