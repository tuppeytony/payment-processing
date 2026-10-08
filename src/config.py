from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Конфигурация приложения."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
        env_file=".env",
        env_ignore_empty=True,
    )

    title: str = "Payment processing service"
    debug: bool = False
    log_level: str = "INFO"
    x_api_key: str
    webhook_timeout: float = 10.0
    max_attempts: int = 3
    retry_base_delay_ms: int = 5000
    port: int = 8000
    host: str = "0.0.0.0"  # noqa: S104


class PostgresSettings(BaseSettings):
    """Конфигурация базы."""

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        extra="ignore",
        case_sensitive=False,
        env_file=".env",
        env_ignore_empty=True,
    )

    name: str
    password: str
    user: str
    driver: str = "postgresql+asyncpg"
    host: str
    port: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def dsn(self) -> str:
        """DSN базы данных."""
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RabbitSettings(BaseSettings):
    """Конфигурация rabbitmq."""

    model_config = SettingsConfigDict(
        env_prefix="RABBITMQ_",
        extra="ignore",
        case_sensitive=False,
        env_file=".env",
        env_ignore_empty=True,
    )

    default_user: str
    default_pass: str
    host: str
    port: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def dsn(self) -> str:
        """DSN rabbitmq."""
        return f"amqp://{self.default_user}:{self.default_pass}@{self.host}:{self.port}"


app_settings = AppSettings()
postgres_settings = PostgresSettings()
rabbit_settings = RabbitSettings()
