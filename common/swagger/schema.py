from common.exceptions.exception_enum import CustomExceptionEnum


def get_swagger_response_dict(
    exception_enums: list[CustomExceptionEnum] = [],
    success_response=None,
) -> str:
    """
    swagger_auto_schema 함수내 responses 인자를 만들어 swagger에서 잘 보이도록 해줌
    :param api_exceptions: 해당 view에서 일어날 모든 exception의 List
    :param success_response: 성공 응답 http 코드 및 응답시 사용할 Serializer 정보를 담은 dict
    :return:
    """
    if success_response:
        result = success_response
    else:
        result = {}
    api_exception_str_info = {}

    if exception_enums:
        for exception_enum in exception_enums:
            if exception_enum.code in api_exception_str_info.keys():
                api_exception_str_info[exception_enum.code] += (
                    f'{{"detail" : "{exception_enum.detail}"}} // {exception_enum.description}\n\n'
                )
            else:
                api_exception_str_info[exception_enum.code] = (
                    f'{{"detail" : "{exception_enum.detail}"}} // {exception_enum.description}\n\n'
                )

    for k, v in api_exception_str_info.items():
        result[k] = v
    return result
