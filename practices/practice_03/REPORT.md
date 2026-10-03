# Отчёт: локальные модели

Отчёт ведёт OpenCode по фактическим результатам команд и вашим сообщениям в чате. Поручите агенту заполнить разделы и показать diff. Выводы студента он записывает после обсуждения; отсутствующие измерения отмечает как невыполненные.

## Окружение

ОС / CPU / GPU / RAM / VRAM / свободный диск:
- Linux 6.18.33.2-microsoft-standard-WSL2 (WSL2), AMD Ryzen 5 3500X 6-Core, 6 vCPU
- RAM: 7.7Gi (free ~0.2Gi, available 4.9Gi); Swap: 2Gi
- GPU: NVIDIA GeForce GTX 1660 (6 GiB VRAM), драйвер 610.57.01 (CUDA UMD 13.3)
- Диск: / 1.0T, свободно ~944G

Ollama / OpenCode / Python, версии:
- Ollama 0.34.4, локальный API 11434
- OpenCode 1.18.32
- Python 3.12.3

Модель, разработчик, семейство, тег и ID:
- Локальная база: qwen3.5:2b (family qwen35, 2.3B, gguf, Q8_0, digest 324d162b…)
- Сборки: itmo-local:latest (parent qwen3.5:2b, digest 8055c1d…)
- Агент: itmo-agent:latest (parent qwen3.5:2b, digest db69124…)

Формат, квантизация, лицензия, источник:
- GGUF, Q8_0, Apache-2.0 (из ollama pull qwen3.5:2b)

Фактический контекст, размещение CPU/GPU:
- Модель qwen3.5:2b сообщает context_length 262144; в itmo-agent параметр num_ctx=65536
- Запуск itmo-agent: контекст 65536, Processor: 100% GPU (по `ollama ps`)

Почему выбрана эта конфигурация:
- 2B Qwen3.5 умещается в RAM/GPU этого ПК; Q8_0 подходит для 6 GB VRAM.

## Сравнение семейств

| Разработчик / модель | Задача | Параметры / формат | Лицензия | Язык / tools | Источник |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

## Воспроизведение

Команды и файлы конфигурации:
- `make -C practices/practice_03/lab install && make -C practices/practice_03/lab test`
- `ollama create itmo-local -f practices/practice_03/lab/Modelfile`
- `ollama run itmo-local "Объясни разницу…"`
- `python3 experiment.py --mode baseline --model qwen3.5:2b --output results/baseline.json`
- `python3 experiment.py --mode baseline --model itmo-local --output results/baseline_itmo.json`
- `python3 experiment.py --mode system --model itmo-local --output results/system.json`
- Температуры и сиды: см. файлы `results/hot*.json` и `results/cold*.json`
- Профиль агента: `ollama create itmo-agent -f Modelfile.agent`, `ollama show itmo-agent`, `ollama ps`
- Проверки OpenCode: см. `lab/demo/opencode.json` и логи `results/*.jsonl`

Подтверждение локального endpoint и скачанных весов:
- `curl --fail http://localhost:11434/api/tags` вернул список с itmo-local, itmo-agent, qwen3.5:2b

Проверка без сети после подготовки:
- Эксперименты выполнялись по локальному API Ollama; внешние подключения отключены флагом `--pure`.

Если работали в паре, чей компьютер и почему:
- Один компьютер (WSL2 с GTX 1660). Партнёр не использовался.

## Эксперимент

Фактор A/B:
- A: baseline (без явного system-сообщения в API-запросе), B: system (system.txt). В сохранённых запросах меняется только наличие system-сообщения; отсутствие SYSTEM в самой модели itmo-local этим не подтверждается: текущий Modelfile содержит SYSTEM.

Неизменные условия:
- model=itmo-local (qwen3.5:2b), temperature=0.2, seed=42, think=false, num_ctx=4096.

Итоги по вопросу о CI (demo/README.md, один и тот же контекст):
- A (baseline): модель выдумала GitHub Actions — неверно. См. results/baseline_itmo.json
- B (system): «В предоставленных материалах нет ответа.» — верно. См. results/system.json

Сводные цифры и ответы — в `results/*.json`.

## Скорость

Холодный старт отдельно:
- baseline_itmo.json (wall≈10.06s), system.json (wall≈7.13s)

Три прогретых повтора и медиана:
- Temperature 0.8, seeds 42/43/44: wall 0.53s / 0.22s / 1.35s; медиана ≈ 0.53s
- Temperature 0.2, seeds 42/43/44: wall 0.20s / 0.20s / 0.22s; медиана ≈ 0.20s
- Скорости декодирования по eval_duration в файлах: 63–75 ток/с в коротких ответах

Единицы и метод замера:
- Скрипт experiment.py сохраняет `wall_seconds`, `load_seconds`, `total_seconds`, `decode_tokens_per_second` из ответа Ollama API.

TTFT измерен или не измерен:
- Не измерен (ответ не потоковый), соответствует методичке.

## Вывод

Ошибка или обнаруженное ограничение:
- baseline без явного system-сообщения в API-запросе выдал выдуманный ответ про GitHub Actions на вопрос о CI.
- В CLI-запуске `ollama run` отображались «размышления», но в experiment.py использовалось `think=false`.

Как проверили:
- A/B по одному вопросу, равные параметры; результаты в `results/baseline_itmo.json` и `results/system.json`.

Какой конфигурацией будете пользоваться:
- itmo-local (qwen3.5:2b, Q8_0), temperature=0.2, seed=42 для проверок на факты.

Что осталось непроверенным:
- Другие вопросы через API в этом эксперименте не проводились; ответы через OpenCode зафиксированы отдельно в `answers.md` и `results/q*.jsonl`.
