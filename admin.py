"""
Flask-приложение для управления проектами строительства.
Поддерживает полный CRUD через REST API.

Установка зависимостей:
    pip install flask flask-cors

Запуск (для разработки):
    python projects_api.py

Для production (WSGI):
    Используйте gunicorn или uWSGI с этим файлом.
"""

import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- НАСТРОЙКИ ---
DATA_FILE = "projects_data.json"
app = Flask(__name__)
CORS(app)  # Разрешаем кросс-доменные запросы

# --- ДАННЫЕ ПО УМОЛЧАНИЮ ---
DEFAULT_PROJECTS = [
    {
        "id": 1,
        "title": "Дом в ЖК «Солнечный»",
        "image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80",
        "area": "145 м²",
        "material": "Газобетон",
        "finish": "Чистовая",
        "time": "5 месяцев",
        "description": "Современный двухэтажный дом в жилом комплексе «Солнечный». Просторная терраса, панорамные окна и продуманная планировка. 4 спальни, большая кухня-столовая, камин.",
        "features": {
            "foundation": "Монолитная плита",
            "walls": "Газобетон D500 + утепление",
            "ceilings": "Монолитные ж/б",
            "windows": "Двухкамерные стеклопакеты (Rehau)",
            "utilities": "Автономное отопление, водоснабжение"
        },
        "review": "«Приятно удивила чистота на стройке и соблюдение сроков»"
    },
    {
        "id": 2,
        "title": "Коттедж в пос. Залесный",
        "image": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&q=80",
        "area": "98 м²",
        "material": "Кирпич",
        "finish": "Премиум",
        "time": "6 месяцев",
        "description": "Уютный одноэтажный кирпичный дом в экологически чистом районе. Классический английский стиль, качественная отделка из натуральных материалов. 3 спальни, гостиная с выходом на террасу.",
        "features": {
            "foundation": "Ленточный глубокого заложения",
            "walls": "Кирпич керамический 2,5 кирпича",
            "ceilings": "Деревянные балки",
            "windows": "Деревянные евроокна",
            "utilities": "Газовое отопление, центральное водоснабжение"
        },
        "review": "«Сделали даже лучше, чем мы представляли. Спасибо команде!»"
    },
    {
        "id": 3,
        "title": "Дом с мансардой в СНТ «Березка»",
        "image": "https://images.unsplash.com/photo-1600573472591-ee6981cf35b3?w=800&q=80",
        "area": "210 м²",
        "material": "Дерево (брус)",
        "finish": "Чистовая",
        "time": "7 месяцев",
        "description": "Двухэтажный деревянный дом с просторной мансардой. Натуральный брус создаёт уникальный микроклимат. 5 спален, большой зал, сауна.",
        "features": {
            "foundation": "Винтовые сваи",
            "walls": "Профилированный брус 200x200",
            "ceilings": "Деревянные перекрытия",
            "windows": "Двухкамерные, деревянные",
            "utilities": "Автономное газовое отопление, септик"
        },
        "review": "«Всё прозрачно, вовремя, без доплат. Рекомендуем!»"
    },
    {
        "id": 4,
        "title": "Скандинавский дом в «Зелёной долине»",
        "image": "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=800&q=80",
        "area": "132 м²",
        "material": "Каркас",
        "finish": "Чистовая",
        "time": "4 месяца",
        "description": "Стильный скандинавский дом по финской технологии. Быстровозводимый каркасный дом с большими панорамными окнами. Терраса по всему периметру. 3 спальни, кухня-гостиная, кабинет.",
        "features": {
            "foundation": "Утеплённая шведская плита (УШП)",
            "walls": "Каркас 150x150, утепление 200 мм",
            "ceilings": "Деревянные фермы",
            "windows": "Трёхкамерные стеклопакеты",
            "utilities": "Электрическое отопление, водоснабжение"
        },
        "review": "«Построили дом мечты! Отдельное спасибо за террасу»"
    },
    {
        "id": 5,
        "title": "Дом с бассейном в коттеджном посёлке",
        "image": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800&q=80",
        "area": "280 м²",
        "material": "Кирпич",
        "finish": "Премиум",
        "time": "10 месяцев",
        "description": "Роскошный двухэтажный особняк с собственным бассейном и террасой. Классическая архитектура, качественные материалы. 6 спален, домашний кинотеатр, бассейн с подогревом.",
        "features": {
            "foundation": "Монолитная плита с цокольным этажом",
            "walls": "Кирпич облицовочный + газобетон",
            "ceilings": "Монолитные ж/б",
            "windows": "Алюминиевые с терморазрывом",
            "utilities": "Автономное газовое отопление, водоснабжение, бассейн"
        },
        "review": "«Дом получился роскошным. Все пожелания учтены!»"
    },
    {
        "id": 6,
        "title": "Таунхаус в центре Казани",
        "image": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&q=80",
        "area": "180 м²",
        "material": "Газобетон",
        "finish": "Чистовая",
        "time": "8 месяцев",
        "description": "Современный таунхаус в центральном районе Казани. Удобная планировка, два уровня, небольшая придомовая территория. 4 спальни, просторная гостиная, 2 санузла, гардеробная.",
        "features": {
            "foundation": "Ленточный мелкого заложения",
            "walls": "Газобетон D600 + облицовочный кирпич",
            "ceilings": "Монолитные ж/б",
            "windows": "Двухкамерные стеклопакеты (Rehau)",
            "utilities": "Центральное отопление, водоснабжение, канализация"
        },
        "review": "«Строили в стеснённых условиях, справились отлично»"
    }
]


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def load_projects():
    """Загружает проекты из JSON-файла."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except (json.JSONDecodeError, IOError):
            pass
    # Если файла нет или он повреждён — создаём с дефолтными данными
    save_projects(DEFAULT_PROJECTS)
    return DEFAULT_PROJECTS


def save_projects(projects):
    """Сохраняет проекты в JSON-файл."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)


