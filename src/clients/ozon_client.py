from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class OzonClient:
    client_id: str
    api_key: str
    base_url: str = "https://api-seller.ozon.ru"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def list_products(self, limit: int = 20) -> dict[str, Any]:
        # 公开常用 endpoint（具体字段以你账号版本为准）
        payload = {
            "filter": {"visibility": "ALL"},
            "last_id": "",
            "limit": limit,
        }
        return self.post("v3/product/list", payload)
