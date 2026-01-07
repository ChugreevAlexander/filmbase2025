# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile

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