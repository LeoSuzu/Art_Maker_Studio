from datetime import datetime
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import turtle

import colorgram
from PIL import Image, ImageGrab, ImageTk

from circle_art import CircleArt
from dot_art import DotArtMaker
from random_walk_art import RandomWalkArt


APP_BG = "#0f172a"
PANEL_BG = "#111827"
CARD_BG = "#f8fafc"
ACCENT = "#f97316"
CANVAS_BG = "#fffaf0"
TEXT_DARK = "#0f172a"
TEXT_LIGHT = "#e5eefc"
APP_NAME = "Art Maker Studio"
OUTPUT_DIR = Path.home() / "ArtMakerStudioExports"
CANVAS_WIDTH = 980
CANVAS_HEIGHT = 700

brightness_threshold = 400
palette_amount = 50
filepath = ""
rgb_colors = []
turtle_canvas = None
turtle_screen = None

size_mapping = {
    "A4": {"steps": 900, "turtles": 42},
    "A3": {"steps": 1300, "turtles": 54},
    "A2": {"steps": 1800, "turtles": 66},
}


window = tk.Tk()
window.title(APP_NAME)
window.geometry("1500x920")
window.configure(bg=APP_BG)
window.minsize(1320, 860)


style = ttk.Style()
style.theme_use("clam")
style.configure("Sidebar.TFrame", background=PANEL_BG)
style.configure("CanvasCard.TFrame", background=CARD_BG)
style.configure("SidebarTitle.TLabel", background=PANEL_BG, foreground="white", font=("Avenir Next", 24, "bold"))
style.configure("SidebarText.TLabel", background=PANEL_BG, foreground=TEXT_LIGHT, font=("Avenir Next", 11))
style.configure("CardTitle.TLabel", background=CARD_BG, foreground=TEXT_DARK, font=("Avenir Next", 16, "bold"))
style.configure("CardText.TLabel", background=CARD_BG, foreground="#475569", font=("Avenir Next", 10))
style.configure("Art.TButton", background=ACCENT, foreground="white", borderwidth=0, focusthickness=0, focuscolor=ACCENT, font=("Avenir Next", 11, "bold"), padding=(14, 10))
style.map("Art.TButton", background=[("active", "#ea580c")])
style.configure("Secondary.TButton", background="#dbe4f0", foreground=TEXT_DARK, borderwidth=0, font=("Avenir Next", 10, "bold"), padding=(12, 9))
style.map("Secondary.TButton", background=[("active", "#c4d2e3")])
style.configure("Studio.TCombobox", fieldbackground="white", padding=6)
style.configure("Studio.TCheckbutton", background=PANEL_BG, foreground=TEXT_LIGHT, font=("Avenir Next", 10))


image_var = tk.StringVar(value="Valitse kuva väripaletin lähteeksi")
status_var = tk.StringVar(value="Lataa kuva ja valitse taidetyyli.")
art_var = tk.StringVar(value="Dot Art")
dot_var = tk.StringVar(value="100")
size_var = tk.StringVar(value="A3")
circle_var = tk.StringVar(value="7")
autosave_var = tk.BooleanVar(value=True)


def get_output_dir():
    if getattr(sys, "frozen", False):
        return Path.home() / "ArtMakerStudioExports"
    return OUTPUT_DIR


def create_turtle_surface():
    global turtle_canvas, turtle_screen

    if turtle_canvas is not None:
        turtle_canvas.destroy()

    turtle_canvas = tk.Canvas(
        canvas_host,
        width=CANVAS_WIDTH,
        height=CANVAS_HEIGHT,
        bg=CANVAS_BG,
        bd=0,
        highlightthickness=0,
    )
    turtle_canvas.pack(fill="both", expand=True, padx=24, pady=24)

    turtle_screen = turtle.TurtleScreen(turtle_canvas)
    turtle_screen.bgcolor(CANVAS_BG)
    turtle_screen.colormode(255)
    turtle_screen.tracer(0, 0)


def extract_palette(selected_path):
    colors = colorgram.extract(selected_path, palette_amount)
    palette = []

    for color in colors:
        r = color.rgb.r
        g = color.rgb.g
        b = color.rgb.b
        brightness = (r + g + b) / 3

        if brightness < brightness_threshold:
            rgb = (r, g, b)
            if rgb not in palette:
                palette.append(rgb)

        if len(palette) >= 100:
            break

    return palette


def show_image_preview(selected_path):
    image = Image.open(selected_path)
    width, height = image.size
    preview_width = 290
    preview_height = int(height * preview_width / width)
    preview = image.resize((preview_width, preview_height), Image.LANCZOS)
    photo = ImageTk.PhotoImage(preview)
    preview_label.configure(image=photo, text="")
    preview_label.image = photo


