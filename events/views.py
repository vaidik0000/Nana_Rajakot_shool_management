from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event
from .forms import EventForm
from core.decorators import new_user_restricted

# Create your views here.

@login_required
def event_list(request):
    events = Event.objects.all()
    # Get user type to control display of action buttons
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    return render(request, 'events/event_list.html', {'events': events, 'is_student': is_student})

@login_required
@new_user_restricted
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Event created successfully.')
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event'})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    # Get user type to control display of action buttons
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    return render(request, 'events/event_detail.html', {'event': event, 'is_student': is_student})

@login_required
@new_user_restricted
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Edit Event'})

@login_required
@new_user_restricted
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('events:event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})
