from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Property, Inquiry, Message
from .forms import PropertyForm
from accounts.forms import AddLandlordForm

User = get_user_model()

def home_view(request):
    featured_properties = Property.objects.filter(
        landlord__role='ADMIN'
    ).order_by('-created_at')[:6]

    total_listings = Property.objects.filter(landlord__role='ADMIN').count()

    context = {
        'featured_properties': featured_properties,
        'total_listings': total_listings,
    }
    return render(request, 'home.html', context)

def property_search_view(request):
    query = request.GET.get('q', '')
    # Only show properties listed by Admins
    properties = Property.objects.filter(landlord__role='ADMIN').order_by('-created_at')
    
    if query:
        properties = properties.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
        
    context = {
        'properties': properties,
        'query': query
    }
    return render(request, 'property_search.html', context)

def property_detail_view(request, pk):
    property = get_object_or_404(Property, pk=pk)
    context = {
        'property': property
    }
    return render(request, 'property_detail.html', context)

@login_required
def dashboard_view(request):
    if request.user.role == 'STUDENT':
        inquiries = Inquiry.objects.filter(student=request.user).order_by('-created_at')
        # Only show recent properties listed by Admin
        recent_properties = Property.objects.filter(landlord__role='ADMIN').order_by('-created_at')[:3]
        context = {
            'inquiries': inquiries,
            'total_inquiries': inquiries.count(),
            'recent_properties': recent_properties,
        }
        return render(request, 'dashboard/student_index.html', context)
        
    elif request.user.role == 'ADMIN':
        properties = Property.objects.all().order_by('-created_at')
        total_reviews = sum([p.reviews.count() for p in properties])
        inquiries = Inquiry.objects.all().order_by('-created_at')
        
        context = {
            'properties': properties,
            'total_properties': properties.count(),
            'total_reviews': total_reviews,
            'inquiries': inquiries,
        }
        return render(request, 'dashboard/index.html', context)
    elif request.user.role == 'LANDLORD':
        properties = Property.objects.filter(landlord=request.user).order_by('-created_at')
        total_reviews = sum([p.reviews.count() for p in properties])
        inquiries = Inquiry.objects.filter(property__in=properties).order_by('-created_at')
        
        context = {
            'properties': properties,
            'total_properties': properties.count(),
            'total_reviews': total_reviews,
            'inquiries': inquiries,
        }
        return render(request, 'dashboard/index.html', context)
    else:
        messages.error(request, "You do not have a valid role.")
        return redirect('home')

@login_required
def property_create_view(request):
    if request.user.role not in ['ADMIN', 'LANDLORD']:
        return redirect('home')
        
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.landlord = request.user
            property.save()
            
            # Log property creation
            from accounts.logging_utils import log_event
            log_event(
                level='INFO',
                category='PROPERTY',
                action='Property Created',
                message=f"Property '{property.title}' created - Price: {property.price_per_month}frs",
                user=request.user,
                request=request
            )
            
            messages.success(request, "Property listed successfully!")
            return redirect('dashboard')
    else:
        form = PropertyForm()
        
    return render(request, 'dashboard/property_form.html', {'form': form})

@login_required
def property_edit_view(request, pk):
    if request.user.role not in ['ADMIN', 'LANDLORD']:
        return redirect('home')
        
    if request.user.role == 'ADMIN':
        property = get_object_or_404(Property, pk=pk)
    else:
        property = get_object_or_404(Property, pk=pk, landlord=request.user)

    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, "Property updated successfully!")
            return redirect('dashboard')
    else:
        form = PropertyForm(instance=property)
        
    return render(request, 'dashboard/property_form.html', {'form': form, 'is_edit': True})

@login_required
def property_delete_view(request, pk):
    if request.user.role == 'ADMIN':
        property = get_object_or_404(Property, pk=pk)
    elif request.user.role == 'LANDLORD':
        property = get_object_or_404(Property, pk=pk, landlord=request.user)
    else:
        messages.error(request, "You do not have permission to delete properties.")
        return redirect('dashboard')

    if request.method == 'POST':
        prop_title = property.title
        property.delete()
        
        # Log property deletion
        from accounts.logging_utils import log_event
        log_event(
            level='INFO',
            category='PROPERTY',
            action='Property Deleted',
            message=f"Property '{prop_title}' deleted",
            user=request.user,
            request=request
        )
        
        messages.success(request, "Property deleted successfully!")
    return redirect('dashboard')

