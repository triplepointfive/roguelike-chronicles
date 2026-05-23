# Roguelike Chronicles

Статический блог о пройденных roguelike-играх. Каждая игра — **отдельная HTML-страница** с оглавлением. Генерируется из Markdown для [GitHub Pages](https://pages.github.com/).

> **Важно:** на GitHub в браузере по умолчанию показывается `README.md` — это обычный Markdown без стилей. Чтобы увидеть сайт, откройте собранный каталог **`docs/`** (после `python build.py`) локально или опубликуйте Pages из `/docs`.

## Структура проекта

```
.
├── articles/          # Исходники статей (Markdown)
├── static/            # CSS и JS (встраиваются при сборке)
├── docs/              # Собранный сайт → GitHub Pages
│   ├── index.html     # Список игр
│   └── games/         # Страница каждой игры
├── build.py           # Генератор
└── README.md
```

## Как добавить статью

1. Создай `articles/название-игры.md` с frontmatter (`title`, `hours`, `date`, `deaths`, …).
2. Запусти `python build.py`
3. Закоммить `articles/` и обновлённый `docs/`

При 5–10 играх на главной будут карточки, у каждой игры — своя страница и боковое оглавление по разделам.

## Локальный просмотр

```bash
python build.py
python -m http.server 8000 --directory docs
# http://localhost:8000
```

## Публикация на GitHub Pages

1. Загрузи репозиторий (исходники + `docs/`)
2. **Settings → Pages →** Branch: `main`, Folder: **`/docs`**
3. Сайт: `https://<username>.github.io/<repo-name>/`

## Jekyll или build.py?

| | **build.py (сейчас)** | **Jekyll** |
|---|------------------------|------------|
| Зависимости | Только Python, без pip | Ruby, gem, тема |
| Страницы | Уже отдельный HTML на игру | Через коллекции и шаблоны |
| Стили | Полный контроль в `static/style.css` | Тема + переопределения |
| Сборка | `python build.py` | `jekyll build` → обычно `_site` |

Переход на Jekyll имеет смысл, если нужны плагины, теги, RSS или экосистема тем. Для личного блога с кастомным «терминальным» UI текущий генератор проще и уже масштабируется добавлением `.md` в `articles/`.

## Требования

- Python 3.7+
- Без внешних pip-зависимостей
