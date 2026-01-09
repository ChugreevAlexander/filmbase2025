# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Conversation, Profile

class ProfileForm(forms.ModelForm):
    # Поля из модели User
    username = forms.CharField(max_length=150, label="Имя пользователя")
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = Profile
        fields = ['birthday', 'avatar', 'bio']
        labels = {
            'birthday': 'Дата рождения',
            'avatar': 'Аватар',
            'bio': 'О себе',
        }
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        # Передаём user_instance при создании формы
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)

        if self.user_instance:
            self.fields['username'].initial = self.user_instance.username
            self.fields['email'].initial = self.user_instance.email

    def save(self, commit=True):
        # Сохраняем User
        if self.user_instance:
            self.user_instance.username = self.cleaned_data['username']
            self.user_instance.email = self.cleaned_data['email']
            if commit:
                self.user_instance.save()

        # Сохраняем Profile
        profile = super().save(commit=False)
        if commit:
            profile.save()
        return profile
    
    
class GroupChatCreateForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        label="Название группы"
    )
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Участники"
    )

    class Meta:
        model = Conversation
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        if self.current_user:
            self.fields['participants'].queryset = User.objects.exclude(id=self.current_user.id)

    def clean_participants(self):
        participants = self.cleaned_data.get('participants')
        if participants and len(participants) < 2:
            raise ValidationError("Групповая беседа должна включать минимум 2 участников (помимо вас).")
        return participants

    def save(self, commit=True):
        conversation = super().save(commit=False)
        if commit:
            conversation.save()
            # Добавляем текущего пользователя + выбранных участников
            selected_participants = list(self.cleaned_data['participants'])
            conversation.participants.set(selected_participants + [self.current_user])
        return conversation