@login_required
def submit_inquiry_view(request, property_id):
    if request.method == 'POST':
        if request.user.role != 'STUDENT':
            messages.error(request, "Only students can send inquiries.")
            return redirect('property_detail', pk=property_id)
            
        property = get_object_or_404(Property, pk=property_id)
        message_content = request.POST.get('message', '')
        
        if message_content.strip():
            # Get or create the Inquiry thread
            inquiry, created = Inquiry.objects.get_or_create(
                property=property,
                student=request.user
            )
            
            # Create the initial message
            Message.objects.create(
                inquiry=inquiry,
                sender=request.user,
                content=message_content
            )
            
            messages.success(request, f"Your inquiry has been sent! You can view it in your dashboard.")
            return redirect('chat', inquiry_id=inquiry.id)
        else:
            messages.error(request, "Message cannot be empty.")
    return redirect('property_detail', pk=property_id)

@login_required
def chat_view(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, pk=inquiry_id)
    
    # Check permissions
    if request.user != inquiry.student and request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to view this chat.")
        return redirect('dashboard')
        
    chat_messages = inquiry.messages.all()
    
    # Mark messages as read
    unread_messages = chat_messages.exclude(sender=request.user).filter(is_read=False)
    unread_messages.update(is_read=True)
    
    context = {
        'inquiry': inquiry,
        'chat_messages': chat_messages,
    }
    return render(request, 'chat.html', context)

@login_required
def send_message_view(request, inquiry_id):
    if request.method == 'POST':
        inquiry = get_object_or_404(Inquiry, pk=inquiry_id)
        
        # Check permissions
        if request.user != inquiry.student and request.user.role != 'ADMIN':
            return redirect('dashboard')
            
        content = request.POST.get('content', '')
        if content.strip():
            Message.objects.create(
                inquiry=inquiry,
                sender=request.user,
                content=content
            )
    return redirect('chat', inquiry_id=inquiry_id)

@login_required
def add_landlord_view(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Only admins can add landlords.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = AddLandlordForm(request.POST)
        if form.is_valid():
            landlord = form.save()

            from accounts.logging_utils import log_event
            log_event(
                level='INFO',
                category='LANDLORD',
                action='Landlord Created',
                message=f"Landlord '{landlord.username}' created by admin",
                user=request.user,
                request=request
            )

            messages.success(request, f"Landlord '{landlord.username}' has been added successfully.")
            return redirect('manage_landlords')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddLandlordForm()

    context = {'form': form}
    return render(request, 'admin/add_landlord.html', context)


@login_required
def manage_landlords_view(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Only admins can manage landlords.")
        return redirect('dashboard')

    landlords = User.objects.filter(role='LANDLORD').order_by('-date_joined')
    context = {'landlords': landlords}
    return render(request, 'admin/manage_landlords.html', context)

@login_required
def delete_landlord_view(request, landlord_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "Only admins can delete landlords.")
        return redirect('dashboard')
    
    landlord = get_object_or_404(User, pk=landlord_id, role='LANDLORD')
    
    if request.method == 'POST':
        # Delete properties and related inquiries/messages
        properties = Property.objects.filter(landlord=landlord)
        for prop in properties:
            Inquiry.objects.filter(property=prop).delete()
        properties.delete()
        
        # Delete the landlord
        username = landlord.username
        landlord.delete()
        
        # Log landlord deletion
        from accounts.logging_utils import log_event
        log_event(
            level='WARNING',
            category='LANDLORD',
            action='Landlord Deleted',
            message=f"Landlord '{username}' and their {properties.count()} properties deleted",
            user=request.user,
            request=request
        )
        
        messages.success(request, f"Landlord '{username}' and their properties have been deleted.")
        return redirect('manage_landlords')
    
    context = {'landlord': landlord}
    return render(request, 'admin/confirm_delete_landlord.html', context)
