from datetime import datetime
from pathlib import Path
import sys
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk
import turtle

import colorgram
from PIL import Image, ImageTk
import subprocess
import tempfile

from circle_art import CircleArt
from dot_art import DotArtMaker
from random_walk_art import RandomWalkArt
from raster_recorder import RasterRecorder


APP_BG = "#0f172a"
PANEL_BG = "#111827"
CARD_BG = "#f8fafc"
ACCENT = "#f97316"
TEXT_DARK = "#0f172a"
TEXT_LIGHT = "#e5eefc"
APP_NAME = "Art Maker Studio"
OUTPUT_DIR = Path.home() / "ArtMakerStudioExports"

# Canvas dimensions based on art type and settings
# Format: (width, height)
# Dot Art's canvas is computed dynamically from the chosen grid (see get_dot_grid /
# dot_canvas_size below) so it always matches the actual number of rows/cols.
canvas_sizes = {
    "Random Walk Art": {
        "A4": (1600, 900),
        "A3": (1600, 900),
        "A2": (1600, 900),
    },
    "Circle Art": {
        "all": (1600, 900),
    },
}

DOT_CELL_SIZE = 55
DOT_CANVAS_MARGIN = 100
DOT_CANVAS_MIN = 500

# Named colors that Tk (and therefore turtle, which draws through Tk) is
# guaranteed to understand, offered as quick background presets.
BACKGROUND_COLOR_CHOICES = [
    "white", "ivory", "lightyellow", "honeydew", "aliceblue", "lavenderblush",
    "lightgray", "gainsboro", "black", "midnightblue", "darkslategray", "Custom...",
]

brightness_threshold = 400
palette_amount = 50
filepath = ""
rgb_colors = []

size_mapping = {
    "A4": {"steps": 150, "turtles": 42},
    "A3": {"steps": 250, "turtles": 54},
    "A2": {"steps": 350, "turtles": 66},
}


window = tk.Tk()
window.title(APP_NAME)
# Make the main control window compact (sidebar only) so no large empty area appears
window.geometry("380x940")
# Aut resize depend of content
window.resizable(True, True)
window.grid_rowconfigure(0, weight=1)
window.configure(bg=APP_BG)
window.minsize(380, 940)
    # window.maxsize(380, 1040)  # Removed to allow window to grow


style = ttk.Style()
style.theme_use("clam")
style.configure("Sidebar.TFrame", background=PANEL_BG)
style.configure("CanvasCard.TFrame", background=CARD_BG)
style.configure("SidebarTitle.TLabel", background=PANEL_BG, foreground="white", font=("Avenir Next", 24, "bold"))
style.configure("SidebarText.TLabel", background=PANEL_BG, foreground=TEXT_LIGHT, font=("Avenir Next", 11))
style.configure("CardTitle.TLabel", background=CARD_BG, foreground=TEXT_DARK, font=("Avenir Next", 16, "bold"))
style.configure("CardText.TLabel", background=CARD_BG, foreground="#475569", font=("Avenir Next", 10))
style.configure("Art.TButton", background=ACCENT, foreground="white", borderwidth=0, focusthickness=0, focuscolor=ACCENT, font=("Avenir Next", 11, "bold"), padding=(12, 8))
style.map("Art.TButton", background=[("active", "#ea580c")])
style.configure("Secondary.TButton", background="#dbe4f0", foreground=TEXT_DARK, borderwidth=0, font=("Avenir Next", 10, "bold"), padding=(10, 6))
style.map("Secondary.TButton", background=[("active", "#c4d2e3")])
style.configure("Studio.TCombobox", fieldbackground="white", padding=6)
style.configure("Studio.TCheckbutton", background=PANEL_BG, foreground=TEXT_LIGHT, font=("Avenir Next", 10))


image_var = tk.StringVar(value="Valitse kuva väripaletin lähteeksi")
status_var = tk.StringVar(value="Lataa kuva ja valitse taidetyyli.")
art_var = tk.StringVar(value="Dot Art")
dot_var = tk.StringVar(value="100 - Square")
dot_grid_config = {
    "100": {"cols": 10, "rows": 10},
    "200": {"cols": 20, "rows": 10},
    "300": {"cols": 20, "rows": 15},
}
size_var = tk.StringVar(value="A3")
circle_count_var = tk.IntVar(value=7)
circle_thickness_var = tk.IntVar(value=6)
circle_size_var = tk.IntVar(value=120)
autosave_var = tk.BooleanVar(value=False)
bg_color_var = tk.StringVar(value="white")