def get_next_id(projects):
    """Возвращает следующий доступный ID."""
    if not projects:
        return 1
    return max(p.get("id", 0) for p in projects) + 1


def validate_project(data):
    """Проверяет обязательные поля."""
    required = ["title", "image"]
    missing = [field for field in required if field not in data or not data[field]]
    if missing:
        return False, f"Обязательные поля: {', '.join(missing)}"
    return True, "OK"


# --- API ROUTES ---

@app.route("/api/projects", methods=["GET"])
def get_projects():
    """Получить список всех проектов."""
    projects = load_projects()
    return jsonify({
        "success": True,
        "data": projects,
        "count": len(projects)
    })


@app.route("/api/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    """Получить проект по ID."""
    projects = load_projects()
    project = next((p for p in projects if p.get("id") == project_id), None)
    if project:
        return jsonify({
            "success": True,
            "data": project
        })
    return jsonify({
        "success": False,
        "error": f"Проект с ID {project_id} не найден"
    }), 404


@app.route("/api/projects", methods=["POST"])
def add_project():
    """Добавить новый проект."""
    data = request.get_json()
    if data is None:
        return jsonify({
            "success": False,
            "error": "Неверный JSON"
        }), 400

    valid, msg = validate_project(data)
    if not valid:
        return jsonify({
            "success": False,
            "error": msg
        }), 400

    projects = load_projects()
    
    # Если id не передан или уже существует — генерируем новый
    if "id" not in data or any(p.get("id") == data["id"] for p in projects):
        data["id"] = get_next_id(projects)
    else:
        if any(p.get("id") == data["id"] for p in projects):
            return jsonify({
                "success": False,
                "error": f"Проект с ID {data['id']} уже существует"
            }), 400

    projects.append(data)
    save_projects(projects)

    return jsonify({
        "success": True,
        "message": "Проект добавлен",
        "data": data
    }), 201


@app.route("/api/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    """Обновить существующий проект."""
    data = request.get_json()
    if data is None:
        return jsonify({
            "success": False,
            "error": "Неверный JSON"
        }), 400

    projects = load_projects()
    index = next((i for i, p in enumerate(projects) if p.get("id") == project_id), None)

    if index is None:
        return jsonify({
            "success": False,
            "error": f"Проект с ID {project_id} не найден"
        }), 404

    # Сохраняем id и обновляем остальные поля
    data["id"] = project_id
    projects[index] = data
    save_projects(projects)

    return jsonify({
        "success": True,
        "message": "Проект обновлён",
        "data": data
    })


@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    """Удалить проект."""
    projects = load_projects()
    new_projects = [p for p in projects if p.get("id") != project_id]

    if len(new_projects) == len(projects):
        return jsonify({
            "success": False,
            "error": f"Проект с ID {project_id} не найден"
        }), 404

    save_projects(new_projects)
    return jsonify({
        "success": True,
        "message": f"Проект с ID {project_id} удалён"
    })


@app.route("/api/projects/reset", methods=["POST"])
def reset_projects():
    """Сбросить проекты к значениям по умолчанию."""
    save_projects(DEFAULT_PROJECTS)
    return jsonify({
        "success": True,
        "message": "Проекты сброшены к значениям по умолчанию",
        "count": len(DEFAULT_PROJECTS)
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Проверка работоспособности."""
    return jsonify({
        "status": "ok",
        "message": "API работает"
    })


@app.errorhandler(404)
def not_found(error):
    """Обработчик 404."""
    return jsonify({
        "success": False,
        "error": "Endpoint не найден"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик 500."""
    return jsonify({
        "success": False,
        "error": "Внутренняя ошибка сервера"
    }), 500


# --- ЗАПУСК ДЛЯ РАЗРАБОТКИ ---
if __name__ == "__main__":
    print("🚀 Запуск Flask-сервера...")
    print(f"📁 Данные хранятся в файле: {DATA_FILE}")
    print("\nДоступные endpoints:")
    print("  GET  /api/projects           — получить все проекты")
    print("  GET  /api/projects/<id>     — получить проект по ID")
    print("  POST /api/projects          — добавить проект")
    print("  PUT  /api/projects/<id>     — обновить проект")
    print("  DELETE /api/projects/<id>   — удалить проект")
    print("  POST /api/projects/reset    — сбросить к дефолту")
    print("  GET  /api/health            — проверка состояния")
    print("\n🌐 http://localhost:5000")
    print("Нажмите Ctrl+C для остановки\n")
    
    app.run(host="0.0.0.0", port=5000, debug=True)