def choose_image():
    global filepath, rgb_colors

    selected_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )

    if not selected_path:
        return

    try:
        palette = extract_palette(selected_path)
    except Exception as exc:
        messagebox.showerror("Virhe", f"Kuvan analysointi ei onnistunut:\n{exc}")
        return

    if not palette:
        messagebox.showerror("Virhe", "Kuvasta ei löytynyt tarpeeksi värejä. Kokeile toista kuvaa.")
        return

    filepath = selected_path
    rgb_colors = palette
    image_var.set(Path(selected_path).name)
    status_var.set(f"Kuva ladattu. Paletissa {len(rgb_colors)} uniikkia väriä.")
    show_image_preview(selected_path)


def update_parameter_controls(*_args):
    for widget in parameter_row.winfo_children():
        widget.destroy()

    ttk.Label(parameter_row, text="Asetukset", style="SidebarText.TLabel").pack(anchor="w", pady=(0, 8))

    selected_art = art_var.get()
    if selected_art == "Dot Art":
        ttk.Label(parameter_row, text="Pisteiden määrä", style="SidebarText.TLabel").pack(anchor="w")
        ttk.Combobox(
            parameter_row,
            textvariable=dot_var,
            values=["100", "225", "400"],
            state="readonly",
            style="Studio.TCombobox",
        ).pack(fill="x", pady=(6, 0))
    elif selected_art == "Random Walk Art":
        ttk.Label(parameter_row, text="Komposition koko", style="SidebarText.TLabel").pack(anchor="w")
        ttk.Combobox(
            parameter_row,
            textvariable=size_var,
            values=list(size_mapping.keys()),
            state="readonly",
            style="Studio.TCombobox",
        ).pack(fill="x", pady=(6, 0))
    else:
        ttk.Label(parameter_row, text="Ympyräryhmien määrä", style="SidebarText.TLabel").pack(anchor="w")
        ttk.Combobox(
            parameter_row,
            textvariable=circle_var,
            values=["5", "7", "10", "14"],
            state="readonly",
            style="Studio.TCombobox",
        ).pack(fill="x", pady=(6, 0))


def export_art():
    if turtle_canvas is None:
        raise RuntimeError("Canvasia ei ole vielä luotu.")

    output_dir = get_output_dir()
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base_name = f"{art_var.get().lower().replace(' ', '_')}-{timestamp}"

    window.update()

    postscript_path = output_dir / f"{base_name}.ps"
    turtle_canvas.postscript(file=postscript_path, colormode="color")

    x = turtle_canvas.winfo_rootx()
    y = turtle_canvas.winfo_rooty()
    x1 = x + turtle_canvas.winfo_width()
    y1 = y + turtle_canvas.winfo_height()

    image = ImageGrab.grab(bbox=(x, y, x1, y1))
    png_path = output_dir / f"{base_name}.png"
    jpg_path = output_dir / f"{base_name}.jpg"
    image.save(png_path)
    image.convert("RGB").save(jpg_path, quality=95)

    return png_path, jpg_path, postscript_path


def create_art():
    if not filepath or not rgb_colors:
        messagebox.showerror("Virhe", "Valitse ensin kuva, jotta värit saadaan poimittua.")
        return

    create_turtle_surface()
    status_var.set("Piirretään uutta versiota...")
    window.update_idletasks()

    try:
        selected_art = art_var.get()
        if selected_art == "Dot Art":
            DotArtMaker(turtle_screen, CANVAS_WIDTH, CANVAS_HEIGHT, rgb_colors, dot_var.get()).create_dot_art()
        elif selected_art == "Random Walk Art":
            size_config = size_mapping[size_var.get()]
            RandomWalkArt(
                turtle_screen,
                CANVAS_WIDTH,
                CANVAS_HEIGHT,
                turtle_count=size_config["turtles"],
            ).random_walk(size_config["steps"], rgb_colors)
        else:
            CircleArt(turtle_screen, CANVAS_WIDTH, CANVAS_HEIGHT).draw_art(rgb_colors, circle_var.get())

        saved_copy = ""
        if autosave_var.get():
            _, jpg_path, _ = export_art()
            saved_copy = f" Tallennettu automaattisesti: {jpg_path.name}"

        status_var.set(f"{selected_art} valmis.{saved_copy}")
    except Exception as exc:
        status_var.set("Piirtäminen epäonnistui.")
        messagebox.showerror("Virhe", f"Piirtäminen epäonnistui:\n{exc}")


