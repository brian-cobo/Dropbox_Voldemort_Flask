import requests
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#replace with url of flask application
baseUrl = 'the_url_of_the_flask_app'

def getDocumentList():
    url = baseUrl + 'dropboxsign/signature_request/list/'
    data = {'email_address': 'hardcoded_email_for_hackathon_purposes'}
    response = requests.get(url, json=data).json()
    documentsToCheck = response['signature_requests']
    return response['signature_requests']


def getDocumentUrl(documentId):
    url = baseUrl + 'dropboxsign/signature_request/file_download_url/'
    data = {'signature_request_id': documentId}
    response = requests.get(url, json=data).json()
    fileUrlOfCurrentDoc = response['file_url']
    return fileUrlOfCurrentDoc


def getPdfTextThatBrianDidntTrimForMe(documentUrl):
    url = baseUrl + 'dropboxsign/pdfreader/'
    data = {'file_uri': documentUrl}
    response = requests.get(url, json=data).json()
    fileText = response['text']
    slightlyTrimmedText = fileText.replace('\n', '.')
    fullyTrimmedText = fileText.replace("_", "")
    return fileText


def summarizeDocument(documentText):
    url = baseUrl + 'chatgpt/summarize/'
    data = {'document_text': documentText}
    response = requests.get(url, json=data).json()
    summarizedText = response['text']
    return summarizedText


def translateDocument(documentText, language):
    print('translateDocument')
    print(language)
    url = baseUrl + 'chatgpt/translate'
    data = {
        'document_text': documentText,
        'trasnlate_to_what': language
    }
    response = requests.get(url, json=data).json()
    print(response)
    translatedText = response['text']
    return translatedText


def getListOfUnsignedDocuments(listOfDocuments):
    newListOfUnsignedDocuments = []
    for document in listOfDocuments:
        if not document.get('is_complete', False):
            newListOfUnsignedDocuments.append(document)
    return newListOfUnsignedDocuments


def getNextDocument(listOfDocuments, currentIndex):
    if len(currentDocument) < currentIndex:
        currentIndex += 1
    return listOfDocuments[currentIndex]


def incrementCurrentDocOrNot(masterListLength, currentIndex):
    if masterListLength > currentIndex + 1:
        currentIndex += 1
        return currentIndex
    else:
        return -1