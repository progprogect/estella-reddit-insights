# Excel_Output_Contract — формат выгрузки

## Файл
- Расширение: `.xlsx`
- Путь: `{output_dir}/{workbook_name}.xlsx` (каталог с `expanduser`, например `~/Downloads/EstellaReddit`)
- Листы:
  - `posts` — найденные посты (листинги)
  - `comments` — комментарии (если включён шаг `reddit_fetch_comments`; иначе лист пустой с заголовками)

## Колонки (минимум)
Общие идеи столбцов (реализация в `reddit_export_xlsx`):
- `record_id` — стабильный id (`t3_` / `t1_` или id из Reddit)
- `kind` — `post` | `comment`
- `subreddit`
- `title` — для поста; пусто для комментария
- `body` — selftext или текст комментария (укороченный при необходимости в нормализации не делаем — Excel может быть большим; при риске — optional max length в параметрах эксперта позже)
- `permalink` — полная URL `https://www.reddit.com...`
- `url` — ссылка поста (для постов)
- `author`
- `created_utc` — ISO UTC
- `score`
- `num_comments` — для постов
- `parent_id` / `parent_permalink` — для комментариев (если доступно)
- `depth` — глубина в дереве (0 = top-level)
- `source_method` — `A` | `B` | `C`

## Локальное выполнение
Экспорт выполнять на **локальном target**, чтобы pandas/openpyxl имели доступ к файловой системе пользователя.
