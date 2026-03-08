# Варенье на любой вкус

Небольшой сайт по продаже варенья: каталог, корзина, заказы, админка. Вариант A (простой CI/CD): деплой на свой сервер через GitHub Actions.

## Стек

- **Backend:** Flask, SQLAlchemy
- **БД:** PostgreSQL (в Docker)
- **Админка:** Flask-Admin (HTTP Basic: `admin` / `admin123` — смените в продакшене)
- **Docker:** docker-compose (сервисы `web`, `db`)

## Запуск локально (Docker)

```bash
git clone <ваш-репозиторий>
cd vulns  # или имя папки проекта
docker compose up -d
```

Сайт: http://localhost:5000  
Админка: http://localhost:5000/admin (логин `admin`, пароль `admin123`)

## Первый запуск

1. Откройте админку и добавьте товары (Товары → Create).
2. На главной появятся карточки варенья, можно добавлять в корзину и оформлять заказ.

## Деплой на сервер (вариант A)

1. На сервере Ubuntu установите Docker и Docker Compose, клонируйте репозиторий в каталог, например `/home/user/jam-app`.
2. Создайте SSH-ключ для деплоя (на своей машине):
   ```bash
   ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy
   ssh-copy-id -i ~/.ssh/github_deploy.pub user@IP_СЕРВЕРА
   ```
3. В GitHub: репозиторий → Settings → Secrets and variables → Actions. Добавьте:
   - `SERVER_HOST` — IP или домен сервера
   - `SERVER_USER` — пользователь SSH
   - `APP_DIR` — путь к проекту на сервере (например `/home/user/jam-app`)
   - `SSH_PRIVATE_KEY` — содержимое файла `~/.ssh/github_deploy` (приватный ключ)
4. При каждом `push` в ветку `main` workflow подключается по SSH, делает `git pull`, пересобирает образ и перезапускает контейнеры.

## Безопасность в продакшене

- Смените `SECRET_KEY` и пароль админки (через переменные окружения или код).
- В `docker-compose` задайте свои `POSTGRES_PASSWORD` и при необходимости вынесите их в `.env` (файл в `.gitignore`).
