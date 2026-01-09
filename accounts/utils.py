# accounts/utils.py
from .models import Conversation, ConversationVisit

def get_or_create_private_conversation(user1, user2):
    """
    Возвращает или создаёт личную беседу между двумя пользователями.
    """
    conversations = Conversation.objects.filter(
        participants=user1
    ).filter(
        participants=user2
    )
    if conversations.exists():
        return conversations.first()
    else:
        conv = Conversation.objects.create()
        conv.participants.add(user1, user2)
        return conv


def mark_conversation_as_read(user, conversation):
    """
    Обновляет время последнего визита → сбрасывает счётчик непрочитанных.
    """
    visit, created = ConversationVisit.objects.get_or_create(
        user=user,
        conversation=conversation
    )
    # `auto_now=True` обновит дату автоматически при save()
    visit.save()
    return visit


def get_unread_count_for_user(user):
    """
    Возвращает общее количество непрочитанных сообщений.
    """
    from django.db import models
    total = 0
    visits = ConversationVisit.objects.filter(user=user)
    for visit in visits:
        count = visit.conversation.messages.filter(
            created_at__gt=visit.last_visited_at
        ).count()
        total += count
    return total