from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile, Conversation, Message, ConversationVisit, MessageFile
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import get_messages
from .forms import ProfileForm, GroupChatCreateForm
from .utils import get_or_create_private_conversation, mark_conversation_as_read
from django.db import models, transaction
from django.utils import timezone

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

@login_required
def conversation_list_view(request):
    """Список всех бесед пользователя с количеством непрочитанных"""
    conversations = request.user.conversations.prefetch_related('messages').all()

    for conv in conversations:
        # Получаем или создаём запись о посещении
        visit, created = ConversationVisit.objects.get_or_create(
            user=request.user,
            conversation=conv
        )
        # Считаем непрочитанные
        conv.unread_count = conv.messages.filter(
            created_at__gt=visit.last_visited_at
        ).count()
        conv.last_message = conv.messages.last()

    return render(request, 'accounts/conversations.html', {
        'conversations': conversations
    })


@login_required
def conversation_detail_view(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )
    mark_conversation_as_read(request.user, conversation)
    messages_qs = conversation.messages.all()

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        files = request.FILES.getlist('files')  # ← получаем список файлов

        if not content and not files:
            messages.warning(request, "Сообщение не может быть пустым.")
        else:
            with transaction.atomic():
                message = Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    content_raw=content
)
                # Сохраняем все файлы
                for uploaded_file in files:
                    MessageFile.objects.create(
                        message=message,
                        file=uploaded_file
                    )
            return redirect('accounts:conversation_detail', conversation_id=conversation_id)

    return render(request, 'accounts/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages_qs
    })

@login_required
def start_private_chat_view(request, user_id):
    """Начать личный чат с пользователем"""
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        messages.error(request, "Нельзя писать самому себе.")
        return redirect('accounts:user_list')
    
    conversation = get_or_create_private_conversation(request.user, other_user)
    return redirect('accounts:conversation_detail', conversation_id=conversation.id)

@login_required
def create_group_chat_view(request):
    if request.method == 'POST':
        form = GroupChatCreateForm(request.POST, current_user=request.user)
        if form.is_valid():
            form.current_user = request.user
            conversation = form.save()
            return redirect('accounts:conversation_detail', conversation_id=conversation.id)
    else:
        form = GroupChatCreateForm(current_user=request.user)
    
    return render(request, 'accounts/create_group_chat.html', {'form': form})