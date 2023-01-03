class DatabaseException(Exception):
    """Ошибки связанные с базой данных"""


class ApiException(Exception):
    """Ошибки связанные с API"""
    bad_request = 'Неправильный запрос.'
    timeout_error = 'Время истекло.'
    no_result = 'Ничего не найдено.'
