# User Guide | 用户操作指南

## How to Use This Framework | 如何使用本框架

### Step 1: Initialization | 初始化
Copy the content of `SYSTEM_PROMPT.md` and paste it into the chat box of your preferred LLM (e.g., ChatGPT, Claude, Qwen).
将 `SYSTEM_PROMPT.md` 的内容复制并粘贴到你常用的大模型聊天框中。

### Step 2: Language Configuration | 语言配置
The AI will ask you to specify:
1. **Interaction Language**: The language for conversation (default: Chinese/中文)
2. **Document Language(s)**: The language(s) for official documents (default: English/英文)

**Examples | 示例**:
- "我想用中文交流，生成英文文书" (Chinese interaction, English documents)
- "English conversation, generate English and Japanese documents" (英文交流，生成英文和日文文书)
- "日本語で会話、英語と日本語の書類を作成" (Japanese interaction, English and Japanese documents)

**Example Responses | 回复示例**:

| Your Need | Response to AI |
|-----------|----------------|
| Chinese chat, English docs | "我想用中文交流，生成英文文书" |
| English chat, English docs | "English conversation, English documents" |
| Chinese chat, English + Japanese docs | "中文交流，生成英文和日文文书" |
| German chat, German + English docs | "Deutsch sprechen, deutsche und englische Dokumente erstellen" |
| Thai chat, Thai + English docs | "คุยเป็นภาษาไทย สร้างเอกสารภาษาไทยและภาษาอังกฤษ" |
| Keep defaults | "使用默认配置" |

**Configuration | 配置**:
> "中文交流，生成英文、日文和韩文三种文书"

**AI Will Generate | AI 将生成**:
- 🇬🇧 English version (for local police/university)
- 🇯🇵 Japanese version (for consulate/family)
- 🇰🇷 Korean version (for additional support services)
- 🇩🇪 German version (if requested, for European authorities)
- 🇹🇭 Thai version (if requested, for Thai consulate)
- 🇨🇳 Chinese reference (for your review)

### Step 3: Interaction | 交互流程
1.  **Safety Check**: The AI will ask if you are safe (in your chosen language). Reply honestly.
2.  **Narrative**: Describe what happened in your interaction language. Don't worry about grammar or order.
3.  **Follow-up**: Answer the AI's questions one by one. If you don't remember, say "I'm not sure" (in your interaction language).
4.  **Review**: The AI will summarize the timeline in your interaction language. Confirm if it's correct.
5.  **Generate**: Type "Generate Documents" to get your multilingual drafts.

### Supported Languages | 支持的语言
-   **Chinese (中文)**: zh
-   **English (英文)**: en
-   **Japanese (日文)**: ja
-   **Korean (韩文)**: ko
-   **Spanish (西班牙文)**: es
-   **French (法文)**: fr
-   **German (德文)**: de
-   **Thai (泰文)**: th

*Note: You can request documents in any combination of these languages.*
*注意：您可以请求生成任意组合的语言文书。*

### Tips for Better Results | 使用建议
-   **Be Honest**: It's okay to say "I forgot" or "I was too scared to notice."
-   **Details Matter**: Try to recall colors, sounds, smells, and exact words used.
-   **Privacy**: You can use placeholders like "[Name]" or "[Location]" if you prefer not to share real names initially.
-   **Language Consistency**: Use your chosen interaction language consistently throughout the conversation for best results.

## Example Dialogue | 对话示例

### Example 1: Chinese Interaction, English Documents | 示例1：中文交流，英文文书

**AI**: 你好，我是 SafeAbroad 智能体助手。请告诉我：1) 你希望用什么语言交流？2) 生成什么语言的文书？3) 你现在安全吗？

**User**: 我想用中文交流，生成英文文书。我现在在家，很安全。

**AI**: 好的，已配置：交流语言=中文，文书语言=英文。请描述发生了什么，不用担心顺序或语法。

**User**: 我昨晚在便利店外被推了一下。

**AI**: 我明白这很令人害怕。你还记得当时周围有其他人吗？

---

### Example 2: English Interaction, Multilingual Documents | 示例2：英文交流，多语文书

**AI**: Hello, I'm the SafeAbroad Agent. Please tell me: 1) What language for conversation? 2) What language(s) for documents? 3) Are you safe?

**User**: English conversation, generate English and Japanese documents. I'm safe at home now.

**AI**: Configuration set: Interaction=English, Documents=English & Japanese. Please describe what happened.

**User**: I was pushed outside a convenience store last night.

**AI**: I understand this must be frightening. Do you remember if there were any witnesses around?
