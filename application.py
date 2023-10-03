from flask import Flask, request
import requests
import json
from PDFReaderService import PDFReaderService
from chamber_of_secrets import get_secret

application = Flask(__name__)

dropbox_client_secret = get_secret('DROPBOX_SIGN_API_SECRET')
dropbox_sign_api_uri = f"https://{dropbox_client_secret}:@api.hellosign.com/v3/"

@application.route('/')
def hello_world():
    return 'Hello World!'


@application.route('/dropboxsign/account/')
def get_dropbox_sign_account():
    if request.method == 'GET':
        email_address = (request.json).get('email_address')

        if not email_address:
            return {'error': 'missing values in body'}, 400
        else:
            email_address = email_address.replace('@', '%40')
            dropbox_endpoint_uri = f'account?email_address={email_address}'

        try:
            request_url = f'{dropbox_sign_api_uri}{dropbox_endpoint_uri}'
            response = requests.get(request_url)
            json_response_body = json.loads(response.content)
            return json_response_body, 200
        except Exception as e:
            print("Exception when calling Dropbox Sign API: %s\n" % e)


@application.route('/dropboxsign/signature_request/list/')
def get_signature_request_list():
    if request.method == 'GET':
        email_address = (request.json).get('email_address')

        if not email_address:
            return {'error': 'missing values in body'}, 400
        else:
            try:
                account_id = get_dropbox_sign_account()[0]['account']['account_id']
                dropbox_endpoint_uri = f'signature_request/list?account_id={account_id}'
                request_url = f'{dropbox_sign_api_uri}{dropbox_endpoint_uri}'
                response = requests.get(request_url)
                json_response_body = json.loads(response.content)
                return json_response_body, 200
            except Exception as e:
                print("Exception when calling Dropbox Sign API: %s\n" % e)


@application.route('/dropboxsign/signature_request/')
def get_signature_request():
    if request.method == 'GET':
        signature_request_id = (request.json).get('signature_request_id')

        if not signature_request_id:
            return {'error': 'missing values in body'}, 400
        else:
            try:
                dropbox_endpoint_uri = f'signature_request/{signature_request_id}'
                request_url = f'{dropbox_sign_api_uri}{dropbox_endpoint_uri}'
                response = requests.get(request_url)
                json_response_body = json.loads(response.content)
                return json_response_body, 200
            except Exception as e:
                print("Exception when calling Dropbox Sign API: %s\n" % e)


@application.route('/dropboxsign/signature_request/file_download_url/')
def get_file_download_uri():
    if request.method == 'GET':
        signature_request_id = (request.json).get('signature_request_id')

        if not signature_request_id:
            return {'error': 'missing values in body'}, 400
        else:
            try:
                dropbox_endpoint_uri = f'signature_request/files_as_file_url/{signature_request_id}'
                request_url = f'{dropbox_sign_api_uri}{dropbox_endpoint_uri}'
                response = requests.get(request_url)
                json_response_body = json.loads(response.content)
                return json_response_body, 200
            except Exception as e:
                print("Exception when calling Dropbox Sign API: %s\n" % e)

@application.route('/dropboxsign/pdfreader/')
def get_text_from_pdf():
    if request.method == 'GET':
        file_uri = (request.json).get('file_uri')

        if not file_uri:
            return {'error': 'missing values in body'}, 400
        else:
            try:
                _pdf_reader = PDFReaderService()
                return _pdf_reader.get_text_from_pdf(file_uri), 200
            except Exception as e:
                print("Exception when calling Dropbox Sign API: %s\n" % e)


if __name__ == '__main__':
    application.run()
