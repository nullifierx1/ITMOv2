# Полные ответы

## **ZERO-SHOT**

Findings (ordered by severity)
1. app/api.py:35-38 create_review – missing input validation and schema
- You accept a raw dict for the request body and immediately index payload"diff". If the key is missing or not a string, this raises KeyError -> 500 instead of 422 validation.
- Without a Pydantic model, your OpenAPI schema will be vague (“object”), hurting client integration and docs.
- Fix: define a request model, e.g. class ReviewRequest(BaseModel): diff: str. Optionally define a response model with a stable shape.
2. app/review_service.py:19-22 ReviewService.review – prompt injection and unbounded input size
- You interpolate untrusted diff directly into the LLM prompt. A malicious diff can steer the model (“ignore previous instructions…”), leak data, or produce non-actionable output.
- No truncation or token budgeting; large diffs can exceed context limits or degrade latency/cost.
- Fix: delimit the diff (e.g., wrap in diff … ), add firm, explicit instructions about allowed behavior and output format, and truncate/summarize large diffs before sending.
3. Cross-layer coupling – service returns transport-shaped dict
- review returns dictstr, str, which bakes API shape into the domain service. This makes reuse harder and mixes responsibilities.
- Fix: have ReviewService.review return a domain value (e.g., a string or a structured ReviewResult), and let the API layer shape the HTTP response.
4. app/api.py:35-38 – blocking call and lack of timeout/error handling
- The endpoint is sync; FastAPI will run it in a threadpool, but if llm.generate does network I/O without timeouts/retries, requests could hang or consume workers.
- No try/except for LLM failures; users will see 500s with generic errors.
- Fix: add timeouts at the LLM client boundary, handle exceptions and return a controlled error (or map to 502/504). Consider async if your LLM client supports it.
5. Output contract is underspecified for an automated reviewer
- The prompt asks to “find problems” but you return a single "comment" string. That’s hard to consume programmatically and loses structure (severity, file, line).
- Fix: enforce structured output (e.g., JSON with findings: {file, line, severity, message}). Validate/parsing on the server side before returning.
6. API design and DX
- No response_model in the FastAPI route; docs will be generic. Add response_model to lock the schema.
- Path naming/versioning: “/api/reviews” under an app that may already be mounted under /api can be redundant. Consider “/reviews” with a versioned prefix (/v1) at the router level.
7. Testing gaps
- Missing unit tests for ReviewService.review (prompt composition, truncation) and API tests for payload validation and error cases (missing diff, too large diff, LLM error path).
8. Minor style/compatibility notes
- app/review_service.py:10-13: Expanded Protocol method body is fine; functionally unchanged. Keep consistent style with repo conventions.
- dictstr, str requires Python 3.9+. If the project supports <3.9, use Dictstr, str from typing.
Open questions
- Do you want the LLM to return structured findings (file, line, severity)? If yes, I’ll update the prompt and implement strict JSON parsing plus response models.
- What’s the maximum diff size we should accept/process? Should we summarize/truncate beyond N lines or characters?
- Is authentication required for this endpoint, or is it intentionally open?
- Which Python version is targeted by this project?
Change summary (minimal, targeted)
- Introduce Pydantic models: ReviewRequest {diff: str}, ReviewResponse {comment: str} (or a Findings schema if you want structure), wire them into @app.post with request/response_model to get validation and better OpenAPI.
- Harden the prompt: wrap diff in fenced code block, add explicit output-format instructions, and basic prompt-injection guardrails. Add truncation/summarization for large diffs.
- Decouple layers: make ReviewService.review return a domain value (string or structured findings). Let the API construct the HTTP response dict/model.
- Add basic error handling and timeouts for LLM calls; map failures to clear HTTP errors.
- Add unit and API tests for happy path and validation/error scenarios. 

---

## **MASTER-PROMPT**

summary: PR добавляет метод генерации ревью через внешний LLM и HTTP-эндпоинт POST /api/reviews, который принимает diff и возвращает ответ модели без доп. обработок.
risks:
1. file: app/review_service.py
line: 12
evidence: prompt формируется из сырого diff без редактирования секретов: 'prompt = f"Review this pull request and find problems:\n{diff}"'; правило: SEC-1
risk: Утечка токенов/паролей/ключей во внешний LLM при передаче diff без редактирования.
check: Подставить в diff тестовую строку 'token=TEST_SECRET'; замокать LLM так, чтобы он возвращал полученный prompt; вызвать review_service.review(diff); ожидание: в prompt должно быть REDACTED, фактически секрет останется в тексте.
2. file: app/api.py
line: 10
evidence: длинный diff не ограничивается и не отклоняется: 'return review_service.review(payload"diff")'; правило: API-1
risk: Нарушение протокола API для больших входов и риск перегруза сервиса: диффы >20 000 символов не отклоняются HTTP 413.
check: Отправить POST /api/reviews с 'diff' длиной 20 001 символ; ожидание: HTTP 413; фактически вернётся 200/ответ модели и произойдёт вызов LLM.
3. file: app/review_service.py
line: 13
evidence: внешний вызов без таймаута и обработки ошибок: 'answer = self.llm.generate(prompt)'; правило: REL-1
risk: Подвисание запроса дольше 10 секунд или падение без контролируемого ответа при ошибке LLM.
check: Замокать LLM.generate с задержкой 15 секунд либо выбрасывающий исключение; вызвать review_service.review(diff); ожидание: таймаут 10с и контролируемый ответ, фактически — зависание >10с или непроброшенная 500/traceback.
checks:
- Юнит‑тест редактирования секретов в prompt: diff с 'token=TEST_SECRET' не должен попадать в внешний вызов (SEC-1).
- Интеграционный тест API на ограничение размера: diff = 20 001 символ, ожидание HTTP 413 (API-1).
- Тесты надёжности LLM-вызова: симулированная задержка >10с и исключение → проверка таймаута 10с и контролируемого ответа (REL-1).

---

