from tkinter import ttk
import tkinter as tk
from tkinter import filedialog, colorchooser, font as tkfont, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

# ------------------- КЛАСС ТЕКСТОВОГО ОБЪЕКТА -------------------
class TextObject:
    def __init__(self, text, x, y, font, color):
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.width = 0
        self.height = 0
        self.update_size()

    def update_size(self):
        dummy_img = Image.new('RGB', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        try:
            bbox = dummy_draw.textbbox((0, 0), self.text, font=self.font)
            self.width = bbox[2] - bbox[0]
            self.height = bbox[3] - bbox[1]
        except:
            self.width, self.height = 100, 40

    def contains(self, x, y):
        return (self.x <= x <= self.x + self.width) and (self.y <= y <= self.y + self.height)


# ------------------- ГЛАВНОЕ ПРИЛОЖЕНИЕ -------------------
class AdvancedImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 WinPaint Pro")
        self.root.geometry("1300x800")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#2e3b2c")

        # Иконка (если есть logo.png)
        self.set_window_icon("logo.png")

        # ---------- РАБОЧИЕ ПЕРЕМЕННЫЕ ----------
        # Сразу создаём status_var, чтобы избежать ошибок
        self.status_var = tk.StringVar()
        self.status_var.set("Загрузка...")

        self.original_image = None   # исходный фон (без текстов)
        self.working_image = None    # фон + рисунки кистью (тексты хранятся отдельно)
        self.text_objects = []       # список TextObject
        self.selected_text = None    # выбранный текстовый объект
        self.drag_start_x = None
        self.drag_start_y = None
        self.tk_image = None

        # Режимы
        self.tool_mode = "brush"     # "brush", "text", "move"

        # Рисование кистью
        self.pen_color = "#000000"
        self.pen_size = 5
        self.last_x, self.last_y = None, None
        self.is_drawing = False

        # Текст по умолчанию
        self.font_family = tk.StringVar(value="Arial")
        self.font_size = tk.IntVar(value=28)
        self.text_color = "#000000"
        self.text_input = tk.StringVar(value="Новый текст")

        # Доступные шрифты
        self.available_fonts = list(tkfont.families())

        # Построение GUI (важен порядок!)
        self.create_menu()
        self.create_toolbar()   # здесь НЕ вызываем set_tool
        self.create_canvas()
        self.create_statusbar()  # создаём статус-бар

        # Теперь можно безопасно устанавливать режим
        self.set_tool("brush")

        # Создаём пустой холст
        self.new_image(900, 600, "white")

        # Привязка событий
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    # ------------------- ИКОНКА -------------------
    def set_window_icon(self, icon_path):
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                icon = ImageTk.PhotoImage(img.resize((64, 64), Image.Resampling.LANCZOS))
                self.root.iconphoto(True, icon)
            except:
                pass

    # ------------------- GUI КОМПОНЕНТЫ -------------------
    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="📂 Загрузить", command=self.load_image, accelerator="Ctrl+O")
        file_menu.add_command(label="💾 Сохранить", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="🆕 Новый холст", command=self.new_image_dialog)
        file_menu.add_command(label="❌ Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="🗑️ Сброс рисунков", command=self.reset_drawings)
        edit_menu.add_command(label="🔄 Объединить текст с фоном", command=self.merge_text_to_image)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        self.root.config(menu=menubar)
        self.root.bind("<Control-o>", lambda e: self.load_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg="#4a5b47", bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Режимы
        self.brush_btn = tk.Button(toolbar, text="🖌️ Кисть", command=lambda: self.set_tool("brush"), bg="#e0e0e0")
        self.brush_btn.pack(side=tk.LEFT, padx=4, pady=4)
        self.text_btn = tk.Button(toolbar, text="✍️ Текст", command=lambda: self.set_tool("text"), bg="#f0f0f0")
        self.text_btn.pack(side=tk.LEFT, padx=4)
        self.move_btn = tk.Button(toolbar, text="🖱️ Переместить текст", command=lambda: self.set_tool("move"), bg="#f0f0f0")
        self.move_btn.pack(side=tk.LEFT, padx=4)

        sep = tk.Frame(toolbar, width=2, bg="#aaa", height=30)
        sep.pack(side=tk.LEFT, padx=6, pady=2)

        # Настройки кисти
        self.color_btn = tk.Button(toolbar, text="🎨 Цвет кисти", command=self.choose_pen_color)
        self.color_btn.pack(side=tk.LEFT, padx=4)
        self.color_preview = tk.Label(toolbar, text="    ", bg=self.pen_color, width=3, relief=tk.SUNKEN)
        self.color_preview.pack(side=tk.LEFT, padx=2)

        tk.Label(toolbar, text="Размер:", bg="#4a5b47", fg="white").pack(side=tk.LEFT, padx=(8,2))
        self.size_slider = tk.Scale(toolbar, from_=1, to=30, orient=tk.HORIZONTAL, length=100,
                                    command=self.update_pen_size, bg="#4a5b47", fg="white", highlightthickness=0)
        self.size_slider.set(self.pen_size)
        self.size_slider.pack(side=tk.LEFT, padx=4)

        # Настройки текста
        sep2 = tk.Frame(toolbar, width=2, bg="#aaa", height=30)
        sep2.pack(side=tk.LEFT, padx=6)
        tk.Label(toolbar, text="Текст:", bg="#4a5b47", fg="white").pack(side=tk.LEFT)
        self.text_entry = tk.Entry(toolbar, textvariable=self.text_input, width=15)
        self.text_entry.pack(side=tk.LEFT, padx=4)

        tk.Label(toolbar, text="Шрифт:", bg="#4a5b47", fg="white").pack(side=tk.LEFT)
        self.font_combo = ttk.Combobox(toolbar, textvariable=self.font_family, values=self.available_fonts, width=12)
        self.font_combo.pack(side=tk.LEFT, padx=4)

        tk.Label(toolbar, text="Размер шрифта:", bg="#4a5b47", fg="white").pack(side=tk.LEFT)
        self.font_size_spin = tk.Spinbox(toolbar, from_=8, to=120, width=5, textvariable=self.font_size)
        self.font_size_spin.pack(side=tk.LEFT, padx=4)

        self.text_color_btn = tk.Button(toolbar, text="🎨 Цвет текста", command=self.choose_text_color)
        self.text_color_btn.pack(side=tk.LEFT, padx=4)
        self.text_color_preview = tk.Label(toolbar, text="    ", bg=self.text_color, width=3, relief=tk.SUNKEN)
        self.text_color_preview.pack(side=tk.LEFT, padx=2)

        self.add_text_btn = tk.Button(toolbar, text="➕ Добавить текст", command=self.add_new_text, bg="#6d8f66", fg="white")
        self.add_text_btn.pack(side=tk.LEFT, padx=8)

        # Кнопка сброса
        reset_btn = tk.Button(toolbar, text="🗑️ Сброс рисунков", command=self.reset_drawings, bg="#b86b5a", fg="white")
        reset_btn.pack(side=tk.LEFT, padx=8)

        # ВНИМАНИЕ: здесь НЕТ вызова set_tool("brush") — он будет вызван в __init__ после создания статус-бара

    def create_canvas(self):
        canvas_frame = tk.Frame(self.root, bg="#2e3b2c")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(canvas_frame, bg="#d9d2b0", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_statusbar(self):
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN,
                              anchor=tk.W, bg="#e2dccd")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ------------------- УПРАВЛЕНИЕ РЕЖИМАМИ -------------------
    def set_tool(self, mode):
        self.tool_mode = mode
        # Визуальное выделение кнопок
        for btn, color in [(self.brush_btn, "#e0e0e0"), (self.text_btn, "#f0f0f0"), (self.move_btn, "#f0f0f0")]:
            btn.config(bg=color)
        if mode == "brush":
            self.brush_btn.config(bg="#c0e0c0")
            self.status_var.set("Режим: Кисть — рисуйте левой кнопкой")
            self.canvas.config(cursor="pencil")
        elif mode == "text":
            self.text_btn.config(bg="#c0e0c0")
            self.status_var.set("Режим: Текст — кликните на холсте, чтобы добавить текст")
            self.canvas.config(cursor="xterm")
        elif mode == "move":
            self.move_btn.config(bg="#c0e0c0")
            self.status_var.set("Режим: Перемещение — кликните по тексту и перетащите")
            self.canvas.config(cursor="hand2")

    # ------------------- РАБОТА С ИЗОБРАЖЕНИЕМ -------------------
    def new_image(self, width, height, color="white"):
        self.original_image = Image.new("RGB", (width, height), color)
        self.working_image = self.original_image.copy()
        self.text_objects.clear()
        self.selected_text = None
        self.update_full_display()

    def new_image_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Новый холст")
        dialog.geometry("300x150")
        tk.Label(dialog, text="Ширина:").pack(pady=5)
        w_entry = tk.Entry(dialog)
        w_entry.insert(0, "900")
        w_entry.pack()
        tk.Label(dialog, text="Высота:").pack(pady=5)
        h_entry = tk.Entry(dialog)
        h_entry.insert(0, "600")
        h_entry.pack()
        def create():
            try:
                w = int(w_entry.get())
                h = int(h_entry.get())
                if w > 0 and h > 0:
                    self.new_image(w, h, "white")
                    dialog.destroy()
            except:
                self.status_var.set("Некорректные размеры")
        tk.Button(dialog, text="Создать", command=create).pack(pady=10)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            img = Image.open(path).convert("RGB")
            self.original_image = img.copy()
            self.working_image = img.copy()
            self.text_objects.clear()
            self.selected_text = None
            self.update_full_display()
            self.status_var.set(f"Загружено: {os.path.basename(path)}")

    def save_image(self):
        if self.working_image is None:
            return
        # Сохраняем вместе с текстом (накладываем тексты на working_image)
        final = self.working_image.copy()
        for txt_obj in self.text_objects:
            draw = ImageDraw.Draw(final)
            draw.text((txt_obj.x, txt_obj.y), txt_obj.text, font=txt_obj.font, fill=txt_obj.color)
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if path:
            final.save(path)
            self.status_var.set(f"Сохранено: {os.path.basename(path)}")

    def reset_drawings(self):
        """Сброс рисунков кистью, но текст остаётся"""
        self.working_image = self.original_image.copy()
        self.update_full_display()
        self.status_var.set("Рисунки кистью удалены, текст сохранён")

    def merge_text_to_image(self):
        """Приклеить текст к фону (текст больше нельзя перемещать)"""
        for txt in self.text_objects:
            draw = ImageDraw.Draw(self.working_image)
            draw.text((txt.x, txt.y), txt.text, font=txt.font, fill=txt.color)
        self.text_objects.clear()
        self.selected_text = None
        self.original_image = self.working_image.copy()
        self.update_full_display()
        self.status_var.set("Текст объединён с изображением")

    # ------------------- ОТРИСОВКА ВСЕГО ХОЛСТА -------------------
    def update_full_display(self):
        """Обновляет canvas: фон + все тексты поверх вручную (без изменения working_image)"""
        # Сначала показываем working_image (фон + рисунки кистью)
        display_img = self.working_image.copy()
        # Рисуем все тексты поверх
        draw = ImageDraw.Draw(display_img)
        for txt in self.text_objects:
            draw.text((txt.x, txt.y), txt.text, font=txt.font, fill=txt.color)
        # Если текст выбран, рисуем рамку
        if self.selected_text:
            draw.rectangle(
                [self.selected_text.x, self.selected_text.y,
                 self.selected_text.x + self.selected_text.width,
                 self.selected_text.y + self.selected_text.height],
                outline="red", width=2
            )
        # Масштабирование под размеры canvas
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w <= 1:
            canvas_w = 900
        if canvas_h <= 1:
            canvas_h = 600
        display_img.thumbnail((canvas_w - 20, canvas_h - 20), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(display_img)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_w // 2, canvas_h // 2, anchor=tk.CENTER, image=self.tk_image)
        self.canvas.image = self.tk_image

    def _get_image_coords(self, event):
        """Возвращает координаты мыши относительно изображения (учитывая масштаб)"""
        if not self.tk_image:
            return event.x, event.y
        img_w = self.tk_image.width()
        img_h = self.tk_image.height()
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        x_offset = (canvas_w - img_w) // 2
        y_offset = (canvas_h - img_h) // 2
        img_x = event.x - x_offset
        img_y = event.y - y_offset
        # Ограничение границами изображения
        img_x = max(0, min(img_x, img_w))
        img_y = max(0, min(img_y, img_h))
        # Масштабируем обратно к оригинальному разрешению working_image
        real_w, real_h = self.working_image.size
        scale_x = real_w / img_w
        scale_y = real_h / img_h
        return int(img_x * scale_x), int(img_y * scale_y)

    # ------------------- РИСОВАНИЕ КИСТЬЮ -------------------
    def choose_pen_color(self):
        col = colorchooser.askcolor(color=self.pen_color)[1]
        if col:
            self.pen_color = col
            self.color_preview.config(bg=self.pen_color)

    def update_pen_size(self, val):
        self.pen_size = int(val)

    def start_brush(self, x, y):
        self.is_drawing = True
        self.last_x, self.last_y = x, y
        # Рисуем точку
        draw = ImageDraw.Draw(self.working_image)
        r = self.pen_size // 2
        draw.ellipse((x - r, y - r, x + r, y + r), fill=self.pen_color)
        self.update_full_display()

    def draw_brush_line(self, x1, y1, x2, y2):
        draw = ImageDraw.Draw(self.working_image)
        draw.line([(x1, y1), (x2, y2)], fill=self.pen_color, width=self.pen_size)
        self.update_full_display()

    # ------------------- ДОБАВЛЕНИЕ ТЕКСТА -------------------
    def choose_text_color(self):
        col = colorchooser.askcolor(color=self.text_color)[1]
        if col:
            self.text_color = col
            self.text_color_preview.config(bg=self.text_color)

    def add_new_text(self):
        # Добавление текста в центр экрана
        real_w, real_h = self.working_image.size
        center_x = real_w // 2
        center_y = real_h // 2
        self.create_text_object(center_x, center_y)

    def create_text_object(self, x, y):
        text_str = self.text_input.get()
        if not text_str.strip():
            text_str = "Текст"
        try:
            font = ImageFont.truetype(self.font_family.get() + ".ttf", self.font_size.get())
        except:
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size.get())
            except:
                font = ImageFont.load_default()
        new_text = TextObject(text_str, x, y, font, self.text_color)
        new_text.update_size()
        self.text_objects.append(new_text)
        self.update_full_display()
        self.status_var.set(f"Текст '{text_str}' добавлен в ({x},{y})")

    # ------------------- ПЕРЕМЕЩЕНИЕ ТЕКСТА -------------------
    def find_text_at(self, x, y):
        for txt in reversed(self.text_objects):
            if txt.contains(x, y):
                return txt
        return None

    # ------------------- ОБРАБОТЧИКИ МЫШИ -------------------
    def on_mouse_down(self, event):
        img_x, img_y = self._get_image_coords(event)

        if self.tool_mode == "brush":
            self.start_brush(img_x, img_y)

        elif self.tool_mode == "text":
            self.create_text_object(img_x, img_y)

        elif self.tool_mode == "move":
            clicked = self.find_text_at(img_x, img_y)
            if clicked:
                self.selected_text = clicked
                self.drag_start_x = img_x - clicked.x
                self.drag_start_y = img_y - clicked.y
                self.update_full_display()
                self.status_var.set(f"Выбран текст: {clicked.text}")
            else:
                self.selected_text = None
                self.update_full_display()

    def on_mouse_move(self, event):
        img_x, img_y = self._get_image_coords(event)

        if self.tool_mode == "brush" and self.is_drawing:
            if self.last_x is not None and self.last_y is not None:
                self.draw_brush_line(self.last_x, self.last_y, img_x, img_y)
            self.last_x, self.last_y = img_x, img_y

        elif self.tool_mode == "move" and self.selected_text:
            # Перемещаем выбранный текст
            new_x = img_x - self.drag_start_x
            new_y = img_y - self.drag_start_y
            # Ограничиваем, чтобы текст не уходил за пределы
            max_x = self.working_image.width - self.selected_text.width
            max_y = self.working_image.height - self.selected_text.height
            new_x = max(0, min(new_x, max_x))
            new_y = max(0, min(new_y, max_y))
            self.selected_text.x = new_x
            self.selected_text.y = new_y
            self.update_full_display()

    def on_mouse_up(self, event):
        if self.tool_mode == "brush":
            self.is_drawing = False
            self.last_x, self.last_y = None, None
            # Сохраняем текущее состояние фона как новый оригинал для сброса рисунков
            self.original_image = self.working_image.copy()
        elif self.tool_mode == "move":
            self.drag_start_x = None
            self.drag_start_y = None
            self.status_var.set("Текст перемещён")


# ------------------- ЗАПУСК -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedImageEditor(root)
    root.mainloop()
