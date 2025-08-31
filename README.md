# ITEMS-APP
Простое API, которое создает items вида
```json
{"id":1,"name":"item1"}
```

## Требования
- python 3.11+
- postgresql 16

## Запуск
Для запуска проекта выполнить
```bash
git clone https://github.com/AnastasiyaGapochkina01/example-of-diploma.git
cd example-of-diploma
cp env.example .env
# обязательно заменить значения переменных
docker compose up -d --build
docker compose ps
```

### Проверка
```bash
# добавить item
curl -X POST -H "Content-Type: application/json" -d '{"name": "item1"}' localhost/items
# получить items list
curl 127.0.0.1/items
# получить метрики
curl 127.0.0.1/metrics
```

## Ansible
Для первоначальной раскатки приложения на новой машине реализованы ansible roles:
- install-docker
- setup-items-app

### install-docker
Устанавливает docker на ВМ (работает только с debian)

### setup-items-app
Создает директорию для проекта, клонирует репозиторий, генерирует .env файл на основе переменных:
- `app_image` - docker image для items-app
- `db_user` - пользователь для БД
- `db_name` - имя базы данных
- `db_host` - хост, где находится postgres
- `db_pass` - пароль пользователя `db_user`
 и запускает проект с помощью docker compose.