#!/usr/bin/env python3
"""
Roguelike Blog Static Generator v2
====================================
Каждая игра — отдельная HTML страница.
Боковое меню содержит разделы текущей статьи (h2).

Использование:
    python3 build.py

Структура:
    index.html           — главная страница (список игр)
    games/nethack.html   — страница отдельной игры
    games/brogue.html
    ...

Frontmatter таблица:
    ---
    title: "NetHack"
    hours: 340
    table:
      - metric: "Hours played"
        value: "340"
      - metric: "Total deaths"
        value: "312"
    ---
"""

import os
import re
import glob
import shutil
from datetime import datetime


def parse_frontmatter(content):
    """Парсит YAML frontmatter из markdown файла."""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            
            meta = {}
            table_data = []
            current_key = None
            table_mode = False
            current_row = {}
            
            for line in fm_text.split('\n'):
                stripped = line.strip()
                
                # Таблица: начало списка
                if stripped == 'table:':
                    table_mode = True
                    continue
                
                # Таблица: элемент списка (начало строки)
                if table_mode and stripped.startswith('- '):
                    if current_row:
                        table_data.append(current_row)
                    current_row = {}
                    # Парсим ключ-значение из "- metric: \"Hours\""
                    match = re.match(r'-\s+(\w+):\s*(.+)', stripped)
                    if match:
                        k = match.group(1).strip()
                        v = match.group(2).strip().strip('"').strip("'")
                        current_row[k] = v
                    continue
                
                # Таблица: продолжение строки (indent)
                if table_mode and not stripped.startswith('table:') and stripped:
                    match = re.match(r'(\w+):\s*(.+)', stripped)
                    if match and current_row is not None:
                        k = match.group(1).strip()
                        v = match.group(2).strip().strip('"').strip("'")
                        current_row[k] = v
                    continue
                
                # Обычные ключ-значение
                if ':' in stripped and not table_mode:
                    key, value = stripped.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key == 'hours':
                        try:
                            value = int(value)
                        except ValueError:
                            value = 0
                    elif key == 'deaths':
                        try:
                            value = int(value)
                        except ValueError:
                            value = 0
                    meta[key] = value
            
            # Добавляем последнюю строку таблицы
            if current_row:
                table_data.append(current_row)
            
            if table_data:
                meta['table'] = table_data
            
            return meta, body
    return {}, content


def extract_h2_titles(text):
    """Извлекает h2 заголовки из markdown для оглавления."""
    titles = []
    for match in re.finditer(r'^## (.+)$', text, re.MULTILINE):
        title = match.group(1).strip()
        slug = slugify(title)
        titles.append({'title': title, 'slug': slug})
    return titles


def md_to_html_inline(text):
    """Конвертирует inline markdown элементы."""
    text = text.replace('&', '&amp;')
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    return text


