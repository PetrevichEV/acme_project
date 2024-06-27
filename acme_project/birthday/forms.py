from django import forms
from django.core.exceptions import ValidationError

from .models import Birthday
from .validators import real_age

BEATLES = {'Джон Леннон', 'Пол Маккартни', 'Джордж Харрисон', 'Ринго Старр'}

class BirthdayForm(forms.ModelForm):
    # Удаляем все описания полей.

    # Все настройки задаём в подклассе Meta.
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Birthday
        # Указываем, что надо отобразить все поля.
        fields = '__all__'
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'})
        } 
        validators=(real_age,)

        def clean_first_name(self):
            # Получаем значение имени из словаря очищенных данных.
            first_name = self.cleaned_data['first_name']
            # Разбиваем полученную строку по пробелам 
            # и возвращаем только первое имя.
            return first_name.split()[0]
        
        def clean(self):
            # Получаем имя и фамилию из очищенных полей формы.
            first_name = self.cleaned_data['first_name']
            last_name = self.cleaned_data['last_name']
            # Проверяем вхождение сочетания имени и фамилии во множество имён.
            if f'{first_name} {last_name}' in BEATLES:
                raise ValidationError(
                    'Мы тоже любим Битлз, но введите, пожалуйста, настоящее имя!'
                )