# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_model.dialog import DelegateDirective

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
    AbstractExceptionHandler
)
from ask_sdk_core.handler_input import HandlerInput


from ask_sdk_model import Response, IntentRequest, LaunchRequest, SessionEndedRequest



from services import getDocumentList, getNextDocument, getListOfUnsignedDocuments, incrementCurrentDocOrNot, getDocumentUrl, getPdfTextThatBrianDidntTrimForMe, summarizeDocument, translateDocument
from s3Client import setKeyDictionary, getKeyDictionary, setKeyValue, getKeyValue, cleanOutBucket, setKeyString, getKeyString

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

number_of_docs_to_sign = 0
masterList = {}
listOfUnsignedDocs = {}
currentDocument = {}
currentDocIndex = 0
currentSummarizedText = {}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        
        return isinstance(handler_input.request_envelope.request, LaunchRequest)

    def handle(self, handler_input):
        print("Launch Request Handler")
        # type: (HandlerInput) -> Response
        #set values
        masterList = getDocumentList()
        currentDocument = masterList[currentDocIndex]
        listOfUnsignedDocs = getListOfUnsignedDocuments(masterList)
        
        speak_output = "Welcome to Document Signer, you can say 'Check my Queue' to get started."
        
        #set values in s3
        setKeyDictionary('masterList', masterList)
        setKeyDictionary('currentDocument', currentDocument)
        setKeyValue('currentDocIndex', currentDocIndex)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
                )
        
    
class CheckDocumentQueueIntent(AbstractRequestHandler):
    """Handler for Check Document Queue Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CheckDocumentQueueIntent")(handler_input)


    def handle(self, handler_input):
        print("Check Document Queue Intent")
        masterList = getDocumentList()
        currentDocument = masterList[currentDocIndex]
        listOfUnsignedDocs = getListOfUnsignedDocuments(masterList)
        # type: (HandlerInput) -> Response
        if len(listOfUnsignedDocs) > 0:
            speak_output = f'You have {len(listOfUnsignedDocs)} documents in queue to be signed, would you like to hear about the current document?'
        else:
            speak_output = "You have no documents in queue at this moment. Goodbye."

        setKeyDictionary('masterList', masterList)
        setKeyDictionary('currentDocument', currentDocument)
        setKeyValue('currentDocIndex', currentDocIndex)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("You can say, 'Sure, tell me about the current document'.")
                .response
                )


class GetDocumentDataIntent(AbstractRequestHandler):
    """Handler for Get Document Data Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetDocumentDataIntent")(handler_input)

    def handle(self, handler_input):
        print("Get Document Data Intent")
        # type: (HandlerInput) -> Response
        currentDocument = getKeyDictionary('currentDocument')
        speak_output = f"The first document is called {currentDocument['original_title']}, and the author has the message {currentDocument['message']}"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Would you like to read this document or move on to the next one? You can say, 'read this document' or 'move on to the next document'")
                .response
                )


class MoveOnToNextDocumentIntent(AbstractRequestHandler):
    """Handler for Move on To Next Document Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("MoveOnToNextDocumentIntent")(handler_input)

    def handle(self, handler_input):
        print('Move On To Next Document Intent')
        # type: (HandlerInput) -> Response
        #Get values
        masterList = getKeyDictionary('masterList')
        currentDocument = getKeyDictionary('currentDocument')
        currentDocIndex = getKeyValue('currentDocIndex')
        
        #continue logic
        currentDocIndex = incrementCurrentDocOrNot(len(masterList), currentDocIndex)
        currentDocument = masterList[currentDocIndex]
        
        if currentDocIndex == -1:
            speak_output = "There are no more documents to review."
            ask_output = "You can say 'exit' to exit the app."
        else:
            speak_output = f"The next document is called {currentDocument['original_title']}, and the author has the message {currentDocument['message']}"
            ask_output = "Would you like to read this document or move on to the next one? You can say, 'read this document' or 'move on to the next document'"
        
        setKeyDictionary('currentDocument', currentDocument)
        setKeyValue('currentDocIndex', currentDocIndex)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
                )


class ReadCurrentDocumentIntent(AbstractRequestHandler):
    """Handler for Read Current Document Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ReadCurrentDocumentIntent")(handler_input)

    def handle(self, handler_input):
        print("Read Current Document Intent")
        # type: (HandlerInput) -> Response
        # retrieve vars from s3
        currentDocument = getKeyDictionary('currentDocument')
        #logic
        currentDocUrl = getDocumentUrl(currentDocument['signature_request_id'])
        currentDocText = getPdfTextThatBrianDidntTrimForMe(currentDocUrl)
        
        speak_output = currentDocText
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Would you like me to repeat, summarize, or move on to the next document?")
                .response
                )



