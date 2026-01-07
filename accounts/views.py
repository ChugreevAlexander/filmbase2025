from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ProfileForm

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'is_own_profile': True  # потому что это ваш профиль
    })

@login_required
def user_list_view(request):
    """
    Отображает список всех пользователей.
    """
    users = User.objects.all().select_related('profile')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
def public_profile_view(request, user_id):
    """
    Показывает публичный профиль любого пользователя по его ID.
    """
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'accounts/public_profile.html', {
        'profile': profile,
        'is_own_profile': request.user.id == user_id
    })

@login_required
def profile_edit_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            user_instance=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile, user_instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})