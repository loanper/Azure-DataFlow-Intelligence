import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import json
import time
from requests import get, post
import os
import requests
from collections import OrderedDict
import numpy as np
import pandas as pd
app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="input/{name}",
                               connection="storageaccountloan_STORAGE") 
def blob_trigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

# This is the call to the Document Intelligence endpoint
    endpoint = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]
    apim_key = os.environ["DOCUMENT_INTELLIGENCE_KEY"]
    post_url = endpoint + "/formrecognizer/v2.1/layout/analyze"
    source = myblob.read()

    headers = {
    # Request headers
    'Content-Type': 'application/pdf',
    'Ocp-Apim-Subscription-Key': apim_key,
        }

    text1=os.path.basename(myblob.name)

    resp = requests.post(url=post_url, data=source, headers=headers)

    if resp.status_code != 202:
        print("POST analyze failed:\n%s" % resp.text)
        quit()
    print("POST analyze succeeded:\n%s" % resp.headers)
    get_url = resp.headers["operation-location"]

    wait_sec = 25

    time.sleep(wait_sec)
    # The layout API is async therefore the wait statement

    resp = requests.get(url=get_url, headers={"Ocp-Apim-Subscription-Key": apim_key})

    resp_json = json.loads(resp.text)

    status = resp_json["status"]

    if status == "succeeded":
        print("POST Layout Analysis succeeded:\n%s")
        results = resp_json
    else:
        print("GET Layout results failed:\n%s")
        quit()

    results = resp_json

    # This is the connection to the blob storage, with the Azure Python SDK
    blob_service_client = BlobServiceClient.from_connection_string(os.environ["storageaccountloan_STORAGE"])
    container_client=blob_service_client.get_container_client("output")


# The code below extracts the json format into tabular data.
    # Please note that you need to adjust the code below to your form structure.
    # It probably won't work out-of-the-box for your specific form.
    pages = results["analyzeResult"]["pageResults"]

    def make_page(p):
        res=[]
        res_table=[]
        y=0
        page = pages[p]
        for tab in page["tables"]:
            for cell in tab["cells"]:
                res.append(cell)
                res_table.append(y)
            y=y+1

        res_table=pd.DataFrame(res_table)
        res=pd.DataFrame(res)
        res["table_num"]=res_table[0]
        h=res.drop(columns=["boundingBox","elements"])
        h.loc[:,"rownum"]=range(0,len(h))
        num_table=max(h["table_num"])
        return h, num_table, p

    h, num_table, p= make_page(0)

    for k in range(num_table+1):
        new_table=h[h.table_num==k]
        new_table.loc[:,"rownum"]=range(0,len(new_table))
        row_table=pages[p]["tables"][k]["rows"]
        col_table=pages[p]["tables"][k]["columns"]
        b = pd.DataFrame("", index=range(row_table), columns=range(col_table), dtype=object)
        s = 0
        for i, j in zip(new_table["rowIndex"], new_table["columnIndex"]):
            # On récupère le texte de la s-ième cellule trouvée pour ce tableau
            b.loc[i, j] = new_table.iloc[s]["text"]
            s = s + 1
# Here is the upload to the blob storage
    tab1_csv=b.to_csv(header=False,index=False,mode='w')
    name1=(os.path.splitext(text1)[0]) +'.csv'
    container_client.upload_blob(name=name1, data=tab1_csv, overwrite=True)