class SummarizeDocumentIntent(AbstractRequestHandler):
    """Handler for Read Current Document Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SummarizeDocumentIntent")(handler_input)

    def handle(self, handler_input):
        print("Summarize Document Intent")
        # type: (HandlerInput) -> Response
        # retrieve vars from s3
        currentDocument = getKeyDictionary('currentDocument')
        currentDocUrl = getDocumentUrl(currentDocument['signature_request_id'])
        currentDocText = getPdfTextThatBrianDidntTrimForMe(currentDocUrl)
        
        currentDocument = getKeyDictionary('currentDocument')
        #logic
        currentDocUrl = getDocumentUrl(currentDocument['signature_request_id'])
        currentDocText = getPdfTextThatBrianDidntTrimForMe(currentDocUrl)
        
        summarizedText = summarizeDocument(currentDocText)
        
        setKeyString('currentSummarizedText', summarizedText)
        
        speak_output = summarizedText
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Would you like me to repeat, or move on to the next document?")
                .response
                )


class TranslateIntent(AbstractRequestHandler):
    """Handler for Translate Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("TranslateIntent")(handler_input)

    def handle(self, handler_input):
        print("Translate Intent")
        # type: (HandlerInput) -> Response
        # retrieve vars from s3
        currentDocument = getKeyDictionary('currentDocument')
        currentDocUrl = getDocumentUrl(currentDocument['signature_request_id'])
        currentDocText = getPdfTextThatBrianDidntTrimForMe(currentDocUrl)
        
        currentDocument = getKeyDictionary('currentDocument')
        #logic
        
        slots = handler_input.request_envelope.request.intent.slots
        language = slots["language"].value if "language" in slots else None
        print(language)
        
        currentDocUrl = getDocumentUrl(currentDocument['signature_request_id'])
        currentDocText = getPdfTextThatBrianDidntTrimForMe(currentDocUrl)
        print("right before translation")
        
        translatedText = translateDocument(currentDocText, language)
        
        
        speak_output = translatedText
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Would you like me to repeat, or move on to the next document?")
                .response
                )


class TranslateSummaryIntent(AbstractRequestHandler):
    """Handler for Translate Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("TranslateSummaryIntent")(handler_input)

    def handle(self, handler_input):
        print("Translate Summary Intent")
        # type: (HandlerInput) -> Response
        # retrieve vars from s3
        currentSummarizedText =  getKeyString('currentSummarizedText')
        #logic
        
        slots = handler_input.request_envelope.request.intent.slots
        summaryLanguage = slots["summaryLanguage"].value if "summaryLanguage" in slots else None
        print(summaryLanguage)
        
        translatedText = translateDocument(currentSummarizedText, summaryLanguage)
        
        speak_output = translatedText
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Would you like me to repeat, or move on to the next document?")
                .response
                )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return isinstance(handler_input.request_envelope.request, SessionEndedRequest)

    def handle(self, handler_input):
        print("Session End Intent Handler")
        # type: (HandlerInput) -> Response
        cleanOutBucket()
        # Any cleanup logic goes here.

        return handler_input.response_builder.response




class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )



# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(ReadCurrentDocumentIntent())
sb.add_request_handler(CheckDocumentQueueIntent())
sb.add_request_handler(GetDocumentDataIntent())
sb.add_request_handler(MoveOnToNextDocumentIntent())
sb.add_request_handler(SummarizeDocumentIntent())
sb.add_request_handler(TranslateIntent())
sb.add_request_handler(TranslateSummaryIntent())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
# make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()