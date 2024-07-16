import base64
import datetime
import json
from django.db import connection, connections
from rest_framework.response import Response
from rest_framework import status
import logging
import time
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

def create_data_excel_report_in_binary(records, report, filename, sheetname):
    try:
        with BytesIO() as b:
            sqwb_dataframe = pd.DataFrame.from_records(records)
            currency_value = sqwb_dataframe['Currency'].iloc[0]
            new_selling_price = f"Selling Price ({currency_value})"
            new_extended_price = f"Extended Price ({currency_value})"
            sqwb_dataframe = sqwb_dataframe.rename(columns={'Selling Price': new_selling_price,'Extended Price':new_extended_price})

            with pd.ExcelWriter(b) as writer:
                sqwb_dataframe.to_excel(writer, index=False, sheet_name=sheetname)

                (max_row, max_col) = sqwb_dataframe.shape
                workbook = writer.book
                worksheet = writer.sheets[sheetname]
                # headerGray = workbook.add_format({'bg_color': '#c5c8c9'})
                # borderColor = workbook.add_format()
                # borderColor.set_border(1)

                # worksheet.conditional_format(0, 0, max_row, max_col - 1, {'type': 'no_blanks',
                #                                                           'format': borderColor})

                # worksheet.conditional_format(0, 0, max_row, max_col - 1, {'type': 'blanks',
                #                                                           'format': borderColor})

                # worksheet.conditional_format(0, 0, 0, max_col - 1, {'type': 'no_blanks',
                #                                                     'format': headerGray})

            b.seek(0)
            binary_data = b.getvalue()
            encoded_excel_data = base64.b64encode(binary_data).decode()
        return encoded_excel_data

    except Exception as e:
        logger.exception(f"Exception occurred while calling the Generate Excel API: " + str(e))
        raise e

