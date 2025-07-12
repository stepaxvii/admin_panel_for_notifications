"""
Представление модели пользователей в админ-панели.
"""

from fastapi import Request
from starlette_admin.contrib.sqla import ModelView


class UserView(ModelView):
    """Представление модели пользователей в админ-панели."""
    
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa fa-users"
    
    can_export = False
    can_set_page_size = False
    page_size = 20

    def can_create(self, request):
        return False
    def can_edit(self, request):
        return False
    def can_delete(self, request):
        return False
    
    column_list = ["id", "name", "language", "language_code", "status", "blocked_at", "created_at"]
    column_searchable_list = ["name", "language", "language_code", "status"]
    column_sortable_list = ["id", "name", "language", "status", "created_at", "blocked_at"]
    
    column_labels = {
        "id": "ID",
        "name": "Имя",
        "language": "Язык",
        "language_code": "Код языка",
        "status": "Статус",
        "blocked_at": "Заблокирован",
        "created_at": "Зарегистрирован",
    }
    
    form_include_pk = False
    form_excluded_columns = ["id", "created_at", "updated_at", "blocked_at", "status"]
    form_columns = ["name", "language", "language_code"]
    
    form_widget_args = {
        "name": {"placeholder": "Введите имя пользователя..."},
        "language": {"placeholder": "ru"},
        "language_code": {"placeholder": "ru-RU"},
    }
    
    def get_form_fields(self, request: Request) -> list:
        """Возвращает поля для формы."""
        return ["name", "language", "language_code"]
    
    def get_create_form_fields(self, request: Request) -> list:
        """Возвращает поля для формы создания."""
        return ["name", "language", "language_code"]
    
    def get_edit_form_fields(self, request: Request) -> list:
        """Возвращает поля для формы редактирования."""
        return ["name", "language", "language_code"] 