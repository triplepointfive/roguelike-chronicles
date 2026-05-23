# Roguelike Chronicles

Статический блог о пройденных roguelike-играх. Генерируется из Markdown-файлов в HTML для [GitHub Pages](https://pages.github.com/).

## Структура проекта

```
.
├── articles/          # Исходники статей (Markdown)
├── static/            # CSS и JS (встраиваются в HTML при сборке)
├── docs/              # Собранный сайт — публикуется на GitHub Pages
│   ├── index.html
│   └── games/
├── build.py           # Генератор
└── README.md
```

Каталог `docs/` пересоздаётся при каждой сборке. Его нужно коммитить в репозиторий вместе с исходниками.

## Как добавить статью

1. Создай файл `articles/название-игры.md`:

```markdown
---
title: "Название игры"
hours: 123
date: "2024-01-15"
deaths: 42
---

## Заголовок

Текст статьи в **markdown** формате.
```

2. Запусти генератор:

```bash
python build.py
```

3. Закоммить изменения в `articles/` и сгенерированный каталог `docs/`

## Поддерживаемый markdown

- Заголовки `#` — `######`
- **Жирный**, *курсив*, `код`
- Списки (маркированные и нумерованные)
- Цитаты `>`
- Блоки кода ` ``` `
- Таблицы `| Колонка 1 | Колонка 2 |`
- Ссылки `[текст](url)`
- Изображения `![alt](url)`
- Горизонтальная линия `---`

## Публикация на GitHub Pages

1. Создай репозиторий на GitHub и загрузи проект (исходники + `docs/`).
2. Собери сайт локально: `python build.py`
3. В репозитории: **Settings → Pages**
4. **Build and deployment → Source:** Deploy from a branch
5. **Branch:** `main` (или `master`), **Folder:** `/docs`
6. Сохрани настройки. Через минуту сайт будет доступен по адресу:
   - проектный сайт: `https://<username>.github.io/<repo-name>/`
   - пользовательский сайт (репозиторий `<username>.github.io`): `https://<username>.github.io/`

Файл `docs/.nojekyll` отключает обработку Jekyll — GitHub отдаёт HTML как есть.

## Локальная разработка

```bash
# Клонировать
git clone https://github.com/<username>/<repo-name>.git
cd <repo-name>

# Добавить или изменить статью
# articles/novaia-igra.md

# Пересобрать
python build.py

# Проверить (сервер из каталога docs/)
python -m http.server 8000 --directory docs
# Открыть http://localhost:8000
```

## Требования

- Python 3.7+
- Никаких внешних зависимостей
