from common.exceptions.exception_enum import CustomExceptionEnum


class CustomException(Exception):
    def __init__(self, error_code: CustomExceptionEnum):
        self.message = error_code.message
        self.status_code = error_code.status
        self.code = error_code.code
        super().__init__(self.message)