def get_output_dir():
    if getattr(sys, "frozen", False):
        return Path.home() / "ArtMakerStudioExports"
    return OUTPUT_DIR


def get_dot_grid(sel):
    """Parse a dot-art combobox value like '64 - Square' or
    '120 (10x12) - Rectangle' into (dot_count, cols, rows).

    Computing the grid here (instead of looking it up in a separate table
    keyed by the full label string) is what keeps the canvas size and the
    actual dot grid in sync — previously the lookup table's keys didn't
    match the combobox values, so the canvas defaulted to a fixed 600x600
    square no matter which option was picked.
    """
    import re
    import math

    m = re.search(r"(\d+)", sel)
    dot_count = int(m.group(1)) if m else 100

    dims = re.search(r"\((\d+)x(\d+)\)", sel)
    if dims:
        cols, rows = int(dims.group(1)), int(dims.group(2))
    else:
        size = max(1, math.ceil(math.sqrt(dot_count)))
        cols, rows = size, size

    return dot_count, cols, rows


def dot_canvas_size(sel):
    _dot_count, cols, rows = get_dot_grid(sel)
    width = max(DOT_CANVAS_MIN, cols * DOT_CELL_SIZE + DOT_CANVAS_MARGIN)
    height = max(DOT_CANVAS_MIN, rows * DOT_CELL_SIZE + DOT_CANVAS_MARGIN)
    return width, height


def create_turtle_surface():
    """Create a new turtle screen for drawing art"""
    # Use turtle module's native window management instead of embedding in tkinter
    # This avoids the TurtleScreen + Toplevel incompatibility issue
    # Get or create the turtle screen and reset it so each run starts fresh.
    # Handle the case where the previous turtle window was closed by recreating the screen.
    try:
        turtle_screen = turtle.getscreen()
        # ensure canvas exists; will raise if screen was closed
        _ = turtle_screen.getcanvas()
        try:
            # clear() removes every turtle that was ever created on this
            # screen. reset() (the old code path) instead resets each
            # leftover turtle to its initial state, which means showturtle()
            # — so stray turtles from previous runs reappeared as visible
            # arrow cursors sitting at the canvas center. clear() avoids that.
            turtle_screen.clear()
        except Exception:
            try:
                turtle_screen.reset()
            except Exception:
                pass
    except Exception:
        # previous screen missing or closed; create a fresh one
        try:
            turtle_screen = turtle.Screen()
        except Exception:
            # Last resort: create an implicit Tk root then a screen
            import tkinter as _tk

            _root = _tk.Tk()
            _root.withdraw()
            turtle_screen = turtle.Screen()

    turtle_screen.bgcolor(bg_color_var.get())
    turtle_screen.colormode(255)
    turtle_screen.tracer(0, 0)

    # Determine canvas size based on current art type and settings
    art_type = art_var.get()
    if art_type == "Dot Art":
        canvas_width, canvas_height = dot_canvas_size(dot_var.get())
    elif art_type == "Random Walk Art":
        key = size_var.get()
        canvas_width, canvas_height = canvas_sizes["Random Walk Art"].get(key, (1000, 800))
    else:  # Circle Art
        canvas_width, canvas_height = canvas_sizes["Circle Art"]["all"]

    # Setup the window
    turtle_screen.setup(width=canvas_width, height=canvas_height)
    turtle_screen.title(f"{APP_NAME} - {art_type}")

    # Set up world coordinates centered at (0, 0)
    half_width = canvas_width / 2
    half_height = canvas_height / 2
    turtle_screen.setworldcoordinates(-half_width, -half_height, half_width, half_height)

    return turtle_screen, canvas_width, canvas_height


