from django import forms
from django import forms
from .models import UploadedFile
# Create your models here.

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file','name']

    def clean_file(self):
        file = self.cleaned_data['file']
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File size must be under 5MB.")
        return file