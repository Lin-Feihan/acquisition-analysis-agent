"""Responses API transport, adapted from the existing ATL research service."""
from dataclasses import dataclass, field
import math
import os
import time


@dataclass
class ResearchResult:
    text: str
    provider: str
    citations: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("Research result text cannot be empty.")


def plain(value):
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return {}


def parse_response(response, provider, model):
    data = plain(response)
    text_parts, citations, sources, steps = [], [], [], []
    for item in data.get("output", []) or []:
        kind = item.get("type", "")
        if kind == "message":
            for part in item.get("content", []) or []:
                if part.get("type") != "output_text":
                    continue
                text_parts.append(part.get("text", ""))
                for annotation in part.get("annotations", []) or []:
                    if annotation.get("type") != "url_citation":
                        continue
                    c = annotation.get("url_citation", annotation)
                    if not c.get("url"):
                        continue
                    citation = {key: c.get(key) for key in ("url", "title", "start_index", "end_index")}
                    citation.update(type="url_citation", message_id=item.get("id"))
                    citations.append(citation)
                    sources.append({"url": c["url"], "title": c.get("title"), "origin": "citation"})
        elif kind == "web_search_call":
            action = item.get("action") or {}
            steps.append({"type": kind, "id": item.get("id"), "status": item.get("status"), "action": action})
            for source in action.get("sources", []) or []:
                if source.get("url"):
                    sources.append({"url": source["url"], "title": source.get("title"), "origin": "web_search"})
        elif kind.endswith("_call"):
            # Tool outputs are execution evidence, not private reasoning summaries.
            steps.append(item)
    by_url = {}
    for source in sources:
        existing = by_url.setdefault(source["url"], source.copy())
        if not existing.get("title") and source.get("title"):
            existing["title"] = source["title"]
    text = getattr(response, "output_text", None) or data.get("output_text") or "\n".join(text_parts)
    usage = data.get("usage") or {}
    actual_cost = usage.get("actual_cost_micro", data.get("actual_cost_micro"))
    return ResearchResult(text=text, provider=provider, citations=citations,
                          sources=list(by_url.values()), metadata={
                              "response_id": data.get("id"), "model": data.get("model") or model,
                              "status": data.get("status"), "usage": usage,
                              "actual_cost_micro": actual_cost, "research_steps": steps,
                          })


class OpenAIResearchProvider:
    def __init__(self, api_key, config=None, *, client=None, clock=time.monotonic, sleep=time.sleep):
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("A research API key is required.")
        self.api_key = api_key.strip()
        self.config = config or {}
        self.base_url = os.getenv("OPENAI_BASE_URL", "").strip()
        self.model = os.getenv("RESEARCH_MODEL", "").strip() or self.config.get("model")
        if not self.model:
            raise ValueError("Set RESEARCH_MODEL for this research service.")
        self.provider_name = "commonstack" if self.base_url else "openai"
        self.clock, self.sleep = clock, sleep
        self.timeout = float(self.config.get("timeout_seconds", 1800))
        self.poll_interval = float(self.config.get("poll_interval_seconds", 10))
        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError("timeout_seconds must be positive and finite.")
        if not math.isfinite(self.poll_interval) or self.poll_interval <= 0:
            raise ValueError("poll_interval_seconds must be positive and finite.")
        self.client = client

    def run(self, prompt):
        if self.client is None:
            from openai import OpenAI
            kwargs = {"api_key": self.api_key, "timeout": self.timeout, "max_retries": 0}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self.client = OpenAI(**kwargs)
        tools = [{"type": "web_search" if self.base_url else self.config.get("web_search_tool", "web_search_preview")}]
        # Off by default: enable only when the selected endpoint/model supports it.
        if self.config.get("enable_code_interpreter", False):
            tools.append({"type": "code_interpreter", "container": {"type": "auto"}})
        request = {"model": self.model, "input": prompt, "tools": tools,
                   "include": ["web_search_call.action.sources"]}
        if not self.base_url:
            request["background"] = True
        start = self.clock()
        try:
            response = self.client.responses.create(**request)
            data = plain(response)
            while data.get("status") in {"queued", "in_progress"}:
                if self.base_url:
                    raise RuntimeError("Gateway returned an unfinished response; synchronous completion is required.")
                remaining = self.timeout - (self.clock() - start)
                if remaining <= 0:
                    response_id = data.get("id")
                    try:
                        self.client.responses.cancel(response_id)
                    except Exception:
                        pass
                    raise TimeoutError("Research wait limit reached; remote cancellation was attempted but is not guaranteed.")
                self.sleep(min(self.poll_interval, remaining))
                response = self.client.responses.retrieve(data["id"],
                    include=["web_search_call.action.sources"])
                data = plain(response)
            status = data.get("status")
            if status != "completed" and not (self.base_url and status is None):
                raise RuntimeError(f"Research ended with status: {status}")
            result = parse_response(response, self.provider_name, self.model)
            result.metadata["requested_tools"] = tools
            return result
        except (RuntimeError, TimeoutError):
            raise
        except Exception as exc:
            # Never print provider exception bodies: they can contain request secrets.
            raise RuntimeError(f"Research request failed ({type(exc).__name__}); check service credentials and configuration.") from None


def get_provider(provider_name="openai", api_key=None, config=None):
    if provider_name not in {"openai", "commonstack"}:
        raise ValueError("Supported providers: openai, commonstack.")
    if provider_name == "commonstack" and not os.getenv("OPENAI_BASE_URL", "").strip():
        raise ValueError("CommonStack requires OPENAI_BASE_URL.")
    return OpenAIResearchProvider(api_key or os.getenv("OPENAI_API_KEY", ""), config)
