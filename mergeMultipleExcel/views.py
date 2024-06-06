# Create your views here.
from io import BytesIO
from django.shortcuts import redirect, render
from django.http import HttpResponse
from openpyxl import Workbook,load_workbook
from .forms import FileUploadForm
from .models import UploadedFile


def mergeMultipleExcel(request):
    all_data = UploadedFile.objects.all()

    if request.method == "POST":
        files = request.POST.getlist("selected_files")
        output_wb = Workbook()
        output_ws = output_wb.active 
        
        for uploaded_file_id in files:
            uploaded_file = UploadedFile.objects.get(pk=uploaded_file_id)
            file_path = uploaded_file.file.path

            try:
                wb = load_workbook(file_path)
                for sheet_name in wb.sheetnames:
                    sheet = wb[sheet_name]
                    for row in sheet.iter_rows(values_only=True):
                        output_ws.append(row)
            except Exception as e:
                return HttpResponse(f"Error: {e}")

        output_stream = BytesIO()
        output_wb.save(output_stream)
        output_stream.seek(0)
        
        response = HttpResponse(output_stream, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=consolidated.xlsx'
        return response

    return render(request, "mergeMultipleExcel/upload.html",{'data':all_data})

def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_success')
    else:
        form = FileUploadForm()
    return render(request, 'upload_form.html', {'form': form})

def upload_success(request):
    return render(request, 'upload_success.html')

def show_uploaded_data(request):
    all_data=UploadedFile.objects.all()
    return render(request,'mergeMultipleExcel/upload.html',{'data':all_data})