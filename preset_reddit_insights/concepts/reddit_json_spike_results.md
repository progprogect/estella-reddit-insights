# Reddit_JSON_Spike_Results — эмпирика окружения

Источник: локальный спайк `preset_reddit_insights/spike/spike_reddit_json.py`, артефакт `SPIKE_RESULTS.md`.

## Выводы (кратко)
- `search.json` и `r/{sub}/hot.json` отвечали **HTTP 200** с корректным User-Agent.
- Пагинация `after` на 2 страницах — **200** для обеих.
- `old.reddit.com/comments/{id}.json` — ответ из **двух** листингов, верхнеуровневые комментарии присутствуют.

## Рекомендованные дефолты пресета
См. также мастер-концепт:
- Jitter **2.0–4.0 с** между страницами.
- `max_pages = 5`.
- `comment_limit` default **100** (потолок ориентир **500**).
- Обработка **429** с `Retry-After` либо backoff 60 с, до 3 попыток.
