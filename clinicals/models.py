from django.db import models

# Create your models here.
class Patient(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    age=models.IntegerField()

class ClinicalData(models.Model):
    ComponentNames =[('H/W','Height/Weight'),('bp','Blood Pressure'),('heartrate','Heart Rate')]
    componentName = models.CharField(choices=ComponentNames,max_length=100)
    componentValue = models.CharField(max_length=100)
    measureDateTime = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE) # one to many
