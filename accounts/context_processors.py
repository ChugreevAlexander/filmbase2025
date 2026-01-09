# accounts/context_processors.py
from .utils import get_unread_count_for_user

def unread_messages(request):
    """
    Добавляет в контекст количество непрочитанных сообщений.
    """
    if request.user.is_authenticated:
        return {
            'unread_messages_count': get_unread_count_for_user(request.user)
        }
    return {
        'unread_messages_count': 0
    }