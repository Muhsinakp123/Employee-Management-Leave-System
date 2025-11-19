from django.shortcuts import render
from .forms import ResetPasswordForm
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,user_passes_test

from .forms import LoginForm, UserForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile  
from .forms import LeaveForm
from django.contrib import messages
from .models import Leave
from .forms import ProfileForm
from django.db.models import Count


def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            # Save full name into the user model (optional but useful)
            full_name = form.cleaned_data['full_name']
            if ' ' in full_name:
                user.first_name, user.last_name = full_name.split(' ', 1)
            else:
                user.first_name = full_name
            user.save()

            # Create profile
            Profile.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                emp_id=form.cleaned_data['emp_id'],
                department=form.cleaned_data['department']
            )

            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserForm()

    return render(request, 'signup.html', {'form': form})


# --- Login ---
def login_View(request):

    # Fetch the first superuser (for demo display)
    admin_user = User.objects.filter(is_superuser=True).first()
    admin_username = admin_user.username if admin_user else "Not found"
    admin_password = "admin123"

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('dashboard')
                else:
                    return redirect('home')
            else:
                return render(request, 'login.html', {
                    'form': form,
                    'error': 'Invalid credentials',
                    'admin_username': admin_username,
                    'admin_password': admin_password
                })
    else:
        form = LoginForm()

    return render(request, 'login.html', {
        'form': form,
        'admin_username': admin_username,
        'admin_password': admin_password
    })




# --- Forgot Password from login page ---
def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()

        if not username:
            return render(request, 'login.html', {
                'form': LoginForm(),
                'error': 'Please enter your username first.'
            })

        try:
            user = User.objects.get(username=username)
            # Username found → redirect to reset password page
            return redirect('reset_password', user_id=user.id)

        except User.DoesNotExist:
            # Username invalid → show error *without redirecting*
            form = LoginForm(initial={'username': username})
            return render(request, 'login.html', {
                'form': form,
                'error': 'User not found. Please enter a valid username.'
            })
    return redirect('login')


# --- Reset Password ---

def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    success_message = None  # message flag

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            # Show success message in same page instead of redirect
            success_message = "Password reset successfully! Redirecting to login..."
    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {
        'form': form,
        'success_message': success_message
    })

@login_required    
def home(request):
    return render(request,'employee/home.html')    
   
@login_required
def apply_leave(request):
    # Get the logged-in user's employee profile
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Validation: start_date <= end_date
            if start_date > end_date:
                messages.error(request, "Start date cannot be after end date.")
            else:
                # Save the leave request
                leave = form.save(commit=False)
                leave.employee = profile
                leave.status = 'Pending'
                leave.save()
                messages.success(request, "Leave application submitted successfully!")
                return redirect('home')  
    else:
        form = LeaveForm()

    return render(request, 'employee/apply_leave.html', {'form': form})



@login_required
def leave_list(request):
    user_profile = Profile.objects.get(user=request.user)
    leaves = Leave.objects.filter(employee=user_profile)
    return render(request, 'employee/leave_list.html', {'leaves': leaves})

@login_required
def leave_detail(request, pk):
    user_profile = Profile.objects.get(user=request.user)
    leave = get_object_or_404(Leave, pk=pk, employee=user_profile)
    return render(request, 'leave_detail.html', {'leave': leave})


@login_required
def leave_delete(request, pk):
    user_profile = Profile.objects.get(user=request.user)
    leave = get_object_or_404(Leave, pk=pk, employee=user_profile)
    if leave.status == 'Pending':
        leave.delete()
    return redirect('leave_list')

@login_required
def leave_edit(request, pk):
    user_profile = Profile.objects.get(user=request.user)
    leave = get_object_or_404(Leave, pk=pk, employee=user_profile)

    if leave.status != 'Pending':
        return redirect('leave_list')

    if request.method == 'POST':
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            return redirect('leave_list')
    else:
        form = LeaveForm(instance=leave)

    return render(request, 'employee/leave_update.html', {'form': form})

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'employee/profile.html', {'profile': profile})

@login_required
def profile_update(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        initial = {'email': request.user.email}
        form = ProfileForm(instance=profile, initial=initial)
    return render(request, 'employee/profile_update.html', {'form': form})

@login_required
def profile_delete(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # deletes both User and Profile
        messages.success(request, 'Your account has been deleted.')
        return redirect('login')
    return render(request, 'employee/profile_delete.html')



def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    total_employees = Profile.objects.count()
    total_leaves = Leave.objects.count()

    pending_count = Leave.objects.filter(status='Pending').count()
    approved_count = Leave.objects.filter(status='Approved').count()
    rejected_count = Leave.objects.filter(status='Rejected').count()

    leaves = Leave.objects.select_related('employee').all().order_by('-id')

    # Handle approve/reject directly from dashboard
    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        leave = Leave.objects.get(id=leave_id)
        if action == 'approve':
            leave.status = 'Approved'
        elif action == 'reject':
            leave.status = 'Rejected'
        leave.save()
        return redirect('dashboard')

    context = {
        'total_employees': total_employees,
        'total_leaves': total_leaves,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'leaves': leaves,
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def manage_employees(request):
    employees = Profile.objects.all()
    return render(request, 'admin/manage_employees.html', {'employees': employees})

@login_required
@user_passes_test(is_admin)
def admin_leave_list(request):
    # Show all leave applications for admin
    leaves = Leave.objects.select_related('employee', 'employee__user').all().order_by('-id')

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        leave = Leave.objects.get(id=leave_id)

        if action == 'approve':
            leave.status = 'Approved'
        elif action == 'reject':
            leave.status = 'Rejected'
        leave.save()
        return redirect('admin_leave_list')

    return render(request, 'admin/admin_leave_list.html', {'leaves': leaves})


@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    admin_user = request.user
    return render(request, 'admin/admin_profile.html', {'admin_user': admin_user})

@login_required
@user_passes_test(is_admin)
def delete(request, emp_id):
    employee = Profile.objects.get(id=emp_id)
    employee.delete()
    return redirect('manage_employees')

    

def logout_view(request):
    logout(request)
    return redirect('login')