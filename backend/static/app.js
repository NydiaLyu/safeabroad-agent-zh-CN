const state = {
  caseId: null,
  documents: {},
  currentGap: null,
  evidenceEvaluated: false,
  timeline: [],
};

const $ = (id) => document.getElementById(id);

const labels = {
  police_statement: "给警察的英文陈述草稿",
  police_followup: "给警察的跟进短信/邮件",
  medical_summary: "给医生或诊所的英文就诊摘要",
  university_support_email: "给学校 Student Support 的英文邮件",
};

const providerPresets = {
  qwen: {
    label: "阿里云百炼 / 通义千问",
    keyName: "DASHSCOPE_API_KEY",
    model: "qwen-plus",
    baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    placeholder: "sk-...",
  },
  openai: {
    label: "OpenAI",
    keyName: "OPENAI_API_KEY",
    model: "gpt-4.1-mini",
    baseUrl: "https://api.openai.com/v1",
    placeholder: "sk-...",
  },
  anthropic: {
    label: "Anthropic",
    keyName: "ANTHROPIC_API_KEY",
    model: "claude-3-5-sonnet-latest",
    baseUrl: "https://api.anthropic.com",
    placeholder: "sk-ant-...",
  },
  openai_compatible: {
    label: "自定义 OpenAI-compatible",
    keyName: "API_KEY",
    model: "",
    baseUrl: "",
    placeholder: "输入服务商 API Key",
  },
};

function applyProviderPreset(provider, overwrite = false) {
  const preset = providerPresets[provider] || providerPresets.qwen;
  $("apiProviderSelect").value = provider;
  $("apiKeyInput").placeholder = preset.placeholder;
  if (overwrite || !$("apiModelInput").value) $("apiModelInput").value = preset.model;
  if (overwrite || !$("apiBaseUrlInput").value) $("apiBaseUrlInput").value = preset.baseUrl;
}

function loadApiSettings() {
  const provider = localStorage.getItem("safeabroad_llm_provider") || "qwen";
  const apiKey = localStorage.getItem("safeabroad_llm_api_key") || localStorage.getItem("safeabroad_dashscope_api_key") || "";
  const model = localStorage.getItem("safeabroad_llm_model") || localStorage.getItem("safeabroad_qwen_model") || providerPresets[provider]?.model || "qwen-plus";
  const baseUrl = localStorage.getItem("safeabroad_llm_base_url") || providerPresets[provider]?.baseUrl || "";
  applyProviderPreset(provider);
  $("apiKeyInput").value = apiKey;
  $("apiModelInput").value = model;
  $("apiBaseUrlInput").value = baseUrl;
  $("apiSettingsStatus").textContent = apiKey
    ? `浏览器本地已保存 ${providerPresets[provider]?.label || provider} key，尾号：${apiKey.slice(-4)}，模型：${model}`
    : "尚未填写 API Key。";
}

