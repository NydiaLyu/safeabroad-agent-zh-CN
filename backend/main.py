import os
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.agents.case_intake_agent import CaseIntakeAgent
from backend.agents.safety_triage_agent import SafetyTriageAgent, TriagePayload
from backend.models.case_state import CaseState
from backend.services.workflow_service import CaseWorkflowService


app = FastAPI(title="SafeAbroad Agent MVP")
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
cases: Dict[str, CaseState] = {}
intake_agent = CaseIntakeAgent()
triage_agent = SafetyTriageAgent()
workflow = CaseWorkflowService()


@app.middleware("http")
async def apply_llm_headers(request: Request, call_next):
    provider = request.headers.get("x-llm-provider")
    api_key = request.headers.get("x-llm-api-key")
    model = request.headers.get("x-llm-model")
    base_url = request.headers.get("x-llm-base-url")
    if provider:
        os.environ["LLM_PROVIDER"] = provider
    if model:
        os.environ["LLM_MODEL"] = model
    if base_url:
        os.environ["LLM_BASE_URL"] = base_url
    if api_key:
        os.environ["LLM_API_KEY"] = api_key
        if provider == "qwen":
            os.environ["DASHSCOPE_API_KEY"] = api_key
        elif provider == "openai":
            os.environ["OPENAI_API_KEY"] = api_key
        elif provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = api_key
    if provider == "qwen":
        if model:
            os.environ["QWEN_MODEL"] = model
        if base_url:
            os.environ["QWEN_BASE_URL"] = base_url
    return await call_next(request)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/settings/qwen")
def get_qwen_settings() -> dict:
    key = os.getenv("DASHSCOPE_API_KEY", "")
    return {
        "configured": bool(key),
        "suffix": key[-4:] if key else "",
        "model": os.getenv("QWEN_MODEL", "qwen-plus"),
    }


@app.get("/api/settings/llm")
def get_llm_settings() -> dict:
    provider = os.getenv("LLM_PROVIDER", "qwen")
    key_by_provider = {
        "qwen": os.getenv("DASHSCOPE_API_KEY", ""),
        "openai": os.getenv("OPENAI_API_KEY", ""),
        "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
        "openai_compatible": os.getenv("LLM_API_KEY", ""),
    }
    key = key_by_provider.get(provider, "")
    return {
        "configured": bool(key),
        "provider": provider,
        "suffix": key[-4:] if key else "",
        "model": os.getenv("LLM_MODEL") or os.getenv("QWEN_MODEL", "qwen-plus"),
        "base_url": os.getenv("LLM_BASE_URL") or os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    }


@app.post("/api/settings/llm")
def save_llm_settings(payload: dict) -> dict:
    provider = str(payload.get("provider", "qwen")).strip()
    api_key = str(payload.get("api_key", "")).strip()
    model = str(payload.get("model", "")).strip()
    base_url = str(payload.get("base_url", "")).strip()
    if not api_key:
        return {"configured": False, "error": "API Key 不能为空。"}

    defaults = {
        "qwen": ("qwen-plus", "https://dashscope.aliyuncs.com/compatible-mode/v1", "DASHSCOPE_API_KEY"),
        "openai": ("gpt-4.1-mini", "https://api.openai.com/v1", "OPENAI_API_KEY"),
        "anthropic": ("claude-3-5-sonnet-latest", "https://api.anthropic.com", "ANTHROPIC_API_KEY"),
        "openai_compatible": ("", "", "LLM_API_KEY"),
    }
    default_model, default_base_url, env_key_name = defaults.get(provider, defaults["qwen"])
    model = model or default_model
    base_url = base_url or default_base_url

    os.environ["LLM_PROVIDER"] = provider
    os.environ["LLM_MODEL"] = model
    os.environ["LLM_BASE_URL"] = base_url
    os.environ[env_key_name] = api_key

    if provider == "qwen":
        os.environ["DASHSCOPE_API_KEY"] = api_key
        os.environ["QWEN_MODEL"] = model
        os.environ["QWEN_BASE_URL"] = base_url
    elif provider == "openai":
        os.environ["OPENAI_API_KEY"] = api_key
    elif provider == "anthropic":
        os.environ["ANTHROPIC_API_KEY"] = api_key

    lines = [
        f"LLM_PROVIDER={provider}",
        f"{env_key_name}={api_key}",
        f"LLM_MODEL={model}",
        f"LLM_BASE_URL={base_url}",
        "SAFEABROAD_STORAGE_PATH=./data",
    ]
    if provider == "qwen":
        lines.extend(
            [
                f"DASHSCOPE_API_KEY={api_key}",
                f"QWEN_BASE_URL={base_url}",
                f"QWEN_MODEL={model}",
            ]
        )
    Path(".env").write_text("\n".join(lines + [""]), encoding="utf-8")
    return {"configured": True, "provider": provider, "suffix": api_key[-4:], "model": model, "base_url": base_url}


