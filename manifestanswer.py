import fitz
import re
import json

def extract_all_answers():
    all_data = {"shtem1": {}, "shtem2": {}}
    files = ["shtem1pat.pdf", "shtem2pat.pdf"]
    
    for pdf_path in files:
        doc = fitz.open(pdf_path)
        key = "shtem1" if "1" in pdf_path else "shtem2"
        
        # Получаем полный текст из всех страниц
        full_text = ""
        for page in doc:
            full_text += page.get_text("text") + "\n"
        
        # Разбиваем текст на блоки по номеру задачи (например, "199.")
        # re.split создаст список: [пусто, "199", "контент 199", "200", "контент 200"]
        blocks = re.split(r'\n(\d+)\.\s*', full_text)
        
        for i in range(1, len(blocks), 2):
            tid = blocks[i]
            content = blocks[i+1]
            
            # Игнорируем номера страниц (если блок слишком короткий)
            if len(content.strip()) < 2:
                continue
            
            # Регулярка: ищем числа, которые стоят после ")" 
            # Это исключает номера вариантов (1, 2, 3...)
            answers = re.findall(r'\)\s*(\d+)', content)
            
            # Если такой формат не найден (задача 439. 800:), 
            # берем просто все числа в блоке
            if not answers:
                answers = re.findall(r'(\d+)(?=\s*[:])', content)
            
            if answers:
                all_data[key][tid] = answers

    with open("answers.json", "w", encoding="utf8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print("Файл answers_final.json успешно создан!")

extract_all_answers()