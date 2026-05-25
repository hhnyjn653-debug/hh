import argparse
import json

from src.automations.browser_flow import ms_login
from src.clients.ozon_client import OzonClient
from src.config import load_settings



def run_ozon_products() -> None:
    settings = load_settings()
    client = OzonClient(
        client_id=settings.ozon_client_id,
        api_key=settings.ozon_api_key,
        base_url=settings.ozon_base_url,
    )
    data = client.list_products(limit=20)
    print(json.dumps(data, ensure_ascii=False, indent=2))



def run_browser_login() -> None:
    settings = load_settings()
    ms_login(
        username=settings.ms_username,
        password=settings.ms_password,
        headless=settings.base_headless,
    )



def main() -> None:
    parser = argparse.ArgumentParser(description="Automation starter")
    parser.add_argument(
        "command",
        choices=["ozon-products", "browser-login"],
        help="choose one task",
    )
    args = parser.parse_args()

    if args.command == "ozon-products":
        run_ozon_products()
    elif args.command == "browser-login":
        run_browser_login()


if __name__ == "__main__":
    main()
