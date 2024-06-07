# Create your views here.
from io import BytesIO
import io
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from openpyxl import Workbook,load_workbook
from .forms import FileUploadForm
from .models import UploadedFile
from PyPDF2 import PdfMerger, PdfReader
from django.core.cache import cache
from openpyxl.styles import PatternFill
import os

def color_header(sheet,color):
    header_row = sheet[1] 
    for cell in header_row:
        cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        
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
                        for row_index, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                            output_ws.append(row)
                            # Color the header row
                            if row_index == 1:
                                color_header(output_ws, "D3D3D3") 
                    
                    output_stream = BytesIO()
                    output_wb.save(output_stream) 
                    output_stream.seek(0)
        
                elif file_path.endswith('.pdf'):
                    output_wb = Workbook()
                    output_ws = output_wb.active 
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
    
def mergeMultipleExcelInMultipleSheet(request):
    media_files_cache_key='media_files'
    get_cache_data=cache.get(media_files_cache_key)
    
    if get_cache_data:
            media_data=get_cache_data
            print("This list data are being fetched from the cache memory")  
    else:
        
        media_data = UploadedFile.objects.all()
        cache.set(media_files_cache_key,media_data,timeout=100)

    if request.method == "POST":
        files = request.POST.getlist("selected_files")
        print(files)
        if not files:
            error_message = "No files selected. Please select at least one file."
            return HttpResponse(error_message, status=400) 
        
        output_wb = Workbook()
        output_wb.remove(output_wb.active)
        
        output_pdf = PdfMerger()
        output_stream = BytesIO()
        
        
        # checking if user sends multiple files like xlsx and pdf at same time
        file_count=0
        xls_files=0
        pdf_files=0
            
        for selectedfile_id in files:
            selectedfile = get_object_or_404(UploadedFile, pk=selectedfile_id)
            file_path = selectedfile.file.path
            
            file_count=file_count+1
            if file_path.endswith('.xlsx'):
                xls_files=xls_files+1
            if file_path.endswith('.pdf'):
                    pdf_files=pdf_files+1
                    
        print("total Files uploaded",file_count)
        print("total xls Files found ",xls_files)
        print("total pdf Files uploaded",pdf_files)


        for uploaded_file_id in files:
            uploaded_file = get_object_or_404(UploadedFile, pk=uploaded_file_id)
            print(uploaded_file.name)
            file_path = uploaded_file.file.path
            try:
                if file_count==xls_files:
                    
                    file_name_with_extension = os.path.basename(uploaded_file.file.name)
                    file_name_without_extension = os.path.splitext(file_name_with_extension)[0]
                    
                    wb = load_workbook(file_path)
                    for sheet_name in wb.sheetnames:
                        output_ws = output_wb.create_sheet(title=file_name_without_extension)
                        sheet = wb[sheet_name]
                        for row_index, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                            output_ws.append(row)
                            if row_index == 1:
                                color_header(output_ws, "D3D3D3") 
                    
                    output_stream = BytesIO()
                    output_wb.save(output_stream) 
                    output_stream.seek(0)
        
                elif file_count==pdf_files:
                    output_wb = Workbook()
                    output_ws = output_wb.active 
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
                    return HttpResponse("Error: Files are of multiple format!.")

            except Exception as e:
                return HttpResponse(f"Error: {e}")

        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if any(file_path.endswith('.xlsx') for file_path in [uploaded_file.file.path for uploaded_file in UploadedFile.objects.filter(pk__in=files)]) else 'application/pdf'
        filename = 'merged.xlsx' if content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' else 'merged.pdf'
        response = HttpResponse(output_stream, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response 

    return render(request, "mergeMultipleExcel/upload.html",{'data':media_data})


def multipleProcedureMultipleSheet(request):
    wb=Workbook()
    wb.remove(wb.active)
    header_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    
    #example json data/ query data
    
    procedureData1 = [{"name":"Andro","contactNo":54532666,"employeeId":98765,"EmployeeType":"KeysightFTE"},
                    {"name":"Sachin","contactNo":54532666,"employeeId":98765,"EmployeeType":"IT Manager"},
                    {"name":"Rolisha","contactNo":54532666,"employeeId":98765,"EmployeeType":"KeysightFTE"}]
    
    procedureData2 = [{"name":"Manish","contactNo":54532666,"employeeId":98765,"EmployeeType":"IT Manager"},
                    {"name":"Ronick","contactNo":54532666,"employeeId":98765,"EmployeeType":"KeysightFTE"},
                    {"name":"Kamuna","contactNo":54532666,"employeeId":98765,"EmployeeType":"IT Manager"}]
    
    all_json_data = [procedureData1, procedureData2]
    if request.method == "POST":
        for index, json_data in enumerate(all_json_data, start=1):
            sheet = wb.create_sheet(title=f"Sheet {index}")
            # Write column headers
            for col, key in enumerate(json_data[0].keys(), start=1):
                cell=sheet.cell(row=1, column=col, value=key)
                cell.fill = header_fill
            # Write data
            for row, emp in enumerate(json_data, start=2):
                for col, value in enumerate(emp.values(), start=1):
                    sheet.cell(row=row, column=col, value=value)
                    

        output = io.BytesIO()
        wb.save(output)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=output.xlsx'
        output.seek(0)
        response.write(output.getvalue())
        
        return response
    
    return render(request, "multipleProcedureMultipleSheet/getsheet.html",{'all_json_data':all_json_data})


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