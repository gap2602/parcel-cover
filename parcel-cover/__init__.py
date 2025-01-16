import azure.functions as func
import pandas as pd
import requests
import logging
import json
import pymupdf
import re
import io
from . import helper_functions as hf


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    file_id = req.params.get('file_id')
    if not file_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            file_id = req_body.get('file_id')

    if file_id:
        used_cols = ['name', 'address', 'product', 'quantity', 'order_no']
        df = pd.DataFrame(columns=used_cols)
        url = "https://drive.google.com/uc?id=" + file_id
        response = requests.get(url)
        pdf_file = io.BytesIO(response.content)
        doc = pymupdf.open(stream=pdf_file, filetype="pdf")
        for i in range(len(doc)):
            # if doc[i].get_text()[:4] == 'PICK':
            #     temp = hf.extract_shopee_with_image(doc, i)
            # el
            if re.search("Shopee Order", doc[i].get_text()):
                temp = hf.extract_shopee(doc, i)
            elif re.search("LAZADA Order", doc[i].get_text()):
                temp = hf.extract_lazada(doc, i)
            else:
                temp = hf.extract_tiktok(doc, i)
        
            df = pd.concat([df, temp], axis=0).reset_index(drop=True)
            json_df = json.dumps(df.to_dict('records'))

        return func.HttpResponse(json_df)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a file_id in the query string or in the request body for a personalized response.",
             status_code=200
        )