def extract_palette(selected_path):
    # colorgram.extract walks every pixel in pure Python, so on a large photo
    # (e.g. a 12MP phone picture) it can take a very long time. Downscaling
    # to a small thumbnail first keeps the same color palette while cutting
    # the pixel count down by orders of magnitude, making this near-instant.
    tmp_path = None
    try:
        with Image.open(selected_path) as image:
            thumbnail = image.convert("RGB")
            thumbnail.thumbnail((300, 300), Image.LANCZOS)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                tmp_path = tmp_file.name
            thumbnail.save(tmp_path)
        colors = colorgram.extract(tmp_path, palette_amount)
    finally:
        if tmp_path:
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass

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


PREVIEW_MAX_WIDTH = 290
PREVIEW_MAX_HEIGHT = 220


def show_image_preview(selected_path):
    # The preview box has a fixed size (see preview_shell's pack_propagate(False)
    # below), so we letterbox the thumbnail to fit inside it instead of resizing
    # the window to match the photo's aspect ratio — a tall portrait photo used
    # to inflate the window height enough to push the buttons off-screen.
    image = Image.open(selected_path)
    preview = image.copy()
    preview.thumbnail((PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT), Image.LANCZOS)
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
            values=[
                "64 - Square",
                "100 - Square",
                "196 - Square",
                "256 - Square",
                "361 - Square",
                "120 (10x12) - Rectangle",
                "180 (12x15) - Rectangle",
                "240 (12x20) - Rectangle",
                "300 (15x20) - Rectangle",
                "320 (16x20) - Rectangle",
            ],
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
        def add_slider(label_text, variable, from_, to_):
            ttk.Label(parameter_row, text=label_text, style="SidebarText.TLabel").pack(anchor="w", pady=(8, 0))
            tk.Scale(
                parameter_row,
                variable=variable,
                from_=from_,
                to=to_,
                orient="horizontal",
                bg=PANEL_BG,
                fg=TEXT_LIGHT,
                troughcolor="#1e293b",
                highlightthickness=0,
                activebackground=ACCENT,
                showvalue=True,
            ).pack(fill="x")

        add_slider("Ympyröiden määrä", circle_count_var, 5, 60)
        add_slider("Viivan paksuus", circle_thickness_var, 1, 25)
        add_slider("Ympyrän koko (säde)", circle_size_var, 20, 400)


def on_background_color_selected(*_args):
    selected = bg_color_var.get()
    if selected != "Custom...":
        bg_swatch.configure(bg=selected)
        return

    # askcolor returns ((r, g, b), "#rrggbb") or (None, None) if cancelled
    _rgb, hex_color = colorchooser.askcolor(title="Valitse taustaväri")
    if hex_color:
        if hex_color not in background_combo["values"]:
            background_combo["values"] = list(background_combo["values"]) + [hex_color]
        bg_color_var.set(hex_color)
        bg_swatch.configure(bg=hex_color)
    else:
        # user cancelled the picker — fall back to the previous color
        bg_color_var.set(bg_swatch["bg"])


# Holds the RasterRecorder for whatever was drawn most recently, so it can be
# exported without ever touching the turtle window's pixels (see export_art).
current_recorder = {"recorder": None}


def export_art(output_dir: Path | None = None, base_name: str | None = None):
    """Export the most recently drawn art as PNG and PDF.

    If output_dir and base_name are provided, use them; otherwise use the default output folder
    and a timestamped filename.
    Returns a list of the file paths that were successfully written.
    """
    recorder = current_recorder["recorder"]
    if recorder is None:
        raise RuntimeError("Ei piirrettyä taidetta tallennettavaksi.")

    if output_dir is None:
        output_dir = get_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    if base_name is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base_name = f"{art_var.get().lower().replace(' ', '_')}-{timestamp}"

    saved_paths = []

    png_path = output_dir / f"{base_name}.png"
    recorder.save_png(png_path)
    saved_paths.append(png_path)

    pdf_path = output_dir / f"{base_name}.pdf"
    recorder.save_pdf(pdf_path)
    saved_paths.append(pdf_path)

    return saved_paths


# Animation pacing: every art type now draws step-by-step instead of all at
# once, so the user can actually watch it happen and stop it whenever the
# result looks good. ANIMATION_TARGET_MS is the rough total duration we aim
# for; the per-step delay is derived from how many steps that art job has.
ANIMATION_TARGET_MS = 30000
MIN_STEP_DELAY_MS = 15
MAX_STEP_DELAY_MS = 400

