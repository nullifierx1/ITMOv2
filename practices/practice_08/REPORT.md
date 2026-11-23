# Практика 8. Интерфейс недельного отчёта GitHub

Работа следует этапам со слайда 7 лекции 8: задача, прототип, контекст для агента, реализация и проверка. Подход к снимкам и разбору визуальных отличий показан на слайдах 41–45. [Лекция 8](https://github.com/nullifierx1/ITMOv2/blob/main/lections/lection_8_Al%20engineering%20tools.pdf)

## 1. Задача

В практике 7.2 недельная сводка приходила по почте. В этой практике сопровождающий репозитория может сам выбрать неделю и открыть сохранённую сводку в браузере. Сценарий один: выбрать понедельник, нажать «Показать отчёт» и увидеть сохранённые показатели по Issues и PR за семь дней. Для созданных Issues выводится разбивка по типам и авторам.

Выбрали тестовый репозиторий `nullifierx1/n8n-code-review-test`, чтобы на демонстрации проверить результат по двум известным неделям. [Тестовый репозиторий](https://github.com/nullifierx1/n8n-code-review-test) · [ТЗ практики](https://github.com/ai-course-avito/ITMOv2/tree/main/practices/practice_08)

[Репозиторий фронтенда](https://github.com/nullifierx1/n8n-github-weekly-report)

## 2. Прототип и выбор дизайна

Первый [HTML-прототип](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/prototype/report.html) собрали в Codex. Запрос был на один экран с формой и четырьмя карточками. В прототипе можно переключить исходный экран, ввод, загрузку, сохранённый отчёт, сохранённую неделю с нулями, отсутствие строки и ошибку. На узком экране карточки стоят в две колонки.

Для доработки сравнили два шаблона в каталоге v0. Pulse рассчитан на мониторинг инцидентов и развёртываний. В Shadcn Dashboard верхняя панель отделена от ряда карточек с ключевыми числами. Для недельной сводки выбрали второй вариант. Из него адаптировали верхнюю полосу для названия репозитория и ряд равноправных карточек. Сразу под заголовком оставили выбор недели, а разбивки разместили под показателями. [Shadcn Dashboard в v0](https://v0.app/templates/Pf7lw1nypu5) · [Pulse в v0](https://v0.app/templates/3hZwaLtyRbc)

v0 показан на слайде 11 лекции. Здесь его каталог использовали для выбора референса, а редактирование прототипа и перенос в React сделали в Codex. Перед этим на первом проходе по shadcn/ui выделили дельту отдельной меткой рядом с каждым числом. В финальном макете добавили верхнюю панель и проверили, что карточки и разбивки помещаются на мобильном экране.

[Экспорт прототипа в PDF](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/prototype/weekly-report.pdf) содержит семь состояний сценария и отдельный мобильный экран. PDF открывается на GitHub. [Интерактивный HTML](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/prototype/report.html) можно скачать и открыть в браузере. Для обоих форматов используются демонстрационные данные.

## 3. Что передали агенту

Для реализации использовали прототип, [спецификацию формы](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/spec.md) и описанный там JSON-ответ. Макет задаёт расположение элементов. В спецификации отдельно прописано, что делать при пустой дате, дате посреди недели, задержке, повторном Enter и ошибке сервера.

| Этап | Суть запроса к Codex | Что доработали после первого варианта |
|---|---|---|
| Макет | Собрать отчёт и показать состояния одного сценария. | Вынесли сравнение в отдельные метки на карточках и сохранили его рядом с каждым числом. |
| Интерфейс | Переиспользовать элементы shadcn/ui, подключить запрос по контракту и обработать состояния. | Добавили ошибки рядом с полем и блокировку в обработчике формы на время запроса. |
| Тесты | Проверить, что после отправки виден отчёт, а повтор во время задержки не даёт ещё одного запроса. | Управляем задержкой из теста, проверяем число запросов и делаем снимки после наступления нужного состояния. |

## 4. Реализация

Фронтенд написан на React и TypeScript. Сборка и локальный запуск идут через Vite. Кнопка, поле даты, подпись, карточки и сообщение об ошибке используют компоненты shadcn/ui. [Компоненты экрана](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/src/main.tsx)

Цвета и типографика заданы в [теме Tailwind](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/src/style.css).

Браузер вызывает `/api/weekly-report?weekStart=…`, Vite проксирует запрос в n8n. [Workflow практики 8](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/n8n/weekly-report-api.json) проверяет дату и ищет ключ выбранной недели в `weekly_issue_stats`. При наличии отчёта он отдельно читает предыдущую неделю из той же таблицы. Веб-сценарий только читает таблицу. Строки сохраняет существующий [workflow практики 7.2](https://github.com/nullifierx1/ITMOv2/blob/d775351/practices/practice_07.2/artifacts/workflow-json/weekly-gh-report.json).

В ответе воскресенье соответствует дню перед исключительной границей `week_end`. Сохранённая строка с нулями показывает карточки, а для отсутствующей строки выводится сообщение. Если предыдущей строки нет, дельта равна `null`. Дубликаты и сбои обработки дают ответ с ошибкой. [HTTP-контракт](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/spec.md#http)

Пока ответ ожидается, кнопка выключена и виден статус загрузки. Обработчик формы дополнительно проверяет, есть ли запрос в работе. При ошибке поле сохраняет выбранную дату и форму можно отправить снова. Поле имеет видимую подпись, а фокус выделяется через `:focus-visible`. В автоматической проверке Tab переводит фокус, Enter отправляет форму, значение даты задаёт Playwright. [Тест клавиатурной навигации](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/tests/report.spec.ts#L6) · [Стили фокуса](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/src/style.css#L27)

## 5. Проверки по лекции

Playwright запускает Vite и подменяет ответы API. Проверки поведения охватывают дату запроса, валидацию, найденный отчёт и нулевую неделю, отсутствие записи, загрузку, ошибку 500 и повторную попытку. В тесте с задержкой ответ удерживается во время двойного клика, повторного Enter и повторной отправки формы. После получения ответа тест проверяет, что запрос был один. [Валидация даты](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/tests/report.spec.ts#L32) · [Загрузка и блокировка повторов](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/tests/report.spec.ts#L46) · [Нулевая неделя, отсутствие записи и повтор после ошибки](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/tests/report.spec.ts#L70)

Контрактные тесты выполняют код из JSON-экспорта на тестовых строках формата 7.2. Они сверяют результаты с клиентскими фикстурами и проверяют отсутствие предыдущей строки, дубликаты, повреждённый JSON и статусы ответов. [Тест контракта](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/tests/report-contract.spec.ts)

Визуальные эталоны показывают готовый отчёт на 1000 и 390 px, а также сохранённую нулевую неделю, отсутствие записи и ошибку на 390 px. Размер окна, локаль и часовой пояс фиксированы, анимации отключены. Playwright сравнивает снимок приложения с эталоном той же ОС. При изменении видны эталон, текущий снимок и визуальная разница в HTML-отчёте. [Скриншотные тесты](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/tests/visual.spec.ts)

В первой итерации временное увеличение заголовка и удаление текста ошибки привели к падению визуального и поведенческого тестов. После возврата исходников тесты прошли. [Контрольный прогон](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/evidence/playwright-negative.txt) · [Визуальный diff](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/evidence/visual-diff.png)

## 6. Запуск для ревью

В репозитории фронтенда `make all-setup` устанавливает зависимости и Chromium. Команда `make demo` запускает Vite на `127.0.0.1` до `Ctrl+C`. Команда `make check` выполняет сборку и тесты, и завершается. Команда `make test-report` запускает HTML-отчёт Playwright отдельно по адресу `http://127.0.0.1:9324/` до `Ctrl+C`. Загрузка страницы и списка тестов проверена в Chromium. [Команды и настройки](https://github.com/nullifierx1/n8n-github-weekly-report#запуск)

## 7. Проверка с опубликованным n8n

Production-запрос из React за 16–22 ноября прошёл через Vite proxy, n8n Webhook и Data Table `weekly_issue_stats`. Интерфейс получил `success`, показал счётчики 8 / 4 / 7 / 1, разбивки и Δ. [Production Execution №7509](https://n8n-itmo.cyrweb.ru/workflow/6mpt6ZEKaK3M9RtY/executions/7509?projectId=6NeKLg2x1W0oWnNT)

В отдельных ручных проверках неделя 9–15 ноября вернула сохранённый отчёт с четырьмя нулями без сравнения, 30 ноября вернуло `empty`, дата 17 ноября дала HTTP 400. В режиме Offline интерфейс показал ошибку. После возврата Online повторная отправка загрузила отчёт. Для этих проверок номера Executions не указаны. [Сводка ручных проверок](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/evidence/live-integration/README.md)

Оригинальные снимки ручных проверок от 22 ноября 2026 года:

- [Отчёт за 16–22 ноября, разбивки и дельта](https://raw.githubusercontent.com/nullifierx1/n8n-github-weekly-report/b13b73a75978c201cc689ab5c5589131b50c8590/evidence/live-integration/01-report-2026-11-16.png)
- [Сохранённая нулевая неделя 9–15 ноября](https://raw.githubusercontent.com/nullifierx1/n8n-github-weekly-report/b13b73a75978c201cc689ab5c5589131b50c8590/evidence/live-integration/02-zero-2026-11-09.png)
- [Отсутствующий отчёт за неделю с 30 ноября](https://raw.githubusercontent.com/nullifierx1/n8n-github-weekly-report/b13b73a75978c201cc689ab5c5589131b50c8590/evidence/live-integration/03-missing-2026-11-30.png)
- [Ошибка загрузки в режиме Offline](https://raw.githubusercontent.com/nullifierx1/n8n-github-weekly-report/b13b73a75978c201cc689ab5c5589131b50c8590/evidence/live-integration/04-offline-error.png)
- [Успешный повтор после восстановления сети](https://raw.githubusercontent.com/nullifierx1/n8n-github-weekly-report/b13b73a75978c201cc689ab5c5589131b50c8590/evidence/live-integration/05-online-retry.png)
- [Успешная цепочка n8n, Production Execution №7509](https://raw.githubusercontent.com/nullifierx1/n8n-github-weekly-report/b13b73a75978c201cc689ab5c5589131b50c8590/evidence/live-integration/06-n8n-execution-7509.png)

Playwright проверяет интерфейс с подменой HTTP-ответов. Контрактные тесты отдельно проверяют преобразование строк таблицы по экспорту workflow. Задержка и статус загрузки проверяются в текущем тесте. Снимок загрузки относится к первой версии интерфейса и сделан с локальной подменой webhook. [Снимок первой версии](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/evidence/loading.png)

## 8. Результаты автоматических проверок

| Среда | Команда | Результат |
|---|---|---|
| Linux/WSL | `make check` | Сборка успешна, 12 тестов прошли |
| Нативный Windows | `npm.cmd run build`, затем `npm.cmd test -- --update-snapshots=none` | Сборка успешна, 12 тестов прошли |

В каждом прогоне прошли четыре контрактных, шесть поведенческих и два скриншотных теста. При первом запуске на Windows два визуальных теста остановились из-за отсутствующих эталонов. Пять Windows PNG созданы Playwright в нативном Chromium, просмотрены и проверены повторным прогоном без обновления эталонов. [Вывод Linux](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/evidence/make-check-linux.txt) · [Вывод Windows](https://github.com/nullifierx1/n8n-github-weekly-report/blob/main/evidence/make-check-windows.txt)
