from django.urls import path
from .views import PatientCopyCreateView, PatientCopyListView, PatientCopyUpdateView, PatientCreateView,PatientDeleteView,PatientListView,PatientUpdateView,addData,analyze,get_patient_data

urlpatterns = [
    path('addPatient', PatientListView.as_view(),name='index'),
    path('createPatient/', PatientCreateView.as_view()),
    
    path('addPatientCopy', PatientCopyListView.as_view(),name='indexCopy'),
    path('createPatientCopy/', PatientCopyCreateView.as_view()),
    path('updateCopy/<int:pk>/', PatientCopyUpdateView.as_view()),
    
    path('update/<int:pk>/', PatientUpdateView.as_view()),
    path('delete/<int:pk>/', PatientDeleteView.as_view()),
    path('addData/<int:pk>/',addData),
    path('analyze/<int:pk>/',analyze),
    path('getPatient/',get_patient_data)
]
