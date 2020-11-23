import sys
import configparser
import argparse
import json
import requests
import csv




#------------ Argument Parse ------------#
#----------------------------------------#
conf = configparser.ConfigParser()
conf.read('config.ini')

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', action='store', default=conf['DEFAULT']['file'])
parser.add_argument('-r', '--resource', action='store', default=conf['DEFAULT']['resource'])
parser.add_argument('-k', '--apikey', action='store', default=conf['DEFAULT']['apikey'])
parser.add_argument('-s', '--apisecret', action='store', required=True)
parser.add_argument('-c', '--cacert', action='store', default=conf['DEFAULT']['cacert'])
parser.add_argument('-o', '--output', action='store', default=conf['DEFAULT']['output'])
args = parser.parse_args()




#-------------- Data Import -------------#
#----------------------------------------#
if '.zip' in args.file:
    with zipfile.ZipFile(args.file) as myzip:
        members = myzip.namelist()

        if len(members) == 1:
            with myzip.open(members[0]) as myfile:
                record = myfile.read()

        elif len(members) > 1:
            recs = []
            for doc in members:
                with myzip.open(doc) as myfile:
                    rec = myfile.read()
                    for note in rec['documents']:
                        recs.append(note)
            record = {'documents': recs}

elif '.js' in args.file:
    with open(args.file, 'r') as f:
        record = json.load(f)

payloads = {x['metadata']['document_id']: {'profileId': args.resource, 'documents': [x['data']]}
        for x in record['documents']}




#------------- CNLP Request -------------#
#----------------------------------------#
server_add = 'https://edw-clix-d01.med.utah.edu:49120'
process_ep = '/api/v2.0/cnlp/process'
headers = {
        'api_key': args.apikey,
        'api_secret': args.apisecret,
        'Content-type': 'application/json'
        }

def post_req(pay, add, ep, head, cert):
    r = requests.post(
            add + ep,
            headers = head,
            data = json.dumps(pay),
            verify = cert)
    return json.loads(r.text)

req_responses = {k: post_req(v, server_add, process_ep, headers, args.cacert) 
        for k, v in payloads.items()}




#--------------- Formatting -------------#
#----------------------------------------#
def format_response(doc, resp, record):
    doc_id_lst = [x['metadata']['document_id'] for x in record['documents']]
    r_form = {
        'ApiResponse': resp['ApiResponse'],
        'Encoding': resp['pipeline']['Annotations']['nodes'],
        'Narrative': resp['pipeline']['Narrative'],
        'MetaData': record['documents'][doc_id_lst.index(doc)]['metadata']
        }
    
    filter_encode = [x for x in r_form['Encoding'] if x['NodeType']=='Encoding']
    r_form.update({'Encoding': filter_encode})
    return r_form

def flatten_response(resp):
    r_flat = []
    mrn = resp['MetaData']['patient_id']
    sname = resp['MetaData'].get('patient_surname', None)
    fname = resp['MetaData'].get('patient_forename', None)
    dob = resp['MetaData'].get('patient_dob', None)
    sex = resp['MetaData'].get('patient_gender', None)
    visid = resp['MetaData'].get('visit_id', None)
    docid = resp['MetaData']['document_id']
    proj = resp['MetaData']['project']
    auth = resp['MetaData'].get('author', None)
    
    for x in resp['Encoding']:
        r_flat.append([
                    mrn,
                    sname,
                    fname,
                    dob,
                    sex,
                    visid,
                    docid,
                    proj,
                    auth,
                    x['elements'][0]['FeatureValue'],
                    x['id'],
                    x['start'],
                    x['end'],
                    resp['Narrative'][x['start']:x['end']+1]
                    ])
    return r_flat

out_json = {k: format_response(k, v, record) for k, v in req_responses.items()}
out_csv = [flatten_response(x) for x in out_json.values()]




#---------------- Export ----------------#
#----------------------------------------#
with open(args.output + '.json', 'w') as f:
    json.dump(out_json, f)

with open(args.output + '.csv', 'w', newline='') as f:
    csv_header = ['patient_id','surname','forename','dob',
            'gender','document_id','project','encoding',
            'encoding_id','enc_start','enc_end','orig_text']

    writer = csv.writer(f)
    writer.writerow(csv_header)
    for sublst in out_csv:
        writer.writerows(sublst)