def md_to_html(text):
    """Простой markdown -> HTML конвертер."""
    text = text.replace('&', '&amp;')
    
    # Заголовки (h1-h6)
    text = re.sub(r'^###### (.*?)$', r'<h6>\1</h6>', text, flags=re.MULTILINE)
    text = re.sub(r'^##### (.*?)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2 id="\1">\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Фиксируем ID заголовков (slugify)
    def fix_h2_ids(match):
        title = match.group(1)
        slug = slugify(title)
        return f'<h2 id="{slug}">{title}</h2>'
    text = re.sub(r'<h2 id="[^"]*">(.*?)</h2>', fix_h2_ids, text)
    
    # Блоки кода
    code_blocks = []
    def save_code_block(match):
        lang = match.group(1) or "text"
        code = match.group(2).strip()
        code_blocks.append((lang, code))
        return f"\x00CODEBLOCK{len(code_blocks)-1}\x00"
    text = re.sub(r'```(\w+)?\n(.*?)```', save_code_block, text, flags=re.DOTALL)
    
    # Цитаты
    def blockquote_replace(match):
        lines = match.group(1).strip()
        content = '\n'.join(line.lstrip('> ') for line in lines.split('\n'))
        content = md_to_html_inline(content)
        return f'<blockquote>\n{content}\n</blockquote>'
    text = re.sub(r'^>(.*?\n(?:(?:>.*?)\n?)*)', blockquote_replace, text, flags=re.MULTILINE | re.DOTALL)
    
    # Таблицы
    def table_replace(match):
        lines = match.group(0).strip().split('\n')
        if len(lines) < 2:
            return match.group(0)
        if not re.match(r'^[\s|:\-]+$', lines[1].replace(' ', '')):
            return match.group(0)
        header_cells = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
        header_html = '\n'.join(f'<th>{md_to_html_inline(cell)}</th>' for cell in header_cells)
        rows_html = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                row_cells = '\n'.join(f'<td>{md_to_html_inline(cell)}</td>' for cell in cells)
                rows_html.append(f'<tr>\n{row_cells}\n</tr>')
        body_rows = '\n'.join(rows_html)
        return f'<table>\n<thead>\n<tr>\n{header_html}\n</tr>\n</thead>\n<tbody>\n{body_rows}\n</tbody>\n</table>'
    text = re.sub(r'^(?:.*\|.*\n[\s|:\-]+\n(?:.*\|.*\n?)+)', table_replace, text, flags=re.MULTILINE)
    
    # Списки
    def ul_replace(match):
        items = match.group(0)
        item_texts = re.findall(r'^[-*+] (.*?)$', items, re.MULTILINE)
        lis = '\n'.join(f'<li>{md_to_html_inline(item)}</li>' for item in item_texts)
        return f'<ul>\n{lis}\n</ul>'
    text = re.sub(r'^(?:[-*+] .*?\n)+', ul_replace, text, flags=re.MULTILINE)
    
    def ol_replace(match):
        items = match.group(0)
        item_texts = re.findall(r'^\d+\. (.*?)$', items, re.MULTILINE)
        lis = '\n'.join(f'<li>{md_to_html_inline(item)}</li>' for item in item_texts)
        return f'<ol>\n{lis}\n</ol>'
    text = re.sub(r'^(?:\d+\. .*?\n)+', ol_replace, text, flags=re.MULTILINE)
    
    # Горизонтальная линия
    text = re.sub(r'^---+$', '<hr>', text, flags=re.MULTILINE)
    
    # Изображения
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy">', text)
    
    # Ссылки, inline код, жирный/курсив
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
    
    # Восстанавливаем блоки кода
    def restore_code_block(match):
        idx = int(match.group(1))
        lang, code = code_blocks[idx]
        escaped_code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code class="language-{lang}">{escaped_code}</code></pre>'
    text = re.sub(r'\x00CODEBLOCK(\d+)\x00', restore_code_block, text)
    
    # Параграфы
    paragraphs = text.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<') and (p.startswith('<h') or p.startswith('<pre') or 
                                    p.startswith('<ul') or p.startswith('<ol') or 
                                    p.startswith('<blockquote') or p.startswith('<hr') or 
                                    p.startswith('<img') or p.startswith('<table')):
            result.append(p)
        else:
            p = p.replace('\n', '<br>\n')
            result.append(f'<p>{p}</p>')
    
    return '\n\n'.join(result)


def slugify(text):
    """Создаёт URL-friendly slug."""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def get_time_class(hours):
    if hours < 50:
        return 'time-short'
    elif hours < 200:
        return 'time-medium'
    else:
        return 'time-long'


def generate_stats_table(table_data):
    """Генерирует HTML таблицу статистики из frontmatter."""
    if not table_data:
        return ''
    
    rows = []
    for row in table_data:
        metric = row.get('metric', '')
        value = row.get('value', '')
        # Определяем класс для значения
        val_lower = value.lower()
        if val_lower in ('yes', 'true', 'completed', 'done'):
            value_class = 'val-success'
        elif val_lower in ('no', 'false', 'died', 'failed'):
            value_class = 'val-danger'
        else:
            value_class = 'val-normal'
        rows.append(f'<tr><td class="stat-metric">{metric}</td><td class="stat-value {value_class}">{value}</td></tr>')
    
    table_rows = '\n'.join(rows)
    return f'<table class="stats-table">\n<tbody>\n{table_rows}\n</tbody>\n</table>'


