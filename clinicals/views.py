from django.shortcuts import render

from clinicals.serializers import PatientSerializer
from .models import ClinicalData,Patient, PatientCopy
from django.views.generic import CreateView,DeleteView,UpdateView,ListView
from django.urls import reverse_lazy
from .forms import ClinicalDataForm
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
import reversion
from reversion.models import Version
from rest_framework import status

# Create your views here.
class PatientCopyListView(ListView):
    model=PatientCopy
    
class PatientListView(ListView):
    model=Patient
    


# class PatientCreateView(CreateView):
#      # Declare a revision block.
#     with reversion.create_revision():
#         model=Patient
#         success_url=reverse_lazy('index')
#         fields={'firstName','lastName','age'}
#          # Store some meta-information.
#         reversion.set_user("Robot")
#         reversion.set_comment("Created revision 1")


class PatientCreateView(CreateView):
    model = Patient
    fields = ['firstName', 'lastName', 'age']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Use reversion context manager to create a revision
        with reversion.create_revision():
            # Call the super method to save the instance
            self.object = form.save()
            
            # Store meta-information
            # reversion.set_user("Dumy User")
            reversion.set_comment("Created patient entry")
            
            return response
    
class PatientCopyCreateView(CreateView):
    model = PatientCopy
    fields = ['email', 'rollno']
    success_url = reverse_lazy('indexCopy')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Use reversion context manager to create a revision
        with reversion.create_revision():
            # Call the super method to save the instance
            self.object = form.save()
            
            # Store meta-information
            # reversion.set_user("Dumy User")
            reversion.set_comment("Created patient entry")
            
            return response



# class PatientUpdateView(UpdateView):
#     # Declare a new revision block.
#     with reversion.create_revision():
#         model=Patient
#         success_url=reverse_lazy('index')
#         fields={'firstName','lastName','age'}
#         reversion.set_user("dummy")
#         reversion.set_comment("Created revision 2")

class PatientUpdateView(UpdateView):
    model = Patient
    fields = ['firstName', 'lastName', 'age']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Use reversion context manager to create a revision
        with reversion.create_revision():
            # Call the super method to save the instance
            self.object = form.save()
            
            # Store meta-information
            # reversion.set_user(self.request.user)  # Use actual logged-in user
            reversion.set_comment("Updated patient entry")
            
            return response

class PatientCopyUpdateView(UpdateView):
    model = PatientCopy
    fields = ['email', 'rollno']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Use reversion context manager to create a revision
        with reversion.create_revision():
            # Call the super method to save the instance
            self.object = form.save()
            
            # Store meta-information
            # reversion.set_user(self.request.user)  # Use actual logged-in user
            reversion.set_comment("Updated patient entry")
            
            return response

class PatientDeleteView(DeleteView):
    model=Patient
    success_url=reverse_lazy('index')

def addData(request,**kwargs):
    fm=ClinicalDataForm()
    patient=Patient.objects.get(id=kwargs['pk'])
    if request.method == 'POST':
        form=ClinicalDataForm(request.POST)
        if form.is_valid():
            # Declare a revision block.
            with reversion.create_revision():
                form.save()
                 # Store some meta-information
                reversion.set_comment("Created revision 1")
                
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



@api_view(['POST'])
def get_patient_data(request):
    if request.method == 'POST':
        # Extract the ID parameter from the POST request body
        patient_id = request.data.get('id')
        print("Patient Id ",patient_id)
        # Validate the ID parameter
        if not patient_id:
            return Response({"error": "ID parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:

            model_classes = [Patient, PatientCopy]
            # Fetch the current version of the patient
            print("Is Registered Patient Model ",reversion.is_registered(Patient))
            
            # Fetch version history
            version_list = []
            # patient_instance = Patient.objects.get(id=patient_id)  # Get the instance for versioning
            # print("Version instance",patient_instance)
            versions = Version.objects.get_for_model(Patient).filter(object_id=patient_id)  # Get version history for the object
       
            for version in versions:
                version_data = {
                    "revision_id": version.revision.pk,
                    "data": version.field_dict
                }
                version_list.append(version_data)
            
            return Response({
                "version_history": version_list
            })

        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