active_job = {"running": False, "stop": False, "after_id": None}


def set_drawing_state(is_drawing):
    state = "disabled" if is_drawing else "normal"
    create_button.configure(state=state)
    choose_button.configure(state=state)
    stop_button.configure(state=("normal" if is_drawing else "disabled"))


def stop_art():
    """Stop the current animation early and keep whatever has been drawn."""
    active_job["stop"] = True


def run_animated(generator, total_steps, on_finish):
    delay_ms = MIN_STEP_DELAY_MS
    if total_steps > 0:
        delay_ms = max(MIN_STEP_DELAY_MS, min(MAX_STEP_DELAY_MS, ANIMATION_TARGET_MS // total_steps))

    active_job["running"] = True
    active_job["stop"] = False

    progress = {"done": 0}

    def step():
        if active_job["stop"]:
            finish()
            return
        try:
            next(generator)
        except StopIteration:
            finish()
            return
        progress["done"] += 1
        if total_steps > 0:
            percent = min(100, int(progress["done"] * 100 / total_steps))
            status_var.set(f"Piirretään... {percent}%  (paina Pysäytä lopettaaksesi heti)")
        active_job["after_id"] = window.after(delay_ms, step)

    def finish():
        active_job["running"] = False
        active_job["after_id"] = None
        on_finish()

    step()


def create_art():
    if not filepath or not rgb_colors:
        messagebox.showerror("Virhe", "Valitse ensin kuva, jotta värit saadaan poimittua.")
        return

    if active_job["running"]:
        return

    turtle_screen, canvas_width, canvas_height = create_turtle_surface()
    status_var.set("Piirretään uutta versiota...")
    window.update_idletasks()

    recorder = RasterRecorder(canvas_width, canvas_height, bg=bg_color_var.get())
    current_recorder["recorder"] = recorder

    selected_art = art_var.get()
    try:
        if selected_art == "Dot Art":
            dot_count, cols, rows = get_dot_grid(dot_var.get())
            maker = DotArtMaker(turtle_screen, canvas_width, canvas_height, rgb_colors, dot_count)
            maker.grid_cols, maker.grid_rows = cols, rows
            generator = maker.draw_steps(recorder=recorder)
            total_steps = maker.total_dots()
        elif selected_art == "Random Walk Art":
            size_config = size_mapping[size_var.get()]
            walker = RandomWalkArt(
                turtle_screen,
                canvas_width,
                canvas_height,
                turtle_count=size_config["turtles"],
            )
            generator = walker.draw_steps(size_config["steps"], rgb_colors, recorder=recorder)
            total_steps = size_config["steps"]
        else:
            circle_count = circle_count_var.get()
            thickness = circle_thickness_var.get()
            radius = circle_size_var.get()
            circle_art = CircleArt(turtle_screen, canvas_width, canvas_height)
            generator = circle_art.draw_steps(rgb_colors, circle_count, thickness, radius, recorder=recorder)
            total_steps = circle_art.total_strokes(circle_count)
    except Exception as exc:
        status_var.set("Piirtäminen epäonnistui.")
        messagebox.showerror("Virhe", f"Piirtäminen epäonnistui:\n{exc}")
        return

    set_drawing_state(True)

    def on_finish():
        set_drawing_state(False)
        status_var.set(f"{selected_art} valmis.")
        if autosave_var.get():
            save_current_art()

    run_animated(generator, total_steps, on_finish)


def save_current_art():
    if current_recorder["recorder"] is None:
        messagebox.showerror("Virhe", "Ei piirrettyä taidetta tallennettavaksi. Paina ensin 'Luo Art'.")
        return

    # Default file name
    default_name = f"{art_var.get().lower().replace(' ', '_')}.png"
    save_path = filedialog.asksaveasfilename(
        title="Tallenna kuva nimellä...",
        defaultextension=".png",
        initialfile=default_name,
        filetypes=[("PNG-kuva", "*.png"), ("PDF-asiakirja", "*.pdf")],
    )
    if not save_path:
        return

    chosen = Path(save_path)
    output_dir = chosen.parent
    base_name = chosen.stem

    try:
        saved_paths = export_art(output_dir=output_dir, base_name=base_name)
    except Exception as exc:
        messagebox.showerror("Virhe", f"Tallennus epäonnistui:\n{exc}")
        return

    saved_files = [str(p) for p in saved_paths if p and p.exists()]

    if saved_files:
        status_var.set(f"Tallennettu: {', '.join(saved_files)}")
    else:
        status_var.set("Tallennus epäonnistui.")
        messagebox.showerror("Virhe", "Kuvan tallennus epäonnistui.")
        return

    # Open the containing folder in Finder (macOS) so user sees the saved files
    try:
        subprocess.run(["open", str(output_dir)])
    except Exception:
        pass

def quit_app():
    window.destroy()


layout = tk.Frame(window, bg=APP_BG)
layout.pack(fill="both", expand=True, padx=24, pady=24)

sidebar = ttk.Frame(layout, style="Sidebar.TFrame", padding=24)
sidebar.pack(side="left", fill="y")

ttk.Label(sidebar, text="Art Maker", style="SidebarTitle.TLabel").pack(anchor="w")
ttk.Label(
    sidebar,
    text="Vanha turtle-projekti uudella studiologikalla: vakaampi piirto, satunnaisempi random walk ja automaattinen export.",
    style="SidebarText.TLabel",
    wraplength=300,
).pack(anchor="w", pady=(6, 20))

choose_button = ttk.Button(sidebar, text="Valitse kuva", command=choose_image, style="Art.TButton")
choose_button.pack(fill="x")
ttk.Label(sidebar, textvariable=image_var, style="SidebarText.TLabel", wraplength=300).pack(anchor="w", pady=(10, 16))

preview_shell = tk.Frame(sidebar, bg="#1e293b", bd=0, highlightthickness=0, height=PREVIEW_MAX_HEIGHT + 24)
preview_shell.pack(fill="x", pady=(0, 18))
# Lock the frame's height so a tall/portrait photo can't grow the sidebar and
# push the buttons below it off-screen — the thumbnail is letterboxed to fit.
preview_shell.pack_propagate(False)
preview_label = tk.Label(
    preview_shell,
    text="Kuvan esikatselu",
    bg="#1e293b",
    fg="#cbd5e1",
    font=("Avenir Next", 11, "bold"),
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

ttk.Label(sidebar, text="Taustaväri", style="SidebarText.TLabel").pack(anchor="w")
background_row = ttk.Frame(sidebar, style="Sidebar.TFrame")
background_row.pack(fill="x", pady=(6, 18))
background_combo = ttk.Combobox(
    background_row,
    textvariable=bg_color_var,
    values=BACKGROUND_COLOR_CHOICES,
    state="readonly",
    style="Studio.TCombobox",
)
background_combo.pack(side="left", fill="x", expand=True)
bg_swatch = tk.Label(background_row, bg=bg_color_var.get(), width=3, relief="solid", bd=1)
bg_swatch.pack(side="left", padx=(8, 0))
bg_color_var.trace_add("write", on_background_color_selected)

parameter_row = ttk.Frame(sidebar, style="Sidebar.TFrame")
parameter_row.pack(fill="x", pady=(0, 18))

ttk.Checkbutton(
    sidebar,
    text="Kysy tallennus ennen tallennusta",
    variable=autosave_var,
    style="Studio.TCheckbutton",
).pack(anchor="w", pady=(0, 18))

button_row = ttk.Frame(sidebar, style="Sidebar.TFrame")
button_row.pack(fill="x")
create_button = ttk.Button(button_row, text="Luo Art", command=create_art, style="Art.TButton")
create_button.pack(fill="x")
stop_button = ttk.Button(button_row, text="Pysäytä ja näytä tulos", command=stop_art, style="Secondary.TButton", state="disabled")
stop_button.pack(fill="x", pady=(10, 0))
ttk.Button(button_row, text="Tallenna kuva", command=save_current_art, style="Secondary.TButton").pack(fill="x", pady=(10, 0))
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

update_parameter_controls()
art_var.trace_add("write", update_parameter_controls)

window.mainloop()
