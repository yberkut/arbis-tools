# Arbis Tools

**Modular Secure Toolkit for Arch-based Systems.**

## Структура проєкту

```
arbis-tools/                        # Корінь проєкту
├── src/
│   ├── core/                       # Базові, спільні утиліти
|   |   ├── tests/                  # Тести пакету core
|   |   |   ├── __init__.py
|   |   |   ├── test_parse_size.py  # Тести для core/parse_size.py
│   |   |   └── (інші тести core)
|   |   |
|   |   ├── __init__.py
│   |   ├── parse_size.py       
|   |   └── (інші модулі core)
│   |
│   └── ksm/                        # Key & Secret Manager (KSM) - модуль управління ключами
|       ├── __init__.py
│       ├── usb.py                  # Логіка ініціалізації USB store
|       └── (інші модулі KSM)
│
├── arbis-tools-config.yaml         # Конфігурація arbis-tools
├── pyproject.toml                  # Основна конфігурація Python-пакету
├── pytest.ini                      # Конфігурація для pytest
├── README.md                       # Документація проєкту
└── requirements-dev.txt            # Залежності для тестування (pytest, pytest-mock)
```

## Опис основних директорій

- **core/** — загальні функції, що можуть використовуватись у всіх модулях (наприклад, парсинг розмірів, валідація імен розділів, тощо).
- **ksm/** — модуль управління ключами, USB-сховищами, LUKS-розділами.
- **tests/** — модульні тести для різних частин системи.
- **pyproject.toml** — визначає залежності, ім'я пакета, налаштування для публікації.
- **requirements-dev.txt** — тільки для розробки (тести, мокування).

## Як запускати тести

```bash
# Перейти в директорію проєкту
cd arbis-tools/

# (Опційно) створити віртуальне середовище
python -m venv at-venv
source at-venv/bin/activate

# Встановити dev залежності
pip install -r requirements-dev.txt

# Запустити тести
pytest
```

## Usage

```bash
arbis-ksm --help
```