def save_current_art():
    if turtle_canvas is None:
        messagebox.showerror("Virhe", "Luo ensin art, jotta sen voi tallentaa.")
        return

    try:
        png_path, jpg_path, postscript_path = export_art()
    except Exception as exc:
        messagebox.showerror("Virhe", f"Tallennus epäonnistui:\n{exc}")
        return

    status_var.set(
        f"Tallennettu: {png_path.name}, {jpg_path.name} ja {postscript_path.name}"
    )


def quit_app():
    window.destroy()


layout = tk.Frame(window, bg=APP_BG)
layout.pack(fill="both", expand=True, padx=24, pady=24)

sidebar = ttk.Frame(layout, style="Sidebar.TFrame", padding=24)
sidebar.pack(side="left", fill="y")

canvas_card = ttk.Frame(layout, style="CanvasCard.TFrame", padding=0)
canvas_card.pack(side="right", fill="both", expand=True, padx=(20, 0))

ttk.Label(sidebar, text="Art Maker", style="SidebarTitle.TLabel").pack(anchor="w")
ttk.Label(
    sidebar,
    text="Vanha turtle-projekti uudella studiologikalla: vakaampi piirto, satunnaisempi random walk ja automaattinen export.",
    style="SidebarText.TLabel",
    wraplength=300,
).pack(anchor="w", pady=(6, 20))

ttk.Button(sidebar, text="Valitse kuva", command=choose_image, style="Art.TButton").pack(fill="x")
ttk.Label(sidebar, textvariable=image_var, style="SidebarText.TLabel", wraplength=300).pack(anchor="w", pady=(10, 16))

preview_shell = tk.Frame(sidebar, bg="#1e293b", bd=0, highlightthickness=0)
preview_shell.pack(fill="x", pady=(0, 18))
preview_label = tk.Label(
    preview_shell,
    text="Kuvan esikatselu",
    bg="#1e293b",
    fg="#cbd5e1",
    font=("Avenir Next", 11, "bold"),
    width=32,
    height=12,
)
preview_label.pack(fill="both", expand=True, padx=12, pady=12)

ttk.Label(sidebar, text="Taidetyyli", style="SidebarText.TLabel").pack(anchor="w")
ttk.Combobox(
    sidebar,
    textvariable=art_var,
    values=["Dot Art", "Random Walk Art", "Circle Art"],
    state="readonly",
    style="Studio.TCombobox",
).pack(fill="x", pady=(6, 18))

parameter_row = ttk.Frame(sidebar, style="Sidebar.TFrame")
parameter_row.pack(fill="x", pady=(0, 18))

ttk.Checkbutton(
    sidebar,
    text="Tallenna valmis art automaattisesti",
    variable=autosave_var,
    style="Studio.TCheckbutton",
).pack(anchor="w", pady=(0, 18))

button_row = ttk.Frame(sidebar, style="Sidebar.TFrame")
button_row.pack(fill="x")
ttk.Button(button_row, text="Luo Art", command=create_art, style="Art.TButton").pack(fill="x")
ttk.Button(button_row, text="Tallenna Uudelleen", command=save_current_art, style="Secondary.TButton").pack(fill="x", pady=(10, 0))
ttk.Button(button_row, text="Sulje", command=quit_app, style="Secondary.TButton").pack(fill="x", pady=(10, 0))

status_card = tk.Frame(sidebar, bg="#0b1220")
status_card.pack(fill="x", pady=(20, 0))
tk.Label(
    status_card,
    textvariable=status_var,
    bg="#0b1220",
    fg="#f8fafc",
    justify="left",
    wraplength=300,
    padx=14,
    pady=14,
    font=("Avenir Next", 10),
).pack(fill="x")

header = tk.Frame(canvas_card, bg=CARD_BG)
header.pack(fill="x", padx=24, pady=(24, 0))
tk.Label(
    header,
    text="Creative Canvas",
    bg=CARD_BG,
    fg=TEXT_DARK,
    font=("Avenir Next", 22, "bold"),
).pack(anchor="w")
tk.Label(
    header,
    text="Sama canvas palvelee kaikkia art-malleja, joten tyylin vaihto ei enää kaada sovellusta.",
    bg=CARD_BG,
    fg="#64748b",
    font=("Avenir Next", 11),
).pack(anchor="w", pady=(4, 0))

canvas_host = tk.Frame(canvas_card, bg="#e2e8f0", bd=0, highlightthickness=0)
canvas_host.pack(fill="both", expand=True, padx=24, pady=24)

update_parameter_controls()
art_var.trace_add("write", update_parameter_controls)
create_turtle_surface()

window.mainloop()
