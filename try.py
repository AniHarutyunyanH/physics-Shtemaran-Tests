import fitz  # PyMuPDF
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import re
import random

# =========================================================
# === НАСТРОЙКИ ТЕКСТА (МЕНЯЙТЕ НАЗВАНИЯ ТУТ) ===
# =========================================================
STRINGS = {
    "file_1_name": "Ֆիզիկա շտեմարան 1",
    "file_2_name": "Ֆիզիկա շտեմարան 2",
    "mode_combined": "Ֆիզիկա շտեմարան 1 և 2 միասին",
    
    "btn_load": "բացել",
    "btn_random": "Ռանդոմ",
    "btn_add_error": "+",
    "btn_errors_list": "Սխալները",
    "btn_show_ans": "ցույց տալ պատասխանը",
    "btn_clear_errors": "մաքրել սխալները",
    "check_only_test": "Միայն թեստային",
    
    "label_task_num": "№:",
    "msg_correct": "✅ ապրես!",
    "msg_wrong": "❌ Այ ապուշ!",
    "msg_added": "քցված է սխալների ցանկին",
    "start_title": "ընտրի շտեմարանը՝",
    "title_main": "Shtemaran Quiz Master v2.2"
}

FILES_CONFIG = {
    "FILE 1": {
        "tasks": "shtem1.pdf",
        "answers": "shtem1pat.pdf",
        "ranges": [(1, 125), (201, 306), (402, 553), (618, 667), (689, 746),
                   (777, 880), (950, 1060), (1132, 1234), (1310, 1427),
                   (1496, 1600), (1687, 1819), (1928, 2035)],
        "max_task": 2035
    },
    "FILE 2": {
        "tasks": "shtem2.pdf",
        "answers": "shtem2pat.pdf",
        "ranges": [(1, 124), (201, 305), (401, 438), (465, 554), (619, 667), 
                   (690, 747), (778, 880), (951, 1060), (1133, 1234), 
                   (1311, 1428), (1495, 1597), (1687, 1819), (1927, 2031)],
        "max_task": 2031
    }
}

