from django import forms
from django import forms
from .models import UploadedFile
# Create your models here.

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file_name','created_by','file_type','file_size','file','description','is_public','file_extension','tags','is_archived','category']

    def clean_file(self):
        file = self.cleaned_data['file']
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File size must be under 5MB.")
        return file
    
# class UpdateForm(forms.ModelForm):
#     class UpdateForm(forms.ModelForm):
#         def __init__(self, *args, **kwargs):
#             instance = kwargs.get('instance')
#             initial = kwargs.get('initial', {})
#             if instance:
#                 initial['file_name'] = instance.file_name
#                 initial['created_by'] = instance.created_by
#                 initial['file_type'] = instance.file_type
#                 initial['file_size'] = instance.file_size
#                 initial['file'] = instance.file
#                 initial['description'] = instance.description
#                 initial['is_public'] = instance.is_public
#                 initial['file_extension'] = instance.file_extension
#                 initial['tags'] = instance.tags
#                 initial['is_archived'] = instance.is_archived
#                 initial['category'] = instance.category
#             kwargs['initial'] = initial
#             super(UpdateForm, self).__init__(*args, **kwargs)
            
#     def __init__(self, *args, **kwargs):
#         super(UpdateForm, self).__init__(*args, **kwargs)
#         self.fields['file_name'].initial = 'default_file_name.txt'  # Set default file name

#     class Meta:
#         model = UploadedFile
#         fields = ['file_name', 'created_by', 'file_type', 'file_size','file','description', 'is_public', 'file_extension', 'tags', 'is_archived', 'category']