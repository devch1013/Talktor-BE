from rest_framework.renderers import JSONRenderer
from rest_framework.status import is_success


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict) and all(
            key in data for key in ["status", "message", "code"]
        ):
            return super().render(data, accepted_media_type, renderer_context)

        status_code = renderer_context["response"].status_code
        if data is None:
            data = {}

        response = {
            "status": status_code,
            "message": "success"
            if is_success(status_code)
            else data.get("message", "error"),
            "data": data,
        }

        return super().render(response, accepted_media_type, renderer_context)
