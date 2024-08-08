from django.contrib import admin

from clinicals.models import ClinicalData, Patient,PatientCopy

# Register your models here.
myModels = [Patient,ClinicalData,PatientCopy]
admin.site.register(myModels)
