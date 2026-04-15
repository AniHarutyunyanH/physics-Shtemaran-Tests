import fitz
import json

def visualize_rects(pdf_path, json_data):
    doc = fitz.open(pdf_path)
    # Ищем все задачи для конкретного файла
    for task in json_data["tasks"]:
        if task["file"] == pdf_path:
            page = doc[task["page"]]
            # Передаем список координат напрямую в Rect
            rect = fitz.Rect(task["rect"])
            
            # Рисуем красный прямоугольник
            page.draw_rect(rect, color=(1, 0, 0), width=2)
            # Добавляем номер задачи
            page.insert_text(rect.tl, str(task["id"]), color=(1, 0, 0), fontsize=20)
    
    output_filename = "debug_" + pdf_path
    doc.save(output_filename)
    print(f"Готово! Файл {output_filename} сохранен. Открой его в PDF-вьюере.")

# 1. Загружаем твой JSON
with open("manifest.json", "r", encoding="utf8") as f:
    my_manifest_json = json.load(f)

# 2. Запускаем визуализацию для каждого PDF
visualize_rects("shtem1.pdf", my_manifest_json)
visualize_rects("shtem2.pdf", my_manifest_json)
