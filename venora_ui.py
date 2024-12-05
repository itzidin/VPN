import customtkinter as ctk
import tkinter as tk
from math import pi
import sys

class CircularButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            width=70,
            height=70,
            corner_radius=35,
            text="⏽",
            font=("Helvetica", 24),
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white"
        )

class CircleCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            width=240,
            height=240,
            bg='white',
            highlightthickness=0
        )
        # Create concentric circles
        colors = ['#4CAF5019', '#4CAF5026', '#4CAF5033']
        sizes = [240, 180, 120]
        for size, color in zip(sizes, colors):
            x0 = (240 - size) // 2
            y0 = (240 - size) // 2
            x1 = x0 + size
            y1 = y0 + size
            self.create_oval(x0, y0, x1, y1, fill=color, outline='')

class VenoraGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Venora")
        self.root.geometry("400x500")
        self.root.configure(fg_color="white")

        # Header
        header_frame = ctk.CTkFrame(self.root, fg_color="white", height=40)
        header_frame.pack(fill="x", padx=20, pady=(10, 0))

        # Logo
        logo_label = ctk.CTkLabel(
            header_frame,
            text="Venora",
            font=("Helvetica", 20),
            text_color="black"
        )
        logo_label.pack(side="left")

        # Control buttons
        controls_frame = ctk.CTkFrame(header_frame, fg_color="white")
        controls_frame.pack(side="right")

        minimize_btn = ctk.CTkButton(
            controls_frame,
            text="−",
            width=30,
            height=30,
            fg_color="transparent",
            text_color="black",
            hover_color="#f0f0f0",
            command=self.root.iconify
        )
        minimize_btn.pack(side="left", padx=5)

        close_btn = ctk.CTkButton(
            controls_frame,
            text="×",
            width=30,
            height=30,
            fg_color="transparent",
            text_color="black",
            hover_color="#f0f0f0",
            command=self.root.quit
        )
        close_btn.pack(side="left", padx=5)

        # Main content frame with proper spacing
        content_frame = ctk.CTkFrame(self.root, fg_color="white")
        content_frame.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        # Center the connection indicator
        connection_frame = ctk.CTkFrame(content_frame, fg_color="white")
        connection_frame.pack(expand=True, pady=(20, 40))

        # Circles canvas with improved positioning
        self.circles_canvas = CircleCanvas(connection_frame)
        self.circles_canvas.pack()

        # Power button centered over circles
        self.power_button = CircularButton(
            connection_frame,
            command=self.toggle_connection
        )
        self.power_button.place(relx=0.5, rely=0.5, anchor="center")

        # Status text
        self.status_label = ctk.CTkLabel(
            content_frame,
            text="Connected To",
            font=("Helvetica", 16),
            text_color="black"
        )
        self.status_label.pack(pady=(60, 5))

        self.location_label = ctk.CTkLabel(
            content_frame,
            text="Smart Location",
            font=("Helvetica", 22, "bold"),
            text_color="black"
        )
        self.location_label.pack()

        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Make window borderless
        self.root.overrideredirect(True)
        self._make_draggable(header_frame)

    def toggle_connection(self):
        # Placeholder for connection toggle
        pass

    def _make_draggable(self, widget):
        widget.bind("<Button-1>", self.start_move)
        widget.bind("<ButtonRelease-1>", self.stop_move)
        widget.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        try:
            # Center window on screen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - 400) // 2
            y = (screen_height - 500) // 2
            self.root.geometry(f"400x500+{x}+{y}")

            # Set window attributes
            self.root.attributes('-topmost', True)
            self.root.update()
            self.root.attributes('-topmost', False)

            self.root.mainloop()
        except tk.TclError as e:
            print("Warning: GUI cannot be displayed in headless environment")
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    app = VenoraGUI()
    app.run()
