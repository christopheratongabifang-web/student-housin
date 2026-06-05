from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property, Inquiry, Message
from .forms import PropertyForm

def home_view(request):
    return render(request, 'home.html')

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
            messages.success(request, "Property listed successfully!")
            return redirect('dashboard')
    else:
        form = PropertyForm()
        
    return render(request, 'dashboard/property_form.html', {'form': form})

@login_required
def property_edit_view(request, pk):
    if request.user.role not in ['ADMIN', 'LANDLORD']:
        return redirect('home')
        
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
    property = get_object_or_404(Property, pk=pk, landlord=request.user)
    if request.method == 'POST':
        property.delete()
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
