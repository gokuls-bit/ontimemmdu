from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """
    Standardized API JSON Response Renderer.
    Enforces unified envelope structure:
    Success: {"success": true, "data": ..., "meta": {"server_time": "...", "timezone": "Asia/Kolkata"}}
    Error: {"success": false, "error": {"code": "...", "message": "..."}}
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None
        status_code = response.status_code if response else 200

        # If data is already wrapped in standard envelope (e.g. from error handler), return directly
        if isinstance(data, dict) and ('success' in data):
            return super().render(data, accepted_media_type, renderer_context)

        if status_code >= 400:
            # Error response fallback
            error_msg = "An error occurred while processing your request."
            error_code = "API_ERROR"

            if isinstance(data, dict):
                if 'detail' in data:
                    error_msg = str(data['detail'])
                elif 'error' in data:
                    error_msg = str(data['error'])
                else:
                    error_msg = str(data)
            elif isinstance(data, str):
                error_msg = data

            envelope = {
                "success": False,
                "error": {
                    "code": error_code,
                    "message": error_msg
                }
            }
        else:
            # Success response
            envelope = {
                "success": True,
                "data": data if data is not None else {},
            }

        return super().render(envelope, accepted_media_type, renderer_context)
