from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["document"]

class VerifySignForm(forms.Form):
    documento_id = forms.IntegerField(label="Document ID")
