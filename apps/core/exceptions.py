from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'success': False,
            'message': response.reason_phrase,
            'object': None,
        }

        if isinstance(response.data, dict):
            errors = [f"{field}: {', '.join(error_msgs)}" for field, error_msgs in response.data.items()]
            custom_response_data['errors'] = errors
        elif isinstance(response.data, list):
            custom_response_data['errors'] = response.data
        else:
            custom_response_data['errors'] = [str(response.data)]
            
        response.data = custom_response_data

    return response