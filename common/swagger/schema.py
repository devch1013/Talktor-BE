from common.exceptions.exception_enum import CustomExceptionEnum


def get_swagger_response_dict(
    exception_enums: list[CustomExceptionEnum] = [],
    success_response=None,
) -> str:
    """
    swagger_auto_schema 함수내 responses 인자를 만들어 swagger에서 잘 보이도록 해줌

    응답 형태는 CustomJSONRenderer에 의해 래핑됩니다:
    {
        "status": <HTTP_STATUS_CODE>,
        "message": "success" | "error_message",
        "data": <SERIALIZER_DATA>
    }

    :param api_exceptions: 해당 view에서 일어날 모든 exception의 List
    :param success_response: 성공 응답 http 코드 및 응답시 사용할 Serializer 정보를 담은 dict
    :return:
    """
    result = {}
    if success_response:
        # for status_code, serializer in success_response.items():
        #     print(serializer)
        #     print(f"#/definitions/{serializer._meta.name}")
        #     if isinstance(status_code, int) and 200 <= status_code < 300:
        #         result[status_code] = openapi.Response(
        #             description="Success",
        #             schema=openapi.Schema(
        #                 type=openapi.TYPE_OBJECT,
        #                 properties={
        #                     "data": openapi.Schema(
        #                         type=openapi.TYPE_OBJECT,
        #                         ref=f"#/definitions/{serializer.__class__.__name__}",
        #                     ),
        #                     "status": openapi.Schema(type=openapi.TYPE_INTEGER),
        #                     "message": openapi.Schema(type=openapi.TYPE_STRING),
        #                 },
        #             ),
        #         )
        #     else:
        #         result[status_code] = serializer
        result = success_response
    api_exception_str_info = {}

    if exception_enums:
        for exception_enum in exception_enums:
            if exception_enum.code in api_exception_str_info.keys():
                api_exception_str_info[exception_enum.code] += (
                    f'{{"message" : "{exception_enum.message}", "code" : "{exception_enum.code}" }}\n\n'
                )
            else:
                api_exception_str_info[exception_enum.code] = (
                    f'{{"message" : "{exception_enum.message}", "code" : "{exception_enum.code}" }}\n\n'
                )

    for k, v in api_exception_str_info.items():
        result[k] = v
    return result
