# Roguelike Chronicles

Статический блог о пройденных roguelike-играх. Генерируется из Markdown файлов в HTML для GitHub Pages.

## Структура проекта

```
.
├── articles/          # Markdown статьи
├── static/            # CSS и JS
├── build.py           # Генератор
├── index.html         # Сгенерированный сайт
└── README.md          # Этот файл
```

## Как добавить статью

1. Создай файл `articles/название-игры.md`:

```markdown
---
title: "Название игры"
hours: 123
date: "2024-01-15"
---

## Заголовок

Текст статьи в **markdown** формате.
```

2. Запусти генератор:

```bash
python3 build.py
```

3. Коммить `index.html` в репозиторий

## Поддерживаемый markdown

- Заголовки `#` - `######`
- **Жирный**, *курсив*, `код`
- Списки (маркированные и нумерованные)
- Цитаты `>`
- Блоки кода ```
- Таблицы `| Колонка 1 | Колонка 2 |`
- Ссылки `[текст](url)`
- Изображения `![alt](url)`
- Горизонтальная линия `---`

## Публикация на GitHub Pages

1. Создай репозиторий на GitHub
2. Загрузи содержимое этой папки (`index.html`, `articles/`, `static/`)
3. Settings → Pages → Source: Deploy from a branch → Branch: main / root
4. Сайт будет доступен по `https://username.github.io/repo-name/`

## Локальная разработка

```bash
# Клонировать
gh repo clone username/repo-name
cd repo-name

# Добавить статью
vim articles/novaia-igra.md

# Пересобрать
python3 build.py

# Проверить
python3 -m http.server 8000
# Открыть http://localhost:8000
```

## Требования

- Python 3.7+
- Никаких внешних зависимостей
