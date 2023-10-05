from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 1440  # 1 day
    verification_token_expire_minutes: int = 1440


class DBSettings(BaseModel):
    host: str
    port: int = 5432
    username: str
    password: str
    name: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


class EMILSettings(BaseModel):
    USERNAME: str
    PASSWORD: str
    FROM: str
    PORT: int = 465
    SERVER: str = "smtp.gmail.com"
    SIGNUP_EMAIL_SUBJECT: str = 'Conform Your Registration'
    SIGNUP_EMAIL_BODY: str = """
    <p>Welcome, Please confirm your email by clicking this link:</p>
    <p><a href="{}">Click here to confirm</a></p>
    """


class AppSettings(BaseModel):
    name: str = "Flex AI"
    host: str = "0.0.0.0"
    port: int = 8080
    token_url: str = '/auth/token'
    url: str = "http://localhost:8080"
    auth_conform_url: str = f"{url}/auth/confirm?token={{}}"


class AuthProviderSettings(BaseModel):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str


class AuthSettings(BaseModel):
    COOKIE_NAME: str = 'Authorization'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter='__', extra='ignore')

    app_name: str = "Awesome API"
    admin_email: str
    items_per_user: int = 50

    app: AppSettings = AppSettings()
    db: DBSettings
    jwt: JWTSettings
    EMAIL: EMILSettings
    AUTH_PROVIDER: AuthProviderSettings
    AUTH: AuthSettings = AuthSettings()


settings = Settings()
