from django.shortcuts import render
from .models import ClinicalData,Patient
from django.views.generic import CreateView,DeleteView,UpdateView,ListView
from django.urls import reverse_lazy
from .forms import ClinicalDataForm
from django.shortcuts import redirect

# Create your views here.
class PatientListView(ListView):
    model=Patient

class PatientCreateView(CreateView):
    model=Patient
    success_url=reverse_lazy('index')
    fields={'firstName','lastName','age'}

class PatientUpdateView(UpdateView):
    model=Patient
    success_url=reverse_lazy('index')
    fields={'firstName','lastName','age'}

class PatientDeleteView(DeleteView):
    model=Patient
    success_url=reverse_lazy('index')

def addData(request,**kwargs):
    fm=ClinicalDataForm()
    patient=Patient.objects.get(id=kwargs['pk'])
    if request.method == 'POST':
        form=ClinicalDataForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/')
    return render(request,'clinicals/clinicaldata_form.html',{'form':fm,'patient':patient})


def analyze(request,**kwargs):
    data=ClinicalData.objects.filter(patient_id=kwargs['pk'])
    reponseData=[]
    for eachEntry in data:
        if eachEntry.componentName =='H/W':
            heightAndWeight = eachEntry.componentValue.split('/')
            if len(heightAndWeight)>1:
                feetToMeters = float(heightAndWeight[0])*0.4536
                BMI = (float(heightAndWeight[1])/feetToMeters*feetToMeters)
                bmiEntry=ClinicalData()
                bmiEntry.componentName='BMI'
                bmiEntry.componentValue=BMI
                reponseData.append(bmiEntry)
        reponseData.append(eachEntry)
    return render(request,'clinicals/generateReport.html',{'data':reponseData})
