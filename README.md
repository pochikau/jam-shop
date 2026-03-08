# Варенье на любой вкус

Небольшой сайт по продаже варенья: каталог, корзина, заказы, админка. Вариант A (простой CI/CD): деплой на свой сервер через GitHub Actions.

## Стек

- **Backend:** Flask, SQLAlchemy
- **БД:** PostgreSQL (в Docker)
- **Админка:** Flask-Admin (HTTP Basic: `admin` / `admin123` — смените в продакшене)
- **Docker:** docker-compose (сервисы `web`, `db`, `nginx`, `certbot`)
- **Прод:** Nginx, HTTPS через Let's Encrypt (домен jam.secsoc.tech)

## Запуск локально (Docker)

```bash
git clone <ваш-репозиторий>
cd vulns  # или имя папки проекта
docker compose up -d
```

Сайт: http://localhost:5000 (локально порт 5000 не проброшен — заходите через nginx: http://localhost:80 или на VDS по домену)  
Админка: http://localhost/admin (логин `admin`, пароль `admin123`)

## Первый запуск

1. Откройте админку и добавьте товары (Товары → Create).
2. На главной появятся карточки варенья, можно добавлять в корзину и оформлять заказ.

## Деплой на VDS (jam.secsoc.tech, Nginx + HTTPS)

1. **DNS:** создайте A-запись `jam.secsoc.tech` → IP вашей VDS.

2. **На VDS (Ubuntu):** установите Docker и Docker Compose, клонируйте репозиторий:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
   sudo usermod -aG docker $USER
   # выйдите и зайдите по SSH снова, затем:
   git clone https://github.com/ВАШ_ЛОГИН/ВАШ_РЕПО.git /home/user/jam-app
   cd /home/user/jam-app
   ```

3. **Первый запуск (без HTTPS):**
   ```bash
   docker compose up -d
   ```
   Проверьте: http://jam.secsoc.tech должен открываться (сайт по HTTP).

4. **Получение сертификата Let's Encrypt:**
   ```bash
   chmod +x init-letsencrypt.sh
   ./init-letsencrypt.sh your@email.com
   ```
   После этого сайт будет доступен по https://jam.secsoc.tech.  
   Если после `git pull` снова включится только HTTP, выполните:  
   `cp nginx/nginx-ssl.conf nginx/nginx.conf && docker compose restart nginx`.

5. **Продление сертификата (раз в ~3 месяца).** Добавьте в crontab (`crontab -e`):
   ```bash
   0 3 * * * cd /home/user/jam-app && docker compose run --rm --entrypoint certbot certbot renew && docker compose exec nginx nginx -s reload
   ```
   (путь `/home/user/jam-app` замените на свой.)

## Деплой через GitHub Actions (вариант A)

1. Создайте SSH-ключ для деплоя (на своей машине):
   ```bash
   ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy
   ssh-copy-id -i ~/.ssh/github_deploy.pub user@IP_СЕРВЕРА
   ```
2. В GitHub: репозиторий → Settings → Secrets and variables → Actions. Добавьте:
   - `SERVER_HOST` — jam.secsoc.tech (или IP VDS)
   - `SERVER_USER` — пользователь SSH
   - `APP_DIR` — путь к проекту на сервере (например `/home/user/jam-app`)
   - `SSH_PRIVATE_KEY` — содержимое файла `~/.ssh/github_deploy` (приватный ключ)
3. При каждом `push` в ветку `main` workflow подключается по SSH, делает `git pull`, пересобирает образ и перезапускает контейнеры.

## Безопасность в продакшене

- Смените `SECRET_KEY` и пароль админки (через переменные окружения или код).
- В `docker-compose` задайте свои `POSTGRES_PASSWORD` и при необходимости вынесите их в `.env` (файл в `.gitignore`).
