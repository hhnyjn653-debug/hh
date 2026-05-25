from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    ozon_client_id: str
    ozon_api_key: str
    ozon_base_url: str
    ms_username: str
    ms_password: str
    base_headless: bool



def _to_bool(value: str, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}



def load_settings() -> Settings:
    return Settings(
        ozon_client_id=os.getenv("OZON_CLIENT_ID", ""),
        ozon_api_key=os.getenv("OZON_API_KEY", ""),
        ozon_base_url=os.getenv("OZON_BASE_URL", "https://api-seller.ozon.ru"),
        ms_username=os.getenv("MS_USERNAME", ""),
        ms_password=os.getenv("MS_PASSWORD", ""),
        base_headless=_to_bool(os.getenv("BASE_HEADLESS"), True),
    )
