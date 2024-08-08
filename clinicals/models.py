from django.db import models
import reversion 
# Create your models here.

@reversion.register()
class Patient(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    age=models.IntegerField()

@reversion.register()
class ClinicalData(models.Model):
    ComponentNames =[('H/W','Height/Weight'),('bp','Blood Pressure'),('heartrate','Heart Rate')]
    componentName = models.CharField(choices=ComponentNames,max_length=100)
    componentValue = models.CharField(max_length=100)
    measureDateTime = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE) # one to many


@reversion.register()
class PatientCopy(models.Model):
    email = models.CharField(max_length=100)
    rollno = models.CharField(max_length=100)