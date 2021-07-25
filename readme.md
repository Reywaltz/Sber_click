# Тестовое задание в СберКлик

Необходимо создать CRM для регистрации и обработки входящих заявок от пользователей. Необходимо реализовать следующий функционал:
* Управление служебными данными (добавление, изменение, удаление):
    * Клиенты (подумать, как грамотно описать, чтобы было легко подобраться к задаче о нотификации)
    * Сотрудники компании
    * Заявки
* Фильтрация данных: 
    * По дате создания заявки (конкретная дата, промежуток дат); 
    * По типу заявки (заявка на ремонт, обслуживание, консультацию и т.д.);
    * По статусам заявки (одному или нескольким: например "открыта", "в работе", "закрыта" и т.д.)

Весь функционал должен быть закрыт от несанкционированного доступа (произвольным способом). Функционал покрыть тестами.

Система оповещения* (задача со звёздочкой): Предусмотреть механизм оповещения пользователя об изменении статуса заявки посредством использования телеграм-бота и Telegram API. Пользователь должен иметь возможность подписаться на уведомления, после чего при каждом изменении в статусах заявок, которые оформлены на него в соответствующий чат должна прилетать информация об этом. Также необходимо составить документацию, описывающую функционал сервиса и правила работы с ним.
        

## Инструкция по запуску:
Для запуска приложения необходимо развернуть контейнеры через команду docker-compose, находясь в директории с проектом. 
```bash
git clone https://github.com/Reywaltz/Sber_click
cd sber_click
docker-compose up
```

После запуска контейнеров пользователю доступна пустая база данных, структура которой описана в директории sql в файле schema.sql:
```sql
CREATE TABLE customer (
    id INTEGER PRIMARY KEY NOT NULL GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL UNIQUE,
    tg_id TEXT UNIQUE,
    tg_name TEXT UNIQUE,
    tg_chat INTEGER
);

CREATE TABLE worker (
    id INTEGER PRIMARY KEY NOT NULL GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE task (
    id INTEGER PRIMARY KEY NOT NULL GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    worker_id INTEGER REFERENCES worker(id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES customer(id) ON DELETE CASCADE
);

CREATE TABLE users(
    id INTEGER PRIMARY KEY NOT NULL GENERATED ALWAYS AS IDENTITY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    token TEXT,
    valid_to TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

insert into users (username, password) VALUES ('admin', '$2b$12$CUTvOrccJn083q9AkAknV.YIzCO3Nq26psK//udyJfzMGLEH8w5Gm')
```

Так же создаётся пользователь админстатор для взаимодействем с API. Учётные данные:

```
username: admin
password: qwerty
```

Для обеспечения решения задачи с нотификацией было принято решение держать в БД помимо основной информации о пользователе, так же содержаться опциональные поля (ID пользователя в Telegram, его Username, если он существует, и ID чата), которые необходимы для отправки сообщения посредством Telegram API. Если пользователю необходимо будет оповещения через Telegram, то благодаря этим данным можно будет гибко отправлять данные в разные виды чатов: Чат-боты, групповой чат или же в личные сообщения пользователя. Для передачи этих данных в другой сервис подойдёт брокер сообщений, такой как RabbitMQ, Kafka или прочие.

## Основные API методы

Все сущетсвующие методы с входными параментрами и возвращаемыми кодами состояния описаны в документации Swagger:
https://documenter.getpostman.com/view/15332017/TzsZroW1

Для начала работы необходимо получить авторизоваться по URL /api/v1/login с данными, которые были описаны выше. В ответ пользователю возвращается токен, который в последствии необходимо вставлять в заголовок запроса для доступа к остальному API
```
Authorization: "Bearer TOKEN"
```