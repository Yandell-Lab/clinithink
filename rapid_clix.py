import sys
import argparse
import json
import requests
import csv




#------------ Argument Parse ------------#
#----------------------------------------#
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', action='store')
parser.add_argument('-r', '--resource', action='store')
parser.add_argument('-k', '--apikey', action='store')
parser.add_argument('-s', '--apisecret', action='store')
parser.add_argument('-c', '--cacert', action='store')
args = parser.parse_args()




#-------------- Data Import -------------#
#----------------------------------------#
with open(args.file, 'r') as f:
    record = json.load(f)

payload = {'profileId': args.resource,
        'documents': [record['documents'][0]['data']]}




#------------- CNLP Request -------------#
#----------------------------------------#
server_add = 'https://edw-clix-d01.med.utah.edu:49120'
process_ep = '/api/v2.0/cnlp/process'
headers = {
        'api_key': args.apikey,
        'api_secret': args.apisecret,
        'Content-type': 'application/json'
        }

r = requests.post(
        server_add + process_ep, 
        headers = headers, 
        data = json.dumps(payload),
        verify = args.cacert)

rbody = json.loads(r.text)




#--------------- Formatting -------------#
#----------------------------------------#
r_form = {
        'ApiResponse': rbody['ApiResponse'],
        'Encoding': rbody['pipeline']['Annotations']['nodes'],
        'Narrative': rbody['pipeline']['Narrative'],
        'MetaData': record['documents'][0]['metadata']
        }

filter_encode = [x for x in r_form['Encoding'] if x['NodeType']=='Encoding']

r_form.update({'Encoding': filter_encode})

r_flat = []
mrn = r_form['MetaData']['patient_id']
sname = r_form['MetaData']['patient_surname']
fname = r_form['MetaData']['patient_forename']
dob = r_form['MetaData']['patient_dob']
sex = r_form['MetaData']['patient_gender']
docid = r_form['MetaData']['document_id']
proj = r_form['MetaData']['project']

for x in filter_encode:
    r_flat.append([
                mrn,
                sname,
                fname,
                dob,
                sex,
                docid,
                proj,
                x['elements'][0]['FeatureValue'],
                x['id'],
                x['start'],
                x['end'],
                r_form['Narrative'][x['start']:x['end']+1]
                ])




#---------------- Export ----------------#
#----------------------------------------#
with open('output.json', 'w') as f:
    json.dump(r_form, f)

with open('output.csv', 'w', newline='') as f:
    csv_header = ['patient_id','surname','forename','dob',
            'gender','document_id','project','encoding',
            'encoding_id','enc_start','enc_end','orig_text']

    writer = csv.writer(f)
    writer.writerow(csv_header)
    writer.writerows(r_flat)




