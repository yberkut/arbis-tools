# Arbis Tools

**Modular Secure Toolkit for Arch-based Systems.**

## Структура проєкту

```
arbis-tools/                    # Корінь проєкту
├── src/
│   ├── core/                   # Базові, спільні утиліти
|   |   ├── __init__.py
│   |   ├── utils.py            # Загальні функції (parse_size, validate_partition_name, тощо)
|   |   └── (інші модулі core)
│   |
│   └── ksm/                    # Key & Secret Manager (KSM) - модуль управління ключами
|       ├── __init__.py
│       ├── usb.py              # Логіка ініціалізації USB store
|       └── (інші модулі KSM)
│
├── tests/                      # Юніт тести
│   ├── test_utils.py           # Тести для core/utils.py
│   └── (інші тести)
│
├── pytest.ini                  # Конфігурація для pytest
├── requirements-dev.txt        # Залежності для тестування (pytest, pytest-mock)
├── pyproject.toml              # Основна конфігурація Python-пакету
└── README.md                   # Документація проєкту
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