function apiHeaders() {
  const provider = localStorage.getItem("safeabroad_llm_provider");
  const apiKey = localStorage.getItem("safeabroad_llm_api_key") || localStorage.getItem("safeabroad_dashscope_api_key");
  const model = localStorage.getItem("safeabroad_llm_model") || localStorage.getItem("safeabroad_qwen_model");
  const baseUrl = localStorage.getItem("safeabroad_llm_base_url");
  const headers = {};
  if (provider) headers["X-LLM-Provider"] = provider;
  if (apiKey) headers["X-LLM-Api-Key"] = apiKey;
  if (model) headers["X-LLM-Model"] = model;
  if (baseUrl) headers["X-LLM-Base-Url"] = baseUrl;
  if (apiKey) headers["X-DashScope-Api-Key"] = apiKey;
  if (model) headers["X-Qwen-Model"] = model;
  return headers;
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...apiHeaders(), ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

$("apiSettingsBtn").addEventListener("click", () => {
  loadApiSettings();
  $("apiModal").classList.remove("hidden");
});

$("closeApiModalBtn").addEventListener("click", () => {
  $("apiModal").classList.add("hidden");
});

$("apiProviderSelect").addEventListener("change", () => {
  applyProviderPreset($("apiProviderSelect").value, true);
});

document.querySelectorAll("[data-provider-preset]").forEach((button) => {
  button.addEventListener("click", () => applyProviderPreset(button.dataset.providerPreset, true));
});

$("saveApiSettingsBtn").addEventListener("click", async () => {
  const provider = $("apiProviderSelect").value;
  const apiKey = $("apiKeyInput").value.trim();
  const model = $("apiModelInput").value.trim();
  const baseUrl = $("apiBaseUrlInput").value.trim();
  if (!apiKey) {
    $("apiSettingsStatus").textContent = "请填写 API Key。";
    return;
  }

  localStorage.setItem("safeabroad_llm_provider", provider);
  localStorage.setItem("safeabroad_llm_api_key", apiKey);
  localStorage.setItem("safeabroad_llm_model", model);
  localStorage.setItem("safeabroad_llm_base_url", baseUrl);
  if (provider === "qwen") {
    localStorage.setItem("safeabroad_dashscope_api_key", apiKey);
    localStorage.setItem("safeabroad_qwen_model", model);
  }
  $("apiSettingsStatus").textContent = `已保存到浏览器本地，尾号：${apiKey.slice(-4)}。正在尝试同步到后端...`;

  try {
    const result = await request("/api/settings/llm", {
      method: "POST",
      body: JSON.stringify({ provider, api_key: apiKey, model, base_url: baseUrl }),
    });
    $("apiSettingsStatus").textContent = result.configured
      ? `已保存并同步到后端：${result.provider}，尾号：${result.suffix}，模型：${result.model}`
      : `已保存到浏览器，但后端未接受：${result.error || "未知错误"}`;
  } catch (error) {
    $("apiSettingsStatus").textContent =
      "已保存到浏览器本地。后续 agent 请求会自动携带这组 API 配置；如果后端设置接口暂不可用，也不影响本页后续请求使用。";
  }
});

async function ensureCase() {
  if (state.caseId) return state.caseId;
  const payload = {
    user_profile: {
      name: $("name").value,
      university: $("university").value,
    },
    jurisdiction: {
      country: $("country").value,
      state: $("state").value,
      city: $("city").value,
      jurisdiction_id: `${$("country").value === "Australia" ? "AU" : $("country").value}-${$("state").value || "LOCAL"}`,
    },
    police: {
      reported: Boolean($("eventNumber").value),
      event_number: $("eventNumber").value,
    },
  };
  const created = await request("/api/cases", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  state.caseId = created.case_id;
  return state.caseId;
}

function showTriage(result) {
  const lines = [
    `风险等级：${result.risk_level}`,
    `建议动作：${result.action}`,
    `紧急电话：${result.emergency_number}`,
    `英文求助句：${result.script}`,
  ];
  $("triageResult").textContent = lines.join("\n");
}

function showNarrativeTriage(result) {
  if (!result) return;
  const lines = [
    "【中文讲述后二次分流】",
    `风险等级：${result.risk_level}`,
    result.message_zh || "",
    `建议动作：${result.action}`,
    `紧急电话：${result.emergency_number}`,
    `英文求助句：${result.script}`,
  ];
  $("triageResult").textContent = lines.filter(Boolean).join("\n");
}

function showTimeline(events) {
  state.timeline = events || [];
  $("timeline").innerHTML = "";
  state.timeline.forEach((event, index) => {
    const li = document.createElement("li");
    li.className = "timeline-row";
    li.draggable = true;
    li.dataset.index = index;
    li.innerHTML = `
      <div class="drag-handle" title="拖动调整顺序">${index + 1}</div>
      <input class="timeline-description" value="${escapeHtml(event.description_zh || "")}" aria-label="事件描述" />
      <select class="timeline-certainty" aria-label="确定性">
        <option value="confirmed"${event.certainty === "confirmed" ? " selected" : ""}>确定</option>
        <option value="approximate"${event.certainty === "approximate" ? " selected" : ""}>大概</option>
        <option value="uncertain"${event.certainty === "uncertain" ? " selected" : ""}>不确定</option>
      </select>
    `;
    li.addEventListener("dragstart", () => li.classList.add("dragging"));
    li.addEventListener("dragend", () => {
      li.classList.remove("dragging");
      refreshTimelineFromDom();
    });
    li.addEventListener("dragover", (event) => {
      event.preventDefault();
      const dragging = $("timeline").querySelector(".dragging");
      if (!dragging || dragging === li) return;
      const rect = li.getBoundingClientRect();
      const after = event.clientY > rect.top + rect.height / 2;
      $("timeline").insertBefore(dragging, after ? li.nextSibling : li);
    });
    li.querySelector(".timeline-description").addEventListener("input", refreshTimelineFromDom);
    li.querySelector(".timeline-certainty").addEventListener("change", refreshTimelineFromDom);
    $("timeline").appendChild(li);
  });
  $("saveTimelineBtn").disabled = state.timeline.length === 0;
  $("reconstructBtn").disabled = state.timeline.length === 0;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function refreshTimelineFromDom() {
  state.timeline = Array.from($("timeline").querySelectorAll(".timeline-row")).map((row, index) => {
    const original = state.timeline[Number(row.dataset.index)] || {};
    row.dataset.index = index;
    row.querySelector(".drag-handle").textContent = index + 1;
    return {
      ...original,
      event_id: `E${index + 1}`,
      sequence_index: index + 1,
      description_zh: row.querySelector(".timeline-description").value.trim(),
      certainty: row.querySelector(".timeline-certainty").value,
    };
  });
  $("saveTimelineBtn").disabled = state.timeline.length === 0;
  $("reconstructBtn").disabled = state.timeline.length === 0;
}

async function saveTimeline() {
  const caseId = await ensureCase();
  refreshTimelineFromDom();
  try {
    const result = await request(`/api/cases/${caseId}/timeline/update`, {
      method: "POST",
      body: JSON.stringify({ events: state.timeline }),
    });
    showTimeline(result.timeline || []);
    showNarrativeTriage(result.narrative_triage);
    showNextQuestion(result);
    return result;
  } catch (error) {
    showTimeline(state.timeline);
    return { timeline: state.timeline, local_only: true };
  }
}

async function reconstructStory() {
  const caseId = await ensureCase();
  await saveTimeline();
  let result;
  try {
    result = await request(`/api/cases/${caseId}/timeline/reconstruct`);
  } catch (error) {
    result = reconstructStoryLocally();
  }
  $("reconstructResult").textContent = result.story_zh;
  return result;
}

function reconstructStoryLocally() {
  const parts = state.timeline.map((event) => {
    const prefix = event.certainty === "uncertain" ? "我不确定" : event.certainty === "approximate" ? "我大概记得" : "我记得";
    return `${prefix}：${event.description_zh}`;
  });
  return {
    story_zh: parts.length ? `${parts.join("。")}。` : "暂无可还原的案发经过。",
    events: state.timeline,
    uncertain_items: state.timeline.filter((event) => event.certainty === "uncertain"),
  };
}

function showNextQuestion(result) {
  state.currentGap = result.current_gap || null;
  $("nextQuestion").textContent = result.next_question || "暂时没有关键缺口。";
  $("nextQuestion").className = state.currentGap && state.currentGap.issue_id ? "question conflict" : "question";
  $("answerBtn").disabled = !state.currentGap || result.followup_finished;
  $("finishFollowupBtn").disabled = !state.caseId || result.followup_finished;
  $("evaluateEvidenceBtn").disabled = !state.caseId;
  $("supportGuidanceBtn").disabled = !state.caseId;
  $("followupStatus").textContent = [
    `逻辑矛盾：${(result.logic_issues || []).length}`,
    `待补充细节：${(result.missing_details || []).length}`,
    result.followup_finished ? "状态：用户已结束追问" : "状态：追问中",
  ].join("\n");
  if (!state.currentGap) {
    $("followupAnswer").value = "";
  }
}

function showEvidence(evidence) {
  $("evidenceSummary").textContent = evidence.summary || "已生成证据建议清单。";
  $("evidenceCards").innerHTML = "";
  (evidence.recommended_evidence || []).forEach((item) => {
    const card = document.createElement("section");
    card.className = "evidence-card";
    const title = document.createElement("h3");
    title.textContent = item.title;
    const meta = document.createElement("div");
    meta.className = "evidence-meta";
    meta.textContent = `用途等级：${item.usefulness || "unknown"} ｜ 状态：${item.status || "unknown"}`;
    const why = document.createElement("p");
    why.textContent = `为什么有用：${item.why_useful || "待补充"}`;
    const how = document.createElement("p");
    how.textContent = `怎么收集：${item.how_to_collect || "待补充"}`;
    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(why);
    card.appendChild(how);
    $("evidenceCards").appendChild(card);
  });
  state.evidenceEvaluated = true;
}

function showDocuments(payload) {
  state.documents = {
    police_statement: payload.police_statement,
    police_followup: payload.police_followup,
    medical_summary: payload.medical_summary,
    university_support_email: payload.university_support_email,
  };
  $("documents").innerHTML = "";

  Object.entries(state.documents).forEach(([type, generatedDocument]) => {
    const box = document.createElement("section");
    box.className = "document-box";

    const title = document.createElement("h3");
    title.textContent = labels[type] || type;

    const textarea = document.createElement("textarea");
    textarea.id = `doc-${type}`;
    textarea.value = generatedDocument.content;

    const check = document.createElement("label");
    check.className = "review-check";
    check.innerHTML = `<input type="checkbox" id="review-${type}" /> 我已检查这份英文文本，确认事实属实；不确定处已经保留为 unknown / not certain / placeholder。`;

    box.appendChild(title);
    box.appendChild(textarea);
    box.appendChild(check);
    $("documents").appendChild(box);
  });

  $("reviewBtn").disabled = false;
}

function showSupportGuidance(payload) {
  $("supportDisclaimer").textContent = payload.disclaimer || "本模块只提供一般信息整理，不提供法律意见。";
  $("supportPathways").innerHTML = "";
  (payload.pathways || []).forEach((item) => {
    const card = document.createElement("section");
    card.className = "evidence-card";
    const title = document.createElement("h3");
    title.textContent = item.title;
    const purpose = document.createElement("p");
    purpose.textContent = `用途：${item.purpose || ""}`;
    const fit = document.createElement("p");
    fit.textContent = `适用性：${item.fit || "视情况而定"}`;
    const prepare = document.createElement("ul");
    (item.what_to_prepare || []).forEach((text) => {
      const li = document.createElement("li");
      li.textContent = `准备：${text}`;
      prepare.appendChild(li);
    });
    const questions = document.createElement("ul");
    (item.questions_to_ask || []).forEach((text) => {
      const li = document.createElement("li");
      li.textContent = `可问：${text}`;
      questions.appendChild(li);
    });
    card.appendChild(title);
    card.appendChild(purpose);
    card.appendChild(fit);
    card.appendChild(prepare);
    card.appendChild(questions);
    $("supportPathways").appendChild(card);
  });
  $("supportLinks").innerHTML = "";
  (payload.official_links || []).forEach((item) => {
    const link = document.createElement("a");
    link.href = item.url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = item.label;
    $("supportLinks").appendChild(link);
  });
}

$("triageBtn").addEventListener("click", async () => {
  const caseId = await ensureCase();
  const result = await request(`/api/cases/${caseId}/triage`, {
    method: "POST",
    body: JSON.stringify({
      current_danger: $("currentDanger").checked,
      serious_injury: $("seriousInjury").checked,
      offender_nearby: $("offenderNearby").checked,
      needs_ambulance: $("needsAmbulance").checked,
      injured: $("needsAmbulance").checked,
      jurisdiction_id: "AU-NSW",
    }),
  });
  showTriage(result);
});

$("analyzeBtn").addEventListener("click", async () => {
  const caseId = await ensureCase();
  $("analyzeBtn").disabled = true;
  $("analyzeBtn").textContent = "正在分析...";
  try {
    $("nextQuestion").textContent = "正在调用 agent 分析...";
    const result = await request(`/api/cases/${caseId}/interview/free-narrative`, {
      method: "POST",
      body: JSON.stringify({ narrative: $("narrative").value }),
    });
    showTimeline(result.timeline || []);
    showNextQuestion(result);
  } finally {
    $("analyzeBtn").disabled = false;
    $("analyzeBtn").textContent = "生成时间线和下一步问题";
  }
});

$("answerBtn").addEventListener("click", async () => {
  const answer = $("followupAnswer").value.trim();
  if (!answer) {
    $("nextQuestion").textContent = "请先填写你对这条追问的回复。";
    return;
  }

  const caseId = await ensureCase();
  $("answerBtn").disabled = true;
  $("answerBtn").textContent = "正在补充到时间线...";
  try {
    const result = await request(`/api/cases/${caseId}/interview/answer`, {
      method: "POST",
      body: JSON.stringify({ answer }),
    });
    showTimeline(result.timeline || []);
    $("followupAnswer").value = "";
    showNextQuestion(result);
  } finally {
    $("answerBtn").disabled = !state.currentGap;
    $("answerBtn").textContent = "提交回复并补充到时间线";
  }
});

$("finishFollowupBtn").addEventListener("click", async () => {
  const result = await reconstructStory();
  showFinalReview(result);
});

$("saveTimelineBtn").addEventListener("click", async () => {
  await saveTimeline();
  $("reconstructResult").textContent = "时间线修改已保存。";
});

$("reconstructBtn").addEventListener("click", reconstructStory);

function showFinalReview(result) {
  $("finalReviewPanel").classList.remove("hidden");
  $("finalStory").textContent = result.story_zh;
  $("uncertainChoices").innerHTML = "";
  (result.events || []).forEach((event) => {
    const label = document.createElement("label");
    const checked = event.certainty === "uncertain" ? " checked" : "";
    label.innerHTML = `<input type="checkbox" value="${event.event_id}"${checked} /> ${event.sequence_index}. ${escapeHtml(event.description_zh)}（${event.certainty}）`;
    $("uncertainChoices").appendChild(label);
  });
}

$("confirmFinishBtn").addEventListener("click", async () => {
  const caseId = await ensureCase();
  const uncertainEventIds = Array.from($("uncertainChoices").querySelectorAll("input:checked")).map((item) => item.value);
  let result;
  try {
    result = await request(`/api/cases/${caseId}/interview/finalize-review`, {
      method: "POST",
      body: JSON.stringify({ uncertain_event_ids: uncertainEventIds }),
    });
  } catch (error) {
    state.timeline = state.timeline.map((event) => ({
      ...event,
      certainty: uncertainEventIds.includes(event.event_id) ? "uncertain" : event.certainty,
    }));
    result = {
      timeline: state.timeline,
      current_gap: null,
      followup_finished: true,
      logic_issues: [],
      missing_details: [],
      next_question: "用户已结束案发经过追问。你仍然可以生成英文材料，生成前请确认时间线内容。",
    };
  }
  showTimeline(result.timeline || []);
  showNextQuestion(result);
  $("finalReviewPanel").classList.add("hidden");
  $("reconstructResult").textContent = "已结束追问。英文材料将基于复核后的时间线生成。";
});

$("evaluateEvidenceBtn").addEventListener("click", async () => {
  const caseId = await ensureCase();
  $("evaluateEvidenceBtn").disabled = true;
  $("evaluateEvidenceBtn").textContent = "正在评估证据...";
  try {
    const result = await request(`/api/cases/${caseId}/evidence/evaluate`, {
      method: "POST",
      body: JSON.stringify({ note: $("evidenceNote").value }),
    });
    showEvidence(result);
  } finally {
    $("evaluateEvidenceBtn").disabled = false;
    $("evaluateEvidenceBtn").textContent = "评估证据并生成建议清单";
  }
});

$("supportGuidanceBtn").addEventListener("click", async () => {
  const caseId = await ensureCase();
  $("supportGuidanceBtn").disabled = true;
  $("supportGuidanceBtn").textContent = "正在生成支持路径...";
  try {
    const result = await request(`/api/cases/${caseId}/support/guidance`);
    showSupportGuidance(result);
  } finally {
    $("supportGuidanceBtn").disabled = false;
    $("supportGuidanceBtn").textContent = "生成后续支持指导";
  }
});

$("generateBtn").addEventListener("click", async () => {
  const caseId = await ensureCase();
  if (!state.evidenceEvaluated) {
    const evidenceResult = await request(`/api/cases/${caseId}/evidence/evaluate`, {
      method: "POST",
      body: JSON.stringify({ note: $("evidenceNote").value }),
    });
    showEvidence(evidenceResult);
  }
  $("generateBtn").disabled = true;
  $("generateBtn").textContent = "正在生成英文材料...";
  try {
    const result = await request(`/api/cases/${caseId}/documents/generate`, { method: "POST" });
    showEvidence(result.evidence || {});
    showDocuments(result);
  } finally {
    $("generateBtn").disabled = false;
    $("generateBtn").textContent = "生成给警察/医生/学校的英文材料";
  }
});

$("reviewBtn").addEventListener("click", async () => {
  const documents = {};
  Object.keys(state.documents).forEach((type) => {
    documents[type] = {
      content: $(`doc-${type}`).value,
      reviewed_by_user: $(`review-${type}`).checked,
    };
  });

  const result = await request(`/api/cases/${state.caseId}/documents/review`, {
    method: "POST",
    body: JSON.stringify({ documents }),
  });
  $("reviewResult").textContent = result.reviewed_by_user
    ? "已保存：所有英文材料都已由用户检查确认。"
    : "已保存：仍有英文材料未勾选确认，请继续检查。";
});
