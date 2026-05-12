# Preset: Reddit Insights → Excel (локально)

Пресет Extella: от **явного вызова мастер-концепта** до **Excel** с постами и (опционально) комментариями Reddit.

## Состав

| Путь | Назначение |
|------|------------|
| [concepts/master_reddit_insights.md](concepts/master_reddit_insights.md) | Мастер-концепт (точка входа по имени) |
| [concepts/method_*.md](concepts/) | Инструкции по методам A / B / C |
| [concepts/excel_output_contract.md](concepts/excel_output_contract.md) | Контракт колонок Excel |
| [concepts/rate_limit_policy.md](concepts/rate_limit_policy.md) | Лимиты и 429 |
| [concepts/reddit_json_spike_results.md](concepts/reddit_json_spike_results.md) | Выводы спайка |
Исходники экспертов начинаются с `$extens("include.py")` — это **валидно только в Extella**; локальный `python3 -m py_compile` по этим файлам не используется.
| [spike/spike_reddit_json.py](spike/spike_reddit_json.py) | Локальный спайк HTTP (повторяемый) |
| [SPIKE_RESULTS.md](SPIKE_RESULTS.md) | Артефакт последнего спайка |
| [scripts/bootstrap_api.py](scripts/bootstrap_api.py) | Публикация концептов и экспертов в Extella |
| [AGENT_SYSTEM_PROMPT.md](AGENT_SYSTEM_PROMPT.md) | Фрагмент системного промпта агента |

## Мастер-концепт: имя для вызова

Пользователь должен называть концепт **точно как первая строка-заголовок в базе**. В исходнике зафиксировано:

**`Reddit Insights → Excel (master)`**

Пример: «Запусти **Reddit Insights → Excel (master)**».

## Локальный запуск экспертов

1. Установите **Extella Desktop**, войдите в аккаунт.
2. Вызовите экспертов с параметром **`target`** = UUID вашего устройства (см. [Extella CLI.md](../Extella%20CLI.md)), чтобы файлы писались на ваш ПК.
3. `output_dir`, например `~/Downloads/EstellaReddit` — каталог будет создан при необходимости.

## KV-ключи (рекомендации)

| Ключ | Назначение |
|------|------------|
| `reddit_client_id` | Метод **A** (OAuth) |
| `reddit_client_secret` | Метод **A** |
| `reddit_app_user_agent` | Осмысленный User-Agent для A/B/C |

## Публикация в Extella

Скрипт `bootstrap_api.py` добавляет заголовки **`X-Profile-Id: default`** и **`X-Agent-Id: agent_extella_default`** (как в примере curl Extella). Переопределение: переменные `EXTELLA_PROFILE_ID` и `EXTELLA_AGENT_ID`.

```bash
export EXTELLA_API_TOKEN="your-token"
cd preset_reddit_insights/scripts
python3 bootstrap_api.py --dry-run   # проверить состав запросов
python3 bootstrap_api.py             # загрузить концепты и эксперты
```

Повторный `concept/add` создаёт **новые** записи; при необходимости дедупликацию делайте вручную в UI или через `concept/update`.

## Методы

- **A:** OAuth `client_credentials`, листинги через `oauth.reddit.com`.
- **B:** Публичные `.json` без OAuth (`www.reddit.com`).
- **C:** Листинги как у **B**, комментарии через `old.reddit.com` (или `B` для комментариев — параметр `comments_engine`).

## Спайк

```bash
cd preset_reddit_insights/spike
python3 spike_reddit_json.py
```

Обновит [SPIKE_RESULTS.md](SPIKE_RESULTS.md).

## Ссылки

- Обзор неофициальных JSON-подходов: [Roundproxies — How to Scrape Reddit](https://roundproxies.com/blog/reddit/)
- User-Agent и `.json`: [Simon Willison TIL](https://til.simonwillison.net/reddit/scraping-reddit-json)
