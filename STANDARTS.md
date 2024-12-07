# Стек технологий

# Python

## Версии
По дефолту используем версию >=3.11.
3.12 - не возбраняется. В целом 3.12 и 3.11 - идентичны для продуктовой разработки.
В приоритете версия python3.13, но пока он сырой для продуктового использования (предпочтителен из-за free-lock)


## Управление зависимостями

### `poetry`
Плюсы:
- Автоматический резолвинг зависимостей
- Решение "круговых" зависимостей.
- Быстрая скорость работы (резолвинг зависимостей)
- Автоматическое создание виртуального энвайромента
- Простой билдинг пакетов
- Использование `pyproject.toml` !
- Обширная документация и коммьюнити.
Минусы:
- Не установлен по дефолту.

Примечания:
- `pipenv` - даже не рассматривается! В сравнении с `poetry` - он очень медленный, имеет свой формат, а не общий с `pyproject.toml` и у него много подводных камней, с плохими решениями.
- `uv` - хороший аналог, но пока в зачаточном состоянии.


## Линтеры

### Ruff
https://docs.astral.sh/ruff/

Плюсы:
- Написан на Rust со всеми вытекающими: компактность, скорость... (см. репу за подробностями)
- Гибконастраиваемые правила.
- Поддержка `pyproject.toml`
Минусы:
- Много правил для настройки

### Black
https://github.com/psf/black

Плюсы:
- Популярный (но смещается ruff)
- Более строгий (к примеру только двойные кавычки для строковых переменных)
- Почти не надо настраивать.

Минусы:
- Написан на python - медленный, в сравнении с `ruff`
- Более строгий (к примеру только двойные кавычки для строковых переменных)


# Использование технологий

# Poetry

### Инициализация проекта
```zsh
poetry init
```

### Добавление пакета
```zsh
poetry add
```

### Посмотреть список зависимостей в виде дерева
```zsh
poetry show --tree
```

### Зайти в venv
```zsh
poetry shell
```

### Установить зависимости для проекта из `poetry.lock`
```zsh
poetry install
```

### Вывести список имеющихся команд
```zsh
poetry list 
```

### Ruff
### Правила линтинга

В `pyproject.toml` добавить:
```toml
[tool.ruff.lint]
line-length = 120
indent-width = 4
ignore-init-module-imports = true
extend-select = ["Q", "I"]
ignore = [
    "F841", # Skip unused variable rules (`F841`).
    "C901", # too complex
    "B904", # except clause
    "F401", # imported but unused
]
select = [
    "E", # pycodestyle errors
    "W", # pycodestyle warnings
    "F", # pyflakes
    "C", # flake8-comprehensions
    "I", # isort
    "B", # flake8-bugbear
    "UP", # pyupgrade
]

[tool.ruff.format]
quote-style = "double"
line-ending = "lf"

[tool.ruff.lint.flake8-quotes]
docstring-quotes = "double"
inline-quotes = "double"

[tool.ruff.lint.isort]
split-on-trailing-comma = true
combine-as-imports = true
known-third-party = ["bound"]
```


# Логирование
Энтерпрайз-стандарт подразумевает json-формат логов - он очень удобен для time-serial DB, и парсинга/фильтрации по полям.

Стандартными для каждого приложения являются следующие поля:
- app.name
- app.version
- app.logger
- time
- level
- log_id
- message
- lineno (не обязательно, но с ним всегда отладка проще)



# Code-Style
Читать PEP-8 !
- https://peps.python.org/pep-0008/


## Соглашение об именах переменных

### Нотации
- snake_case в приоритете!
- В редких случаях возможно использование camelCase
- В редких случаях возможно использование венгерской нотации (там где невозможно использовать type-hinting)

Запрещено:
- PascalCase (исключения - имена классов)
- kebab-case
- flatcase (исключение - имена констант IDLOCKBOX)


### Использование type-hinting

#### Венгерская нотация
```python
# Венгерская нотация - не имеет смысла!
dict_numbers = {'one': 1, 'two': 2, 'three': 3}

# Приоритетнее использование type-hinting!
numbers: dict = {'one': 1, 'two': 2, 'three': 3}
```

Допускается если подходит по смыслу:
```python
list_users = ['Vladimir', 'Poul', 'Djessica']
```
> Чаще всего, это происходит для переменных со смысловой нагрузкой "список"


#### Функции/Методы
```python
def get_users()->None:
	pass

# Допускается
def get_users():
	pass
```

### Переменные
1. Должны отображать суть:

Пример счетчика обработанных данных:
```python
# Плохо
count = count + 1
```

```python
# Хорошо
processed_data = processed_data + 1
```

```python
# Плохо
for i in secrets:
	...
```

```python
# Хорошо
for secret in secrets:
	...
```


### Комментарии
Комментарии должны нести смысловую нагрузку, направленную на снижение когнитивной нагрузки или для обозначения сложных, непонятных моментов для стороннего читателя.

Комментарии ***не должны***:
- Описывать очевидную вещь
```python
# увеличение счетчика обработанных данных
count = count + 1 
```
- Быть разделителем 
```python
def processings_message(message:):
	...
	return message
#######SENDMESSAGE##########
def send_message(message):
	...
```

Комментарии должны:
- Описывать сложные и порой не очевидные вещи, которая делает функция/метод

```python
kafka = ProcessingKafka()
# Данные сначала получаются из БД,
# а затем сравниваются с тем что возвратило api Kafka
# для приведения кластера к ожидаемому состоянию описанному в БД.
# Возвращает булево значение (был ли приведен кластер к нужному состоянию)
result = kafka.api(address_kafka).sending(data)
```

```python
# Данный код нужен для уменьшения 
# временной сложности с O(n^2) к O(n)
buf_users = {}
for user in users:
	buf_users[user["topic_uuid"]] = user

list_users_topics = []
for topic in kafka_topics:
	list_users_topics.append(buf_users[topic["uuid"]])
```


# Структура проекта
```python
.
├── README.md
├── app
│   ├── main.py
│   ├── api
│   │   └── v1
│   │       └── feedbacks.py
│   ├── configs
│   │   ├── __init__.py
│   │   ├── log_settings.py
│   │   └── settings.py
│   ├── database
│   │   ├── __init__.py
│   │   ├── clusters.py
│   │   └── connection.py
│   └── models
│       ├── __init__.py
│       └── feedbacks.py
├── tests
│   └── test_api.py
├── .env
├── Dockerfile
├── docker-compose.yaml
├── poetry.lock
└── pyproject.toml
```


# GIT

## Коммиты
Работаем по GIT COMMIT CONVENTION!
https://www.conventionalcommits.org/ru/v1.0.0/

Angular Convention:
https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit
> На нем основан git commit convention
> Он нужен для уточнения/расширения таких моментов как scope и type

## Семантическое версионирование - Стандарт!
Правила версионирования пакетов/программ:
https://semver.org/lang/ru/


# Дополнительно 

## PEP20
Прочитать:

```python
import this
```
> Читать!


