import threading
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import math
import tkinter as tk

PALETTES = {
    "原图自动配色": None,
    "NES色板": [
        (124, 124, 124), (0, 0, 252), (0, 0, 188), (68, 40, 188),
        (148, 0, 132), (168, 0, 32), (168, 16, 0), (136, 20, 0),
        (80, 48, 0), (0, 120, 0), (0, 104, 0), (0, 88, 0),
        (0, 64, 88), (0, 0, 0)
    ],
    "GBA色板": [
        (255, 255, 255), (255, 192, 203), (255, 165, 0), (173, 216, 230),
        (0, 255, 0), (255, 255, 0), (255, 0, 0), (0, 0, 255),
        (128, 0, 128), (0, 0, 0)
    ],
    "Game Boy色板": [
        (155, 188, 15), (139, 172, 15), (48, 98, 48), (15, 56, 15)
    ],
    "MSX2色板": [
        (0, 0, 0), (31, 31, 192), (15, 191, 15), (191, 191, 0),
        (191, 0, 0), (191, 0, 191), (0, 191, 191), (191, 191, 191),
        (63, 63, 63), (95, 95, 255), (95, 255, 95), (255, 255, 63),
        (255, 63, 63), (255, 63, 255), (63, 255, 255), (255, 255, 255)
    ],
    "C64色板": [
        (0, 0, 0), (255, 255, 255), (136, 0, 0), (170, 255, 238),
        (204, 68, 204), (0, 204, 85), (0, 0, 170), (238, 238, 119),
        (204, 136, 136), (102, 68, 0), (255, 119, 119), (51, 51, 51),
        (119, 119, 119), (170, 255, 102), (0, 136, 255), (187, 187, 187)
    ],
    "霓虹色板": [
        (255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0),
        (0, 255, 0), (0, 0, 255), (255, 128, 0), (128, 0, 255),
        (255, 255, 255)
    ],
    "荧光色板": [
        (0, 255, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (255, 128, 0), (128, 255, 0), (0, 128, 255), (255, 0, 128),
        (255, 255, 255)
    ]
}

def find_nearest_color(color, palette):
    r, g, b = color
    min_dist = float('inf')
    nearest_color = None
    for pr, pg, pb in palette:
        dist = math.sqrt((r - pr)**2 + (g - pg)**2 + (b - pb)**2)
        if dist < min_dist:
            min_dist = dist
            nearest_color = (pr, pg, pb)
    return nearest_color

def apply_palette(img, palette):
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            original_color = pixels[x, y]
            new_color = find_nearest_color(original_color, palette)
            pixels[x, y] = new_color
    return img

def process_image(img_path, pixel_size, color_count, palette_name):
    img = Image.open(img_path)
    small_img = img.resize((pixel_size, pixel_size), Image.NEAREST)

    if palette_name == "原图自动配色":
        small_img = small_img.convert('P', palette=Image.ADAPTIVE, colors=color_count).convert('RGB')
    else:
        small_img = apply_palette(small_img, PALETTES[palette_name])

    return small_img

def update_preview():
    if not hasattr(update_preview, 'img_original'):
        return

    try:
        pixel_size = int(pixel_size_entry.get())
        color_count = int(color_count_entry.get())
        selected_palette = palette_var.get()

        thread = threading.Thread(target=_thread_process_and_update, args=(pixel_size, color_count, selected_palette))
        thread.start()
    except ValueError:
        messagebox.showwarning("警告", "请输入有效的数值！")

def _thread_process_and_update(pixel_size, color_count, selected_palette):
    processed_img = process_image(update_preview.img_path, pixel_size, color_count, selected_palette)

    preview_size = (300, 300)
    processed_img = processed_img.resize(preview_size, Image.NEAREST)
    
    processed_img_tk = ImageTk.PhotoImage(processed_img)

    window.after(0, lambda: preview_canvas.delete("all"))
    window.after(0, lambda: preview_canvas.create_image(0, 0, anchor='nw', image=processed_img_tk))
    window.after(0, lambda: setattr(preview_canvas, 'image', processed_img_tk))

def save_processed_image():
    if not hasattr(preview_canvas, 'image'):
        messagebox.showinfo("提示", "请先生成预览图像！")
        return

    output_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Files", "*.png")]
    )
    if output_path:
        try:
            img = preview_canvas.image._PhotoImage__photo
            img.write(output_path, format='png')
            messagebox.showinfo("成功", f"图像已保存至：{output_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

def select_image():
    file_path = filedialog.askopenfilename(
        title="选择一张图片",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
    )
    if file_path:
        try:
            original_img = Image.open(file_path)
            original_img.thumbnail((300, 300))
            tk_img = ImageTk.PhotoImage(original_img)

            original_canvas.delete("all")
            original_canvas.create_image(0, 0, anchor='nw', image=tk_img)
            original_canvas.image = tk_img

            update_preview.img_path = file_path
            update_preview.img_original = original_img

            update_preview()
        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败：\n{e}")

def reset_parameters():
    pixel_size_entry.delete(0, tk.END)
    pixel_size_entry.insert(0, "32")
    color_count_entry.delete(0, tk.END)
    color_count_entry.insert(0, "16")
    palette_var.set("原图自动配色")

def create_gui():
    global window, original_canvas, preview_canvas, pixel_size_entry, color_count_entry, palette_var

    window = tk.Tk()
    window.title("图片转像素精灵图 - 专业版")
    window.geometry("900x400")
    window.resizable(True, True)

    panes = tk.PanedWindow(window, orient=tk.HORIZONTAL)
    panes.pack(fill=tk.BOTH, expand=True)

    left_frame = tk.Frame(panes)
    panes.add(left_frame)

    tk.Label(left_frame, text="原图", font=("Arial", 12)).pack()
    original_canvas = tk.Canvas(left_frame, width=300, height=300, bg="white")
    original_canvas.pack(padx=10, pady=10)


    mid_frame = tk.Frame(panes)
    panes.add(mid_frame) 

    param_frame = tk.Frame(mid_frame)
    param_frame.pack(pady=10)



    tk.Label(param_frame, text="缩小到像素数：").grid(row=0, column=0, padx=5, pady=2)
    pixel_size_entry = tk.Entry(param_frame, width=10)
    pixel_size_entry.insert(0, "32")
    pixel_size_entry.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(param_frame, text="保留颜色数：").grid(row=1, column=0, padx=5, pady=2)
    color_count_entry = tk.Entry(param_frame, width=10)
    color_count_entry.insert(0, "16")
    color_count_entry.grid(row=1, column=1, padx=5, pady=2)

    palette_frame = tk.Frame(mid_frame)
    palette_frame.pack(pady=5)
    tk.Label(palette_frame, text="选择色板：").pack()
    palette_var = tk.StringVar()
    palette_var.set("原图自动配色")

    style = ttk.Style()
    style.configure("WhiteText.TCombobox", foreground="white")

    palette_menu = ttk.Combobox(palette_frame, textvariable=palette_var,
                                values=list(PALETTES.keys()), state="readonly", width=15,
                                style="WhiteText.TCombobox")
    palette_menu.pack()

    btn_frame = tk.Frame(mid_frame)
    btn_frame.pack(pady=20)

    btn_common_style = {
        "font": ("Arial", 10, "bold"),
        "bd": 0,
        "relief": "flat",
        "highlightthickness": 0,
        "padx": 8,
        "pady": 4
    }

    select_btn = tk.Button(btn_frame, text="选择图片", command=select_image,
                        bg="#4CAF50", fg="gray", width=10, **btn_common_style)
    select_btn.pack(pady=5)

    apply_btn = tk.Button(btn_frame, text="应用参数", command=update_preview,
                        bg="#FFA726", fg="gray", width=10, **btn_common_style)
    apply_btn.pack(pady=3)

    save_btn = tk.Button(btn_frame, text="另存为", command=save_processed_image,
                       bg="#2E7D32", fg="gray", width=10, **btn_common_style)
    save_btn.pack(pady=3)

    reset_btn = tk.Button(btn_frame, text="重置参数", command=reset_parameters,
                        bg="#FFC107", fg="gray", width=10, **btn_common_style)
    reset_btn.pack(pady=3)

    right_frame = tk.Frame(panes)
    panes.add(right_frame)

    tk.Label(right_frame, text="预览", font=("Arial", 12)).pack()
    preview_canvas = tk.Canvas(right_frame, width=300, height=300, bg="white")
    preview_canvas.pack(padx=10, pady=10)

    window.mainloop()

if __name__ == "__main__":
    create_gui()