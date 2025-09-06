from django import forms
from ckeditor.widgets import CKEditorWidget
from bleach import clean
from bleach.css_sanitizer import CSSSanitizer
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Board, Response, CATEGORIES

class AdForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'content', 'category']
        widgets = {'content': CKEditorWidget()}

    def clean_content(self):
        content = self.cleaned_data['content']
        css_sanitizer = CSSSanitizer(allowed_css_properties=settings.BLEACH_ALLOWED_STYLES)
        return clean(
            content,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
            tags=settings.BLEACH_ALLOWED_TAGS,
            css_sanitizer=css_sanitizer
        )

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']

class SubcriberForm(forms.Form):
    category = forms.MultipleChoiceField(
        choices=CATEGORIES,
        label="",
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

class ConfirmManagerForm(forms.Form):
    code = forms.CharField(max_length=20, label='Введите код для подтверждения, что Вы менеджер')

    def clean_code(self):
        if str(settings.MANAGER_CODE) != self.cleaned_data['code']:
            raise ValidationError('Вы ввели неверный код')
        return self.cleaned_data['code']

class MassSendingForm(forms.Form):
    subject = forms.CharField(min_length=5, max_length=50, label='Тема письма')
    text = forms.CharField(min_length=20, label='Текст письма', widget=forms.Textarea)