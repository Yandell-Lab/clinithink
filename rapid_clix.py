#!/usr/bin/env python3

import sys
import argparse
import zipfile
import json
import requests




#------------ Argument Parse ------------#
#----------------------------------------#
with open("config.json", "r") as f:
        conf = json.load(f)

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--document', action='store', default=conf["document"],
        help='JSON or zipped JSON file containing clinical documents.')
parser.add_argument('-r', '--resource', action='store', default=conf["resource"],
        help='Name of resource set.')
parser.add_argument('-k', '--apikey', action='store', default=conf["apikey"],
        help='User-specific API key from Clinithink.')
parser.add_argument('-s', '--apisecret', action='store', required=True,
        help='User-specific secret key from Clinithink.')
#parser.add_argument('-c', '--cacert', action='store', default=conf["cacert"],
#        help='File path of CA certificate (.pem) used for SSL verification.')
parser.add_argument('-g', '--group', action='store_true', default=False,
        help='Group documents by patient_id. Reduces number of requests sent to server.')
parser.add_argument('-a', '--abstractions', action='store_true', default=False,
        help='Only output list of abstractions instead of SNOMED-CT encodings.')
parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout,
        help='Provide name of output file. Default (-) writes to stdout.')
args = parser.parse_args()




#-------------- Data Import -------------#
#----------------------------------------#
if '.zip' in args.document:
    with zipfile.ZipFile(args.document) as myzip:
        members = myzip.namelist()

        if len(members) == 1:
            with myzip.open(members[0]) as myfile:
                record = json.load(myfile)

        elif len(members) > 1:
            recs = []
            for doc in members:
                with myzip.open(doc) as myfile:
                    rec = json.load(myfile)
                    for note in rec['documents']:
                        recs.append(note)
            record = {'documents': recs}

elif '.js' in args.document:
    with open(args.document, 'r') as f:
        record = json.load(f)

if args.group:
    from itertools import groupby
    group_lst = []
    for k,v in groupby(record['documents'], key=lambda x:x['metadata']['patient_id']):
        v_lst = list(v)
        dat_lst = [x['data'] for x in v_lst]
        drop_keys = ['document_id','visit_id']
        meta = {key: value for key, value in v_lst[0]['metadata'].items() if key not in drop_keys}
        group_lst.append({'data': dat_lst, 'metadata': meta})
    record = {'documents': group_lst}

    payloads = {x['metadata']['patient_id']: {'profileId': args.resource, 'documents': x['data']}
        for x in record['documents']}

else:
    payloads = {x['metadata']['document_id']: {'profileId': args.resource, 'documents': [x['data']]}
        for x in record['documents']}




#------------- CNLP Request -------------#
#----------------------------------------#
server_add = conf['host']
process_ep = conf['endpoint']
headers = {
        'api_key': args.apikey,
        'api_secret': args.apisecret,
        'Content-type': 'application/json'
        }

def post_req(pay, add, ep, head):
    r = requests.post(
            add + ep,
            headers = head,
            data = json.dumps(pay),
            verify = False)
    return json.loads(r.text)

req_responses = {k: post_req(v, server_add, process_ep, headers) 
        for k, v in payloads.items()}




#--------------- Formatting -------------#
#----------------------------------------#
def format_response(doc, resp, record, grouped):
    if grouped:
        id_lst = [x['metadata']['patient_id'] for x in record['documents']]
    else: 
        id_lst = [x['metadata']['document_id'] for x in record['documents']]
    r_form = {
        'ApiResponse': resp['ApiResponse'],
        'Edges': resp['pipeline']['Annotations']['edges'],
        'Encoding': resp['pipeline']['Annotations']['nodes'],
        'Narrative': resp['pipeline']['Narrative'],
        'MetaData': record['documents'][id_lst.index(doc)]['metadata']
        }
    
    filter_encode = [x for x in r_form['Encoding'] if x['NodeType']=='Encoding']
    filter_abstract = [x for x in r_form['Encoding'] if x['NodeType']=='Abstraction']
    r_form.update({
        'Encoding': filter_encode,
        'Abstraction': filter_abstract
        })
    return r_form

def flatten_response(resp):
    r_flat = []
    mrn = resp['MetaData']['patient_id']
    sname = resp['MetaData'].get('patient_surname', None)
    fname = resp['MetaData'].get('patient_forename', None)
    dob = resp['MetaData'].get('patient_dob', None)
    sex = resp['MetaData'].get('patient_gender', None)
    visid = resp['MetaData'].get('visit_id', None)
    docid = resp['MetaData'].get('document_id', None)
    proj = resp['MetaData']['project']
    auth = resp['MetaData'].get('author', None)
    #admit = resp['MetaData'].get('admission_date', None)
    obser = resp['MetaData'].get('observation_datetime', None)
    
    abstract_ids = [x['id'] for x in resp['Abstraction']]

    if args.abstractions:
        abs_lst = [y['elements'][0]['FeatureValue'] for y in resp['Abstraction']]
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
                    obser,
                    ','.join(set(abs_lst))
                    ])
        return r_flat

    for x in resp['Encoding']:
        abs_lst_ids = [
                y['from'] for y in resp['Edges'] \
                if y['to']==x['id'] \
                and y['from'] in abstract_ids
                ]
        abs_lst = [
                y['elements'][0]['FeatureValue'] for y in resp['Abstraction'] \
                if y['id'] in abs_lst_ids
                ]

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
                    obser,
                    x['elements'][0]['FeatureValue'],
                    x['id'],
                    x['start'],
                    x['end'],
                    resp['Narrative'][x['start']:x['end']+1],
                    ','.join(abs_lst)
                    ])
    return r_flat

out_json = {k: format_response(k, v, record, args.group) for k, v in req_responses.items()}
out_csv = [flatten_response(x) for x in out_json.values()]




#---------------- Export ----------------#
#----------------------------------------#
#args.outfile.write(json.dumps(out_json))

if args.abstractions:
    csv_header = ['patient_id','surname','forename','dob',
                'gender','visit_id','document_id','project',
                'author','observation_datetime','abstractions']
else:
    csv_header = ['patient_id','surname','forename','dob',
                'gender','visit_id','document_id','project',
                'author','observation_datetime','encoding',
                'encoding_id','enc_start','enc_end','orig_text','abstractions']

header_str = '\t'.join(csv_header)
flat_out_csv = [item for sublist in out_csv for item in sublist]
csv_str = '\n'.join(['\t'.join([str(y).replace('\n','') for y in x]) for x in flat_out_csv])
args.outfile.write(header_str + '\n' + csv_str)