COLORS = {
    "bg": "#f0f2f5", "primary": "#3f51b5", "secondary": "#2c3e50",
    "accent": "#ff9800", "white": "#ffffff"
}

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title(STRINGS["title_main"])
        self.root.geometry("1000x900")
        self.root.configure(bg=COLORS["bg"])
        
        self.wrong_answers = set() 
        self.current_mode = None   
        self.active_file = "FILE 1"
        self.current_task = None
        self.img_tk = None
        self.only_test_var = tk.BooleanVar(value=False)

        self.show_start_screen()

    def show_start_screen(self):
        self.start_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.start_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(self.start_frame, text=STRINGS["start_title"], font=("Helvetica", 18, "bold"), 
                 bg=COLORS["bg"], fg=COLORS["secondary"]).pack(pady=30)

        modes = [
            (STRINGS["file_1_name"], "FILE 1"),
            (STRINGS["file_2_name"], "FILE 2"),
            (STRINGS["mode_combined"], "COMBINED")
        ]
        
        for display_name, internal_name in modes:
            btn = tk.Button(self.start_frame, text=display_name, width=40, height=2,
                            font=("Helvetica", 12, "bold"), bg=COLORS["primary"], fg="white",
                            command=lambda m=internal_name: self.start_quiz(m), cursor="hand2", relief=tk.FLAT)
            btn.pack(pady=10)

    def start_quiz(self, mode):
        self.current_mode = mode
        self.start_frame.destroy()
        self.setup_main_ui()
        self.load_random_task()

    def setup_main_ui(self):
        # Панель управления
        self.header = tk.Frame(self.root, bg=COLORS["secondary"], height=60)
        self.header.pack(side=tk.TOP, fill=tk.X)
        
        # Левая часть
        self.info_label = tk.Label(self.header, text="", bg=COLORS["secondary"], fg="#cbd5e0", font=("Helvetica", 10, "bold"))
        self.info_label.pack(side=tk.LEFT, padx=15)

        tk.Label(self.header, text=STRINGS["label_task_num"], bg=COLORS["secondary"], fg="white", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        
        self.task_entry = tk.Entry(self.header, width=6, font=("Helvetica", 14), justify='center')
        self.task_entry.pack(side=tk.LEFT, padx=5, pady=10)

        self.create_nav_button(STRINGS["btn_load"], self.load_task, COLORS["primary"]).pack(side=tk.LEFT, padx=5)
        self.create_nav_button(STRINGS["btn_random"], self.load_random_task, COLORS["primary"]).pack(side=tk.LEFT, padx=5)
        
        # Галочка
        self.test_check = tk.Checkbutton(self.header, text=STRINGS["check_only_test"], variable=self.only_test_var,
                                        bg=COLORS["secondary"], fg="white", selectcolor=COLORS["secondary"],
                                        activebackground=COLORS["secondary"], activeforeground="white",
                                        font=("Helvetica", 9))
        self.test_check.pack(side=tk.LEFT, padx=10)

        # Правая часть
        self.create_nav_button(STRINGS["btn_errors_list"], self.show_wrong_list, "#607d8b").pack(side=tk.RIGHT, padx=15)
        self.create_nav_button(STRINGS["btn_add_error"], self.add_to_wrong, COLORS["accent"]).pack(side=tk.RIGHT, padx=5)

        # ХОЛСТ (Canvas)
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        self.footer = tk.Frame(self.root, bg=COLORS["bg"])
        self.footer.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        self.btn_container = tk.Frame(self.footer, bg=COLORS["bg"])
        self.btn_container.pack()

    def create_nav_button(self, text, command, color):
        return tk.Button(self.header, text=text, command=command, bg=color, fg="white",
                        font=("Helvetica", 9, "bold"), relief=tk.FLAT, padx=12, pady=5)

    def is_choice_task(self, file_key, n):
        ranges = FILES_CONFIG[file_key]["ranges"]
        return any(start <= n <= end for start, end in ranges)

    def load_task(self, specific_n=None, file_to_use=None):
        try:
            n = specific_n if specific_n else int(self.task_entry.get())
            if self.current_mode in ["FILE 1", "FILE 2"]:
                self.active_file = self.current_mode
            elif file_to_use:
                self.active_file = file_to_use

            img = self.get_task_image(self.active_file, n)
            if img:
                self.img_tk = ImageTk.PhotoImage(img)
                self.canvas.delete("all")
                
                # ИСПРАВЛЕНИЕ ТУТ: координаты (0, 0) и anchor=tk.NW (North-West)
                # Это гарантирует, что верхний левый угол картинки совпадет с верхним левым углом канваса
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)
                
                self.canvas.config(scrollregion=self.canvas.bbox("all"))
                self.current_task = n
                self.task_entry.delete(0, tk.END)
                self.task_entry.insert(0, str(n))
                
                display_file_name = STRINGS["file_1_name"] if self.active_file == "FILE 1" else STRINGS["file_2_name"]
                self.info_label.config(text=display_file_name)
                self.update_buttons(n)
            else:
                messagebox.showerror("Error", f"Task {n} not found")
        except: pass

    def load_random_task(self):
        attempts = 0
        while attempts < 1000:
            if self.current_mode == "COMBINED":
                temp_file = random.choice(["FILE 1", "FILE 2"])
            else:
                temp_file = self.current_mode
            n = random.randint(1, FILES_CONFIG[temp_file]["max_task"])
            if not self.only_test_var.get() or self.is_choice_task(temp_file, n):
                self.active_file = temp_file
                self.load_task(n)
                break
            attempts += 1

    def update_buttons(self, n):
        for widget in self.btn_container.winfo_children(): widget.destroy()
        if self.is_choice_task(self.active_file, n):
            for i in range(1, 5):
                tk.Button(self.btn_container, text=str(i), width=7, height=2,
                          font=("Helvetica", 14, "bold"), bg=COLORS["white"], relief=tk.GROOVE,
                          command=lambda v=i: self.process_choice(v)).pack(side=tk.LEFT, padx=10)
        else:
            tk.Button(self.btn_container, text=STRINGS["btn_show_ans"], 
                      bg=COLORS["accent"], fg="white", font=("Helvetica", 12, "bold"),
                      relief=tk.FLAT, command=self.show_full_answer, padx=30, pady=10).pack()

    def process_choice(self, val):
        ans = self.get_answer_data(self.active_file, self.current_task)
        nums = re.findall(r'\d', ans) if ans else []
        correct = nums[0] if nums else "?"
        if str(val) == correct:
            messagebox.showinfo(STRINGS["msg_correct"], f"Ճիշտ է!")
            self.load_random_task()
        else:
            messagebox.showerror(STRINGS["msg_wrong"], f"Ճիշտ պատասխանն էր՝ {correct}")
            self.wrong_answers.add((self.active_file, self.current_task))

    def show_full_answer(self):
        ans = self.get_answer_data(self.active_file, self.current_task)
        if messagebox.askyesno(STRINGS["btn_show_ans"], f"{ans}\n\nավելացնել սխալների մեջ?"):
            self.wrong_answers.add((self.active_file, self.current_task))
        self.load_random_task()

    def get_task_image(self, file_key, n, dpi=160):
        try:
            doc = fitz.open(FILES_CONFIG[file_key]["tasks"])
            start_label, end_label = f"{n}.", f"{n+1}."
            start, end = None, None
            for page in doc:
                words = page.get_text("words")
                for w in words:
                    if w[4] == start_label: start = (page.number, w[1] - 15)
                    if start and w[4] == end_label: end = (page.number, w[1] - 5); break
                if start and end: break
            if not start or not end: return None
            
            parts = []
            for p_idx in range(start[0], end[0] + 1):
                page = doc[p_idx]
                if p_idx == start[0] and p_idx == end[0]: clip = fitz.Rect(0, start[1], page.rect.width, end[1])
                elif p_idx == start[0]: clip = fitz.Rect(0, start[1], page.rect.width, page.rect.height)
                elif p_idx == end[0]: clip = fitz.Rect(0, 0, page.rect.width, end[1])
                else: clip = page.rect
                pix = page.get_pixmap(clip=clip, dpi=dpi)
                parts.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
            
            combined = Image.new("RGB", (max(i.width for i in parts), sum(i.height for i in parts)), (255, 255, 255))
            y = 0
            for i in parts: combined.paste(i, (0, y)); y += i.height
            return combined
        except: return None

    def get_answer_data(self, file_key, n):
        try:
            doc = fitz.open(FILES_CONFIG[file_key]["answers"])
            text = "".join([p.get_text() for p in doc])
            pattern = f"{n}\.(.*?){n+1}\."
            match = re.search(pattern, text, re.DOTALL)
            return match.group(1).strip() if match else None
        except: return None

    def add_to_wrong(self):
        self.wrong_answers.add((self.active_file, self.current_task))
        messagebox.showinfo("OK", STRINGS["msg_added"])

    def clear_errors(self, win):
        self.wrong_answers.clear()
        win.destroy()
        messagebox.showinfo("Очищено", "Ցանկը դատարկ է")

    def show_wrong_list(self):
        if not self.wrong_answers:
            messagebox.showinfo("Пусто", "Սխալներ չկան")
            return
        win = tk.Toplevel(self.root)
        win.title(STRINGS["btn_errors_list"])
        win.geometry("350x450")
        frame = tk.Frame(win)
        frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        for f, n in sorted(list(self.wrong_answers)):
            disp = STRINGS["file_1_name"] if f == "FILE 1" else STRINGS["file_2_name"]
            tk.Button(frame, text=f"{disp}: №{n}", anchor="w", padx=10,
                      command=lambda f=f, n=n: [self.load_task(n, f), win.destroy()]).pack(fill=tk.X, pady=1)
        tk.Button(win, text=STRINGS["btn_clear_errors"], bg="#e53e3e", fg="white", 
                  command=lambda: self.clear_errors(win)).pack(fill=tk.X, padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = QuizApp(root)
    root.mainloop()