# Сайт снят с публикации

## Что сделано автоматически

- Главная страница заменена на заглушку «Сайт снят с публикации»
- `robots.txt` — запрет индексации
- Форма заявок и API `/api/apply` отключены (HTTP 410)
- Полная версия сайта сохранена в `archive/index.full.html`
- Деплой на GitHub Pages публикует только заглушку

## Отключить домен sluzhbarf.ru (Reg.ru)

Пока A-записи указывают на GitHub, домен может открывать заглушку с их серверов.

1. Reg.ru → **sluzhbarf.ru** → **Управление зоной DNS**
2. Удалите все **A-записи** для `@` (185.199.108–111.153)
3. Удалите **CNAME** для `www`, если есть
4. Сохраните

## Полностью выключить GitHub Pages

https://github.com/tolkachev14881488-beep/vsrf-contract-landing/settings/pages  
→ **Source: None** → Save

## Render (бэкенд)

https://dashboard.render.com → сервис **vsrf-contract-landing** → **Suspend** или **Delete**

## Восстановить сайт

1. Восстановите `index.html` из `archive/index.full.html`
2. Включите Pages и DNS по `docs/DOMAIN.md`
