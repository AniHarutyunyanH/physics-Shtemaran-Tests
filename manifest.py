import fitz
import json

def get_task_coordinates(pdf_path):
    doc = fitz.open(pdf_path)
    manifest_tasks = []

    for page_num, page in enumerate(doc):
        # Получаем все текстовые блоки с их координатами
        blocks = page.get_text("blocks")
        # Сортируем блоки сверху вниз, слева направо
        blocks.sort(key=lambda b: (b[1], b[0]))

        for i, block in enumerate(blocks):
            x0, y0, x1, y1, text, block_no, block_type = block
            
            # Ищем начало задачи (например, "1. ", "2. " и т.д.)
            import re
            match = re.match(r"^\s*(\d+)\.", text.strip())
            if match:
                task_id = int(match.group(1))
                
                # Координаты начала (где номер задачи)
                start_y = y0
                
                # Координаты конца задачи: 
                # Ищем следующий блок, который начинается с цифры или конец страницы
                end_y = page.rect.height
                for j in range(i + 1, len(blocks)):
                    next_text = blocks[j][4].strip()
                    if re.match(r"^\s*\d+\.", next_text):
                        end_y = blocks[j][1] # Начало следующей задачи
                        break
                
                manifest_tasks.append({
                    "id": task_id,
                    "file": pdf_path.split("/")[-1],
                    "page": page_num,
                    "rect": [0, start_y, page.rect.width, end_y] # Широкий прямоугольник для захвата всей ширины
                })
    return manifest_tasks

# Обработка обоих файлов
all_tasks = []
all_tasks.extend(get_task_coordinates("shtem1.pdf"))
all_tasks.extend(get_task_coordinates("shtem2.pdf"))

with open("manifest.json", "w", encoding="utf8") as f:
    json.dump({"tasks": all_tasks}, f, indent=2, ensure_ascii=False)