def build():
    """Главная функция сборки."""
    print("Roguelike Blog Generator v2")
    print("=" * 40)
    
    base_dir = os.path.dirname(__file__)
    articles_dir = os.path.join(base_dir, 'articles')
    static_dir = os.path.join(base_dir, 'static')
    games_dir = os.path.join(base_dir, 'games')
    
    # Очищаем и создаём директорию games/
    if os.path.exists(games_dir):
        shutil.rmtree(games_dir)
    os.makedirs(games_dir)
    
    # Читаем CSS и JS
    css_content = ''
    js_content = ''
    css_path = os.path.join(static_dir, 'style.css')
    js_path = os.path.join(static_dir, 'script.js')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
    
    # Собираем все статьи
    articles = []
    md_files = sorted(glob.glob(os.path.join(articles_dir, '*.md')))
    
    if not md_files:
        print("No articles found in articles/")
        return
    
    print(f"Found {len(md_files)} articles")
    
    for md_file in md_files:
        filename = os.path.basename(md_file)
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        meta, body = parse_frontmatter(content)
        
        if 'title' not in meta:
            meta['title'] = filename.replace('.md', '')
        if 'hours' not in meta:
            meta['hours'] = 0
        if 'deaths' not in meta:
            meta['deaths'] = 0
        if 'date' not in meta:
            meta['date'] = datetime.now().strftime('%Y-%m-%d')
        if 'first_win' not in meta:
            meta['first_win'] = ''
        if 'version' not in meta:
            meta['version'] = ''
        if 'character' not in meta:
            meta['character'] = ''
        
        html_content = md_to_html(body)
        h2_titles = extract_h2_titles(body)
        slug = slugify(meta['title'])
        stats_table_html = generate_stats_table(meta.get('table', []))
        
        articles.append({
            'title': meta['title'],
            'hours': meta['hours'],
            'deaths': meta['deaths'],
            'date': meta['date'],
            'first_win': meta.get('first_win', ''),
            'version': meta.get('version', ''),
            'character': meta.get('character', ''),
            'slug': slug,
            'content': html_content,
            'h2_titles': h2_titles,
            'stats_table': stats_table_html,
            'filename': filename
        })
        
        print(f"  OK {meta['title']} ({meta['hours']}h, {len(h2_titles)} sections)")
    
    # Сортируем по дате
    articles.sort(key=lambda x: x['date'], reverse=True)
    
    total_hours = sum(a['hours'] for a in articles)
    total_deaths = sum(a['deaths'] for a in articles)
    year = datetime.now().strftime('%Y')
    
    # Генерируем страницу для каждой игры
    for idx, article in enumerate(articles):
        # Формируем оглавление (разделы h2)
        toc_items = []
        for h2 in article['h2_titles']:
            toc_items.append(
                f'<li><a href="#{h2["slug"]}" class="toc-link" data-target="{h2["slug"]}">'
                f'{h2["title"]}'
                f'</a></li>'
            )
        toc_html = '\n'.join(toc_items)
        
        # Формируем навигацию по другим играм
        other_games = []
        for other in articles:
            if other['slug'] != article['slug']:
                other_games.append(
                    f'<li><a href="{other["slug"]}.html" class="nav-game-link">'
                    f'<span class="nav-game-title">{other["title"]}</span>'
                    f'<span class="nav-game-hours">{other["hours"]}h</span>'
                    f'</a></li>'
                )
        other_games_html = '\n'.join(other_games)
        
        # Дата форматированная
        try:
            dt = datetime.strptime(article['date'], '%Y-%m-%d')
            date_formatted = dt.strftime('%d.%m.%Y')
        except ValueError:
            date_formatted = article['date']
        
        time_class = get_time_class(article['hours'])
        
        # Собираем HTML страницы игры
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'  <title>{article["title"]} — Roguelike Chronicles</title>',
            '  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">',
            '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=VT323&family=JetBrains+Mono:wght@400;600;700&display=swap">',
            '  <style>',
            css_content,
            '  </style>',
            '</head>',
            '<body>',
            '  <div class="app">',
            # Sidebar
            '    <aside class="sidebar">',
            '      <div class="sidebar-header">',
            '        <a href="../index.html" class="logo" title="Roguelike Chronicles">@</a>',
            '        <div class="subtitle">Roguelike Chronicles</div>',
            '      </div>',
            # Текущая игра (активная)
            '      <div class="sidebar-current-game">',
            f'        <div class="current-game-title">{article["title"]}</div>',
            f'        <div class="current-game-meta">',
            f'          <span class="current-game-hours {time_class}">{article["hours"]}h</span>',
            f'          <span class="current-game-deaths">&#x2620; {article["deaths"]}</span>',
            '        </div>',
            '      </div>',
            # Оглавление (разделы h2)
            '      <nav class="sidebar-toc">',
            '        <div class="toc-label">Contents</div>',
            '        <ul>',
            toc_html,
            '        </ul>',
            '      </nav>',
            # Другие игры
            '      <nav class="sidebar-other-games">',
            '        <div class="other-games-label">Other Games</div>',
            '        <ul>',
            other_games_html,
            '        </ul>',
            '      </nav>',
            # Footer sidebar
            '      <div class="sidebar-footer">',
            '        <a href="../index.html" class="back-link">&larr; All Games</a>',
            '      </div>',
            '    </aside>',
            # Main content
            '    <main class="main">',
            '      <div class="article-page">',
            # Header
            '        <header class="article-page-header">',
            f'          <h1>{article["title"]}</h1>',
            '          <div class="article-page-meta">',
            f'            <span class="article-date">{date_formatted}</span>',
            f'            <span class="article-hours {time_class}">',
            '              <span class="hours-icon">&#x23F3;</span>',
            f'              <span class="hours-value">{article["hours"]}</span> hours',
            '            </span>',
            f'            <span class="article-deaths">',
            '              <span class="deaths-icon">&#x2620;</span>',
            f'              <span class="deaths-value">{article["deaths"]}</span> deaths',
            '            </span>',
            '          </div>',
            '        </header>',
        ]
        
        # Таблица статистики
        if article['stats_table']:
            html_parts.extend([
                '        <div class="stats-section">',
                '          <h2 class="stats-title">Statistics</h2>',
                article['stats_table'],
                '        </div>',
            ])
        
        # Content
        html_parts.extend([
            '        <div class="article-content">',
            article['content'],
            '        </div>',
            '      </div>',
            '      <footer class="site-footer">',
            f'        <p>Roguelike Chronicles :: {year}</p>',
            '      </footer>',
            '    </main>',
            '  </div>',
            '  <script>',
            js_content,
            '  </script>',
            '</body>',
            '</html>'
        ])
        
        # Сохраняем страницу игры
        game_file = os.path.join(games_dir, f'{article["slug"]}.html')
        with open(game_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_parts))
        print(f"    -> games/{article['slug']}.html")
    
    # Генерируем главную страницу (index.html)
    game_cards = []
    for article in articles:
        try:
            dt = datetime.strptime(article['date'], '%Y-%m-%d')
            date_formatted = dt.strftime('%d.%m.%Y')
        except ValueError:
            date_formatted = article['date']
        
        time_class = get_time_class(article['hours'])
        
        # Берём первые 2 предложения как preview
        preview = re.split(r'(?<=[.!?])\s+', article['content'].replace('<p>', '').replace('</p>', '\n').replace('<br>', ' ')[:300])[0][:200] + '...'
        preview = re.sub(r'<[^>]+>', '', preview)  # Strip tags
        
        game_cards.append(
            f'<a href="games/{article["slug"]}.html" class="game-card">'
            f'  <div class="game-card-header">'
            f'    <h2 class="game-card-title">{article["title"]}</h2>'
            f'    <div class="game-card-meta">'
            f'      <span class="game-card-hours {time_class}">{article["hours"]}h</span>'
            f'      <span class="game-card-deaths">&#x2620; {article["deaths"]}</span>'
            f'    </div>'
            f'  </div>'
            f'  <div class="game-card-date">{date_formatted}</div>'
            f'  <p class="game-card-preview">{preview}</p>'
            f'  <div class="game-card-footer">'
            f'    <span class="game-card-link">Read more &rarr;</span>'
            f'  </div>'
            f'</a>'
        )
    
    # Навигация для главной страницы (все игры)
    main_nav = []
    for article in articles:
        main_nav.append(
            f'<li><a href="games/{article["slug"]}.html" class="nav-game-link">'
            f'<span class="nav-game-title">{article["title"]}</span>'
            f'<span class="nav-game-hours">{article["hours"]}h</span>'
            f'</a></li>'
        )
    main_nav_html = '\n'.join(main_nav)
    
    index_parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '  <title>Roguelike Chronicles</title>',
        '  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">',
        '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=VT323&family=JetBrains+Mono:wght@400;600;700&display=swap">',
        '  <style>',
        css_content,
        '  </style>',
        '</head>',
        '<body>',
        '  <div class="app">',
        # Sidebar
        '    <aside class="sidebar">',
        '      <div class="sidebar-header">',
        '        <a href="index.html" class="logo" title="Roguelike Chronicles">@</a>',
        '        <div class="subtitle">Roguelike Chronicles</div>',
        '      </div>',
        '      <nav class="sidebar-all-games">',
        '        <div class="all-games-label">Games</div>',
        '        <ul>',
        main_nav_html,
        '        </ul>',
        '      </nav>',
        '      <div class="sidebar-footer">',
        f'        <div class="total-hours">',
        f'          <span class="total-label">Total:</span>',
        f'          <span class="total-value">{total_hours}h</span>',
        f'          <span class="total-deaths">&#x2620; {total_deaths}</span>',
        '        </div>',
        '      </div>',
        '    </aside>',
        # Main content
        '    <main class="main main-index">',
        '      <div class="index-container">',
        '        <header class="index-header">',
        '          <h1>Roguelike Chronicles</h1>',
        '          <p class="index-subtitle">A journey through traditional roguelike games.</p>',
        '          <div class="index-stats">',
        f'            <div class="index-stat">',
        f'              <span class="index-stat-value">{len(articles)}</span>',
        f'              <span class="index-stat-label">games</span>',
        '            </div>',
        f'            <div class="index-stat">',
        f'              <span class="index-stat-value">{total_hours}</span>',
        f'              <span class="index-stat-label">hours</span>',
        '            </div>',
        f'            <div class="index-stat">',
        f'              <span class="index-stat-value">{total_deaths}</span>',
        f'              <span class="index-stat-label">deaths</span>',
        '            </div>',
        '          </div>',
        '        </header>',
        '        <div class="games-grid">',
        '\n'.join(game_cards),
        '        </div>',
        '      </div>',
        '      <footer class="site-footer">',
        f'        <p>Roguelike Chronicles :: {year}</p>',
        '      </footer>',
        '    </main>',
        '  </div>',
        '</body>',
        '</html>'
    ]
    
    index_file = os.path.join(base_dir, 'index.html')
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(index_parts))
    print(f"    -> index.html")
    
    print(f"\nDone! Generated {len(articles) + 1} pages")
    print(f"Total games: {len(articles)}")
    print(f"Total hours: {total_hours}")
    print(f"Total deaths: {total_deaths}")
    print(f"\nOpen index.html in browser to view")


if __name__ == '__main__':
    build()