def create_data_excel_report(records,report,filename,sheetname):
    try:
        start = time.time()
        with BytesIO() as b:
            sqwb_dataframe = pd.DataFrame.from_records(records)
            currency_value = sqwb_dataframe['Currency'].iloc[0]
            new_selling_price = f"Selling Price ({currency_value})"
            new_extended_price = f"Extended Price ({currency_value})"
            sqwb_dataframe = sqwb_dataframe.rename(columns={'Selling Price': new_selling_price,'Extended Price':new_extended_price})
            with pd.ExcelWriter(b) as writer:

                sqwb_dataframe.to_excel(writer,index=False,sheet_name=sheetname)

                (max_row, max_col) = sqwb_dataframe.shape
                workbook  = writer.book
                worksheet = writer.sheets[sheetname]
                # headerGray = workbook.add_format({'bg_color': '#c5c8c9'})
                # borderColor = workbook.add_format()
                # borderColor.set_border(1) 

                # worksheet.conditional_format(0,0,max_row,max_col-1, {'type':'no_blanks',
                #                     'format':   borderColor})

                # worksheet.conditional_format(0,0,max_row,max_col-1, {'type':'blanks',
                #                     'format':   borderColor})
                
                # worksheet.conditional_format(0,0,0,max_col-1, {'type':'no_blanks',
                #                     'format': headerGray})

            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            final_filename = filename
            response['Content-Disposition'] = f'attachment; filename={final_filename}.xlsx'

        duration = round((time.time() - start) * 1000,2)
        logger.debug(f"Excel file generated successfully for report {report} using Excel API.", extra={'executiontime' : duration })
        return response
            
    except Exception as e:
        logger.exception(f"Exception occured while calling the Generate Excel API: " + str(e))
        return Response({"Error":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_transaction_excel_report(request):
    logger.debug("Create Transaction Excel Report API triggered.")
    try:
        transaction_ids = request.data.get('transactionId', [])
        if not transaction_ids:
            return HttpResponse("Transaction IDs are missing.", status=400)
        # Get the database connection for 'sqwb-db'
        connection = connections['sqwb-db']
        try:
            with connection.cursor() as cursor:
                cursor.execute('CALL get_tids_data(%s,%s); fetch all in result;', [transaction_ids, 'result'])
                json_data = dictfetchall(cursor)
                print("Json data",json_data)
            cursor.close()
        except Exception as e:
            print(e)
            return None
        try:
            with connection.cursor() as cursor:
                cursor.execute('CALL get_llm_tids_data(%s,%s); fetch all in result;', [transaction_ids, 'result'])
                llm_data = dictfetchall(cursor)
                print("LLM data",llm_data)
            cursor.close()
        except Exception as e:
            print(e)
            return None
        
        combined_data = []
        print("Error starts from here")
        for item1 in json_data:
            combined_data.append(item1)
            for item2 in llm_data:
                if item1["Transaction ID"] == item2.get("Transaction ID") and item1["Item Number"] == item2.get("component_item") and item1["parent_document_number"] == item2.get("parent_document_number") and item1["PTO Model Item"] == item2.get("PTO Model Item"):
                    combined_data.append(item2)

        if not combined_data:
            logger.debug("No transaction data for the ID ")
            return HttpResponse("Error occurred while retrieving transaction data.", status=500)

        try:
            with connection.cursor() as cursor:
                cursor.execute('CALL get_cfg_item_data(%s,%s); fetch all in result;', [transaction_ids, 'result'])
                cfg_item = dictfetchall(cursor)
            cursor.close()
        except Exception as e:
            print(e)
            return None
        
        new_combined_data=[]
        for item1 in cfg_item:
            if(item1["Unit Cost (USD)"] is not None and 'NPA' not in str(item1["Unit Cost (USD)"])):
                item1["Unit Cost (USD)"] = float(item1["Unit Cost (USD)"])
                
            if(item1["BOM Quantity Per"] is not None):
                item1["BOM Quantity Per"] = int(item1["BOM Quantity Per"])
            if(item1["BOM Minimum Quantity"] is not None):
                item1["BOM Minimum Quantity"] = int(item1["BOM Minimum Quantity"])
            if(item1["BOM Maximum Quantity"] is not None):
                item1["BOM Maximum Quantity"] = int(item1["BOM Maximum Quantity"])
                
            new_combined_data.append(item1)
            for item2 in combined_data:
                if(item2["Unit Cost (USD)"] is not None and 'NPA' not in str(item2["Unit Cost (USD)"])):
                    item2["Unit Cost (USD)"] = float(item2["Unit Cost (USD)"])
                if(item2["Extended Cost (USD)"] is not None and 'NPA' not in str(item2["Extended Cost (USD)"])):
                    item2["Extended Cost (USD)"] = float(item2["Extended Cost (USD)"])
                if(item2["Selling Price"] is not None and 'NPA' not in str(item2["Selling Price"])):
                    item2["Selling Price"] = float(item2["Selling Price"])
                if(item2["Corporate Rate"] is not None):
                    item2["Corporate Rate"] = float(item2["Corporate Rate"])
                if(item2["Selling Price (USD)"] is not None and 'NPA' not in str(item2["Selling Price (USD)"])):
                    item2["Selling Price (USD)"] = float(item2["Selling Price (USD)"])
                if(item2["Extended Price"] is not None and 'NPA' not in str(item2["Extended Price"])):
                    item2["Extended Price"] = float(item2["Extended Price"])
                if(item2["Extended Price (USD)"] is not None and 'NPA' not in str(item2["Extended Price (USD)"])):
                    item2["Extended Price (USD)"] = float(item2["Extended Price (USD)"])
                
                if(item2["BOM Quantity Per"] is not None):
                    item2["BOM Quantity Per"] = int(item2["BOM Quantity Per"])
                if(item2["BOM Minimum Quantity"] is not None):
                    item2["BOM Minimum Quantity"] = int(item2["BOM Minimum Quantity"])
                if(item2["BOM Maximum Quantity"] is not None):
                    item2["BOM Maximum Quantity"] = int(item2["BOM Maximum Quantity"])    
                    
                if item1["Transaction ID"] == item2.get("Transaction ID") and item1["Item Number"] == item2.get("Cfg Item") and item1["parent_document_number"] == item2.get("parent_document_number") and item1["PTO Model Item"] == item2.get("PTO Model Item"):
                    new_combined_data.append(item2)
            
        def remove_keys(d):
            if not isinstance(d, (dict, list)):
                return d
            if isinstance(d, list):
                return [remove_keys(v) for v in d]
            return {k: remove_keys(v) for k, v in d.items() if k not in {'parent_document_number', 'component_item','Cfg Item','PTO Model Item'}}

        new_combined_data = remove_keys(new_combined_data)
        
        filename = f"Transaction_File"
        sheetname = "Transaction_Data"
        response = create_data_excel_report(new_combined_data, 'Transaction Report', filename, sheetname)

        logger.debug("Successfully send the Create Transaction Excel Report list")
        return response
    
    except Exception as e:
        logger.debug("Exception occured while calling the Create Transaction Excel Report API.")
        return HttpResponse(f"An error occurred: {str(e)}", status=500) 
    
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
