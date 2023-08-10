from django import forms
from django.forms import ModelForm
from USERS.models import Submissions

class CodeForm(ModelForm):
    class Meta:
        model = Submissions
        fields = ['user_code']
        widgets = {'user_code' : forms.Textarea()}