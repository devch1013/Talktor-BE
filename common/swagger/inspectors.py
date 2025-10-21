from drf_yasg.inspectors import SwaggerAutoSchema


class WrappedResponseAutoSchema(SwaggerAutoSchema):
    def get_response_schemas(self, response_serializers):
        responses = super().get_response_schemas(response_serializers)
        print(responses)

        # 200번대 응답을 wrapping
        for status_code, response in responses.items():
            print(status_code)
            try:
                if 200 <= int(status_code) < 300:
                    original_schema = response.get("schema", {})
                    responses[status_code]["schema"] = {
                        "type": "object",
                        "properties": {
                            "data": original_schema,
                            "status": {"type": "integer"},
                            "message": {"type": "string"},
                        },
                    }
            except ValueError:
                continue
        return responses
