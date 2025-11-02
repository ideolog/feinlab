# FeinLab / Extractor — извлечение данных из PDF

1. Установи git если нет.
2. Открой терминал и скопируй этот проект:
`git clone https://github.com/ideolog/feinlab.git`

3. Открой терминал и перейди в папку проекта:
`cd feinlab`

4. Создай виртуальное окружение:
`python -m venv .venv`

5. Активируй виртуальное окружение:
`source .venv/bin/activate`

6. Открой проект feinlab c помощью Pycharm

7. Установи зависимости:
````bash
pip install --upgrade pip
pip install -r requirements.txt
````

6. Обнови файл .env в корне проекта рядом с manage.py
- Открой  https://platform.openai.com/settings/organization/api-keys
- Сгенерируй свой API-ключ
- Вставь в .env строку:
`OPENAI_API_KEY=твой_ключ_сюда_без_всяких_кавычек`

7. Помести PDF-файлы в папку:
PDF/

8. Запуск обработки статей:
`python manage.py beloch`

9. Результаты появятся в папке:
OUT/
Формат имен файлов:
`имя_статьи.json`
10. 
Например:
`OUT/elife-85069.json`

10. Если нужно редактировать PROMPT, то он лежит в PROMPT.txt в корне проекта.

ฅ^•ﻌ•^ฅ 

