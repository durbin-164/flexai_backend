from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 1440  # 1 day


class DBSettings(BaseModel):
    host: str
    port: int = 5432
    username: str
    password: str
    name: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


class AppSettings(BaseModel):
    name: str = "Flex AI"
    host: str = "0.0.0.0"
    port: int = 8080
    token_url: str = '/auth/token'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter='__', extra='ignore')

    app_name: str = "Awesome API"
    admin_email: str
    items_per_user: int = 50

    app: AppSettings = AppSettings()
    db: DBSettings
    jwt: JWTSettings


settings = Settings()
