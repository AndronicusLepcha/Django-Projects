# Create your views here.
from io import BytesIO
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from openpyxl import Workbook,load_workbook
from .forms import FileUploadForm
from .models import UploadedFile
from PyPDF2 import PdfMerger, PdfReader
from django.core.cache import cache


def mergeMultipleExcel(request):
    media_files_cache_key='media_files'
    get_cache_data=cache.get(media_files_cache_key)
    
    if get_cache_data:
            media_data=get_cache_data
            print("This list data are from the cache memory")  
    else:
        
        media_data = UploadedFile.objects.all()
        cache.set(media_files_cache_key,media_data,timeout=100)

    if request.method == "POST":
        files = request.POST.getlist("selected_files")
        if not files:
            error_message = "No files selected. Please select at least one file."
            return HttpResponse(error_message, status=400) 
        output_wb = Workbook()
        output_ws = output_wb.active 
        output_pdf = PdfMerger()
        output_stream = BytesIO()

        for uploaded_file_id in files:
            uploaded_file = get_object_or_404(UploadedFile, pk=uploaded_file_id)
            file_path = uploaded_file.file.path
            try:
                if file_path.endswith('.xlsx'):
                    wb = load_workbook(file_path)
                    for sheet_name in wb.sheetnames:
                        sheet = wb[sheet_name]
                        for row in sheet.iter_rows(values_only=True):
                            output_ws.append(row)
                    
                    output_stream = BytesIO()
                    output_wb.save(output_stream) 
                    output_stream.seek(0)
        
                elif file_path.endswith('.pdf'):
                    pdf_reader = PdfReader(file_path)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        for line in page.extract_text().split('\n'):
                            output_ws.append([line])
                    output_pdf.append(file_path)
                    
                    output_stream = BytesIO()
                    output_pdf.write(output_stream)
                    output_stream.seek(0)
                else:
                    return HttpResponse("Error: Unsupported file format")

            except Exception as e:
                return HttpResponse(f"Error: {e}")

        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if any(file_path.endswith('.xlsx') for file_path in [uploaded_file.file.path for uploaded_file in UploadedFile.objects.filter(pk__in=files)]) else 'application/pdf'
        filename = 'merged.xlsx' if content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' else 'merged.pdf'
        response = HttpResponse(output_stream, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response 

    return render(request, "mergeMultipleExcel/upload.html",{'data':media_data})

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