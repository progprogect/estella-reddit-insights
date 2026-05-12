# Method_A_OAuth_Setup — официальный Reddit API (чтение)

## Когда использовать
Метод **A**: OAuth **client_credentials** (приложение без пользовательского логина) для чтения публичных данных через `oauth.reddit.com`. Подходит для отчётности и более предсказуемых лимитов, чем у «голого» скрейпа.

## Что подготовить
1. Reddit: **Create App** (тип **script** или **web app** — для client_credentials обычно используются `client_id` и `client_secret` из приложения).
2. В **KV Store** Extella сохранить:
   - `reddit_client_id` — идентификатор приложения.
   - `reddit_client_secret` — секрет приложения.
3. (Рекомендуется) KV-ключ `reddit_app_user_agent` — строка вида `YourApp/1.0 by /u/yourname` (Reddit требует осмысленный User-Agent).

## Что делает пресет
Эксперт `reddit_fetch_pages` для метода **A** получает access token (`/api/v1/access_token`), затем ходит на `oauth.reddit.com` согласно параметрам из `reddit_discover`.

## Ограничения
- Нужны действующие ключи Reddit; политика квот — по правилам Reddit.
- Секреты **никогда** не вписывать в концепты — только имена KV-ключей выше.

## Проверка перед запуском
Вызвать эксперт `reddit_kv_check` с `method="A"` — он проверит, что нужные ключи не пустые (значения агент подставляет из KV в параметры запуска).
