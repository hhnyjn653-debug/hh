import json
import os
import time
import urllib.error
import urllib.request
from typing import Dict, List, Any, Optional


class OpenClawClient:
    """OpenClaw/OpenCloud adapter with optional DeepSeek LLM planning."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout_seconds: int = 30,
        deepseek_api_key: Optional[str] = None,
        deepseek_model: str = "deepseek-chat",
        deepseek_base_url: str = "https://api.deepseek.com",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.deepseek_api_key = deepseek_api_key
        self.deepseek_model = deepseek_model
        self.deepseek_base_url = deepseek_base_url.rstrip("/")

    def _post_json(self, url: str, payload: Dict[str, Any], bearer_token: str) -> Dict[str, Any]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url=url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {bearer_token}")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {"ok": True}
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore")
            return {"ok": False, "error": f"HTTP {e.code}", "detail": detail}
        except urllib.error.URLError as e:
            return {"ok": False, "error": "NETWORK_ERROR", "detail": str(e)}

    def plan_with_deepseek(self, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Use DeepSeek to enrich task params before dispatching to OpenClaw/OpenCloud."""
        if not self.deepseek_api_key:
            return {"enabled": False}

        prompt = {
            "task": task_name,
            "payload": payload,
            "goal": "生成更可执行的平台动作参数，避免红海，优先蓝海需求与合规动作。",
            "output_schema": {
                "priority": "high|medium|low",
                "actions": ["string"],
                "risk_flags": ["string"],
                "optimized_payload": {"any": "json"},
            },
        }

        ds_payload = {
            "model": self.deepseek_model,
            "messages": [
                {"role": "system", "content": "你是中国电商增长与合规自动化助手。输出严格JSON。"},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        url = f"{self.deepseek_base_url}/chat/completions"
        resp = self._post_json(url=url, payload=ds_payload, bearer_token=self.deepseek_api_key)

        if not resp.get("choices"):
            return {"enabled": True, "ok": False, "raw": resp}

        try:
            content = resp["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return {"enabled": True, "ok": True, "plan": parsed}
        except (KeyError, json.JSONDecodeError, TypeError):
            return {"enabled": True, "ok": False, "raw": resp}

    def run_task(self, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ds_plan = self.plan_with_deepseek(task_name, payload)
        final_payload = payload
        if ds_plan.get("ok") and ds_plan.get("plan", {}).get("optimized_payload"):
            final_payload = ds_plan["plan"]["optimized_payload"]

        request_payload = {
            "task": task_name,
            "payload": final_payload,
            "planner": ds_plan,
        }

        endpoint_candidates = [
            f"{self.base_url}/api/v1/tasks/run",
            f"{self.base_url}/tasks/run",
        ]

        for url in endpoint_candidates:
            resp = self._post_json(url=url, payload=request_payload, bearer_token=self.api_key)
            if resp.get("ok") is False and resp.get("error", "").startswith("HTTP 404"):
                continue
            if resp.get("ok") is False:
                return resp
            return {"ok": True, "task": task_name, "result": resp}

        return {"ok": False, "error": "NO_VALID_ENDPOINT", "detail": endpoint_candidates}


class BlueOceanEngine:
    @staticmethod
    def score(niche: Dict[str, Any]) -> float:
        demand = niche.get("demand", 0)
        competition = niche.get("competition", 1)
        margin = niche.get("margin", 0)
        freshness = niche.get("freshness", 0)
        return (demand * 0.4) + (margin * 0.25) + (freshness * 0.25) - (competition * 0.3)

    def pick(self, candidates: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        ranked = sorted(candidates, key=self.score, reverse=True)
        return ranked[:top_k]


class GrowthOrchestrator:
    def __init__(self, oc: OpenClawClient, config: Dict[str, Any]):
        self.oc = oc
        self.config = config
        self.engine = BlueOceanEngine()

    def initialize_brand(self):
        for p in self.config["platforms"]:
            self.oc.run_task("setup_profile", {
                "platform": p["platform"],
                "positioning": self.config["positioning"],
                "bio_rules": self.config["bio_rules"],
                "visual_rules": self.config["visual_rules"],
            })

    def market_scan(self):
        signals = []
        for p in self.config["platforms"]:
            r = self.oc.run_task("scan_market", {
                "platform": p["platform"],
                "seed_categories": self.config["seed_categories"],
                "price_range": self.config["price_range"],
            })
            signals.extend(r.get("result", {}).get("signals", []))

        if not signals:
            signals = self.config.get("fallback_signals", [])

        return self.engine.pick(signals, top_k=self.config.get("top_k", 3))

    def launch_products(self, niches: List[Dict[str, Any]]):
        for n in niches:
            for p in self.config["platforms"]:
                self.oc.run_task("publish_product", {
                    "platform": p["platform"],
                    "niche": n,
                    "price_policy": self.config["pricing_policy"],
                    "listing_template": self.config["listing_template"],
                })

    def optimize_traffic(self):
        for p in self.config["platforms"]:
            self.oc.run_task("enroll_official_campaigns", {
                "platform": p["platform"],
                "fit_threshold": self.config["campaign_fit_threshold"],
                "positioning": self.config["positioning"],
            })
            self.oc.run_task("boost_seo_keywords", {
                "platform": p["platform"],
                "keyword_policy": self.config["keyword_policy"],
            })

    def auto_sales_and_support(self):
        for p in self.config["platforms"]:
            self.oc.run_task("auto_reply", {"platform": p["platform"], "rules": self.config["crm_rules"]})
            self.oc.run_task("after_sales_feedback_loop", {
                "platform": p["platform"],
                "survey_rules": self.config["feedback_rules"],
            })

    def run_daily(self):
        self.initialize_brand()
        niches = self.market_scan()
        self.launch_products(niches)
        self.optimize_traffic()
        self.auto_sales_and_support()


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    cfg = load_config(os.getenv("CONFIG_PATH", "configs/system_config.json"))
    oc = OpenClawClient(
        base_url=os.getenv("OPENCLOW_BASE_URL", "http://localhost:8080"),
        api_key=os.getenv("OPENCLOW_API_KEY", "demo-key"),
        timeout_seconds=int(os.getenv("OPENCLOW_TIMEOUT_SECONDS", "30")),
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )
    GrowthOrchestrator(oc, cfg).run_daily()
    time.sleep(0.1)
