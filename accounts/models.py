from django.db import models
from django.contrib.auth.models import User
import markdown
from django.utils.html import mark_safe

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birthday = models.DateField(null=True, blank=True, verbose_name="День рождения")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")
    bio = models.TextField(null=True, blank=True, verbose_name="Биография")

    def __str__(self):
        return f"{self.user.username}'s profile"
    
class Conversation(models.Model):
    name = models.CharField("Название беседы", max_length=100, blank=True)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.name:
            return self.name
        participant_names = ", ".join([u.username for u in self.participants.all()])
        return f"Беседа: {participant_names}"


class Message(models.Model):
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content_raw = models.TextField("Сообщение (исходный текст)", blank=True)
    content_html = models.TextField("Сообщение (рендеренный HTML)", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        # Обновляем поле content_html при сохранении
        self.content_html = markdown.markdown(self.content_raw, extensions=['extra', 'codehilite'])
        super().save(*args, **kwargs)

    @property
    def content(self):
        # Показываем отрендеренный HTML
        return mark_safe(self.content_html)

    def __str__(self):
        return f"{self.sender}: {self.content_raw[:30]}"


class ConversationVisit(models.Model):
    """
    Отслеживает, когда пользователь последний раз заходил в беседу.
    Используется для определения количества непрочитанных сообщений.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversation_visits',
        verbose_name="Пользователь"
    )
    conversation = models.ForeignKey(
        'Conversation',
        on_delete=models.CASCADE,
        related_name='visits',
        verbose_name="Беседа"
    )
    last_visited_at = models.DateTimeField(
        auto_now=True,  # автоматически обновляется при каждом сохранении
        verbose_name="Последний визит"
    )

    class Meta:
        verbose_name = "Посещение беседы"
        verbose_name_plural = "Посещения бесед"
        unique_together = ('user', 'conversation')  # один пользователь — одна запись на беседу

    def __str__(self):
        return f"{self.user.username} → {self.conversation} ({self.last_visited_at.strftime('%d.%m.%Y %H:%M')})"
    
class MessageFile(models.Model):
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(
        upload_to='message_files/',
        verbose_name="Файл"
    )

    class Meta:
        verbose_name = "Файл сообщения"
        verbose_name_plural = "Файлы сообщений"

    def __str__(self):
        return f"Файл для сообщения {self.message.id}: {self.file.name}"