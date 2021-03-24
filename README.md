# clinithink
Tools for scripting CliniThink use with the CNLP API. The rapid_clix.py script takes a single JSON file containing clinical text in CliniThink document format (see test_cnlp_record.json). These text are packaged with metadata and API keys into HTTPS requests and sent to the CliniThink server for processing. Encodings are returned to the user in TSV format, although the raw JSON response can also be captured if necessary. CliniThink admins can provide user-specific API keys upon request.

## Usage
usage: rapid_clix.py [-h] [-f FILE] [-r RESOURCE] [-k APIKEY] -s APISECRET
                     [-c CACERT] [-g] [-a]
                     [outfile]

positional arguments:
  outfile               Provide name of output file. Default (-) writes to
                        stdout.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  JSON or zipped JSON file containing clinical
                        documents.
  -r RESOURCE, --resource RESOURCE
                        Name of resource set.
  -k APIKEY, --apikey APIKEY
                        User-specific API key from Clinithink.
  -s APISECRET, --apisecret APISECRET
                        User-specific secret key from Clinithink.
  -c CACERT, --cacert CACERT
                        File path of CA certificate (.pem) used for SSL
                        verification.
  -g, --group           Group documents by patient_id. Reduces number of
                        requests sent to server.
  -a, --abstractions    Only output list of abstractions instead of SNOMED-CT
                        encodings.