@app.post("/api/settings/qwen")
def save_qwen_settings(payload: dict) -> dict:
    api_key = str(payload.get("api_key", "")).strip()
    model = str(payload.get("model", "qwen-plus")).strip() or "qwen-plus"
    if not api_key.startswith("sk-"):
        return {"configured": False, "error": "API Key 应以 sk- 开头。"}

    os.environ["LLM_PROVIDER"] = "qwen"
    os.environ["DASHSCOPE_API_KEY"] = api_key
    os.environ["QWEN_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    os.environ["QWEN_MODEL"] = model

    env_path = Path(".env")
    env_path.write_text(
        "\n".join(
            [
                "LLM_PROVIDER=qwen",
                f"DASHSCOPE_API_KEY={api_key}",
                "QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1",
                f"QWEN_MODEL={model}",
                "SAFEABROAD_STORAGE_PATH=./data",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {"configured": True, "suffix": api_key[-4:], "model": model}


@app.get("/", response_class=HTMLResponse)
def app_home() -> str:
    with open("backend/static/index.html", "r", encoding="utf-8") as file:
        return file.read()


@app.post("/api/cases")
def create_case(payload: dict = None) -> CaseState:
    case = intake_agent.create_case()
    payload = payload or {}
    profile = payload.get("user_profile", {})
    jurisdiction = payload.get("jurisdiction", {})
    police = payload.get("police", {})
    for key, value in profile.items():
        if hasattr(case.user_profile, key):
            setattr(case.user_profile, key, value)
    for key, value in jurisdiction.items():
        if hasattr(case.jurisdiction, key):
            setattr(case.jurisdiction, key, value)
    for key, value in police.items():
        if hasattr(case.police, key):
            setattr(case.police, key, value)
    cases[case.case_id] = case
    return case


@app.get("/api/cases/{case_id}")
def get_case(case_id: str) -> CaseState:
    return cases[case_id]


@app.post("/api/cases/{case_id}/triage")
def triage(case_id: str, payload: TriagePayload) -> dict:
    result = triage_agent.classify(payload)
    cases[case_id].current_risk_level = result["risk_level"]
    return result


@app.post("/api/cases/{case_id}/interview/free-narrative")
def free_narrative(case_id: str, payload: dict) -> dict:
    return workflow.submit_free_narrative(cases[case_id], payload["narrative"])


@app.post("/api/cases/{case_id}/interview/answer")
def interview_answer(case_id: str, payload: dict) -> dict:
    return workflow.submit_interview_answer(cases[case_id], payload["answer"])


@app.post("/api/cases/{case_id}/interview/finish")
def finish_interview(case_id: str) -> dict:
    return workflow.finish_followup(cases[case_id])


@app.post("/api/cases/{case_id}/timeline/update")
def update_timeline(case_id: str, payload: dict) -> dict:
    return workflow.update_timeline(cases[case_id], payload.get("events", []))


@app.get("/api/cases/{case_id}/timeline/reconstruct")
def reconstruct_timeline(case_id: str) -> dict:
    return workflow.reconstruct_case_story(cases[case_id])


@app.post("/api/cases/{case_id}/interview/finalize-review")
def finalize_followup_review(case_id: str, payload: dict) -> dict:
    return workflow.finalize_followup_review(cases[case_id], payload.get("uncertain_event_ids", []))


@app.post("/api/cases/{case_id}/evidence/evaluate")
def evaluate_evidence(case_id: str, payload: dict = None) -> dict:
    payload = payload or {}
    return workflow.evaluate_evidence(cases[case_id], payload.get("note", ""))


@app.get("/api/cases/{case_id}/support/guidance")
def support_guidance(case_id: str) -> dict:
    return workflow.support_guidance(cases[case_id])


@app.post("/api/cases/{case_id}/documents/generate")
def generate_documents(case_id: str) -> dict:
    return workflow.generate_outputs(cases[case_id])


@app.post("/api/cases/{case_id}/documents/review")
def review_documents(case_id: str, payload: dict) -> dict:
    case = cases[case_id]
    reviewed_documents = payload.get("documents", {})
    for document in case.generated_documents:
        if document.document_type in reviewed_documents:
            item = reviewed_documents[document.document_type]
            document.content = item.get("content", document.content)
            document.reviewed_by_user = bool(item.get("reviewed_by_user", False))
    case.reviewed_by_user = all(document.reviewed_by_user for document in case.generated_documents)
    return {"case_id": case.case_id, "reviewed_by_user": case.reviewed_by_user, "documents": case.generated_documents}
