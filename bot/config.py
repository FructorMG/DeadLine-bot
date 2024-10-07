from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: str
    CHAT_ID : str
    support_id: str  # Сохраняем как строку
    admin_ids: str    # Сохраняем как строку
    super_user_ids: str  # Сохраняем как строку
    DATABASE_URL: str

    @property
    def admins_list(self) -> List[int]:
        return [int(id_.strip()) for id_ in self.admin_ids.split(',') if id_.strip().isdigit()]

    @property
    def assistants_list(self) -> List[int]:
        return [str(id_.strip()) for id_ in self.support_id.split(',') if id_.strip().isdigit()]

    @property
    def super_users_list(self) -> List[int]:
        return [int(id_.strip()) for id_ in self.super_user_ids.split(',') if id_.strip().isdigit()]

    class Config:
        env_file = ".env"

config = Settings()
