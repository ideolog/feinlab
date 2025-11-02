# FeinLab / Extractor — извлечение данных из PDF

1. Распакуй архив проекта (zip)

2. Открой терминал и перейди в папку проекта:
cd feinlab

3. Создай виртуальное окружение:
python -m venv .venv

4. Активируй виртуальное окружение:
source .venv/bin/activate

5. Открой проект feinlab c помощью Pycharm

6. Установи зависимости:
pip install --upgrade pip
pip install -r requirements.txt

6. Обнови файл .env в корне проекта рядом с manage.py
Открой страницу https://platform.openai.com/settings/organization/api-keys
Сгенерируй свой API-ключ
Вставь в .env строку:
OPENAI_API_KEY=твой_ключ_сюда_без_всяких_кавычек

7. Помести PDF-файлы в папку:
PDF/

8. Запуск обработки статей:
   - Только статьи на крысах (режим по умолчанию):
`python manage.py beloch `
   - Разрешить крыс и мышей:
`python manage.py beloch --gate rodent `
   - Игнорировать вид, но требовать in vivo single-unit или LFP:
`python manage.py beloch --gate any`

9. Результаты появятся в папке:
OUT/
Формат имен файлов:
имя_статьи.gate.json
Например:
OUT/elife-85069.rodent.json

10. Если нужно редактировать PROMPT то он лежит в PROMPT.txt в корне проекта.
Но! Не забудь что там еще часть промта добавляется в обработчике extractor/management/commands/process_papers.py - я его специально завел, чтобы можно было не игнорировать мышей и прочих зверушек 
