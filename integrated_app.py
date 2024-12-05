import customtkinter as ctk
import tkinter as tk
from math import pi
import subprocess
import os
import platform
import json
import tempfile
import shutil
import sys
import time

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
        # Create concentric circles with RGB colors
        colors = ['#E8F5E9', '#C8E6C9', '#A5D6A7']  # Light green colors with increasing intensity
        sizes = [240, 180, 120]
        for size, color in zip(sizes, colors):
            x0 = (240 - size) // 2
            y0 = (240 - size) // 2
            x1 = x0 + size
            y1 = y0 + size
            self.create_oval(x0, y0, x1, y1, fill=color, outline='')

class VenoraVPN:
    def __init__(self):
        self.root = ctk.CTk()
        self.v2ray_process = None
        self.proxy_enabled = False
        self.temp_dir = None

        # UI Setup
        self.setup_ui()

        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

    def setup_ui(self):
        self.root.title("Venora")
        self.root.geometry("400x500")
        self.root.configure(fg_color="white")
        self.root.overrideredirect(True)

        # Header
        header_frame = ctk.CTkFrame(self.root, fg_color="white", height=40)
        header_frame.pack(fill="x", padx=20, pady=(10, 0))
        self._make_draggable(header_frame)

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
            command=self.on_close
        )
        close_btn.pack(side="left", padx=5)

        # Main content
        content_frame = ctk.CTkFrame(self.root, fg_color="white")
        content_frame.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        # Center the connection indicator
        connection_frame = ctk.CTkFrame(content_frame, fg_color="white")
        connection_frame.pack(expand=True, pady=(20, 40))

        # Circles canvas
        self.circles_canvas = CircleCanvas(connection_frame)
        self.circles_canvas.pack()

        # Power button
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
        self.status_label.pack(pady=(0, 5))

        self.location_label = ctk.CTkLabel(
            content_frame,
            text="Smart Location",
            font=("Helvetica", 22, "bold"),
            text_color="black"
        )
        self.location_label.pack()

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

    def extract_v2ray_executable(self):
        if getattr(sys, 'frozen', False):
            self.temp_dir = tempfile.mkdtemp()
            v2ray_path = os.path.join(self.temp_dir, "v2ray.exe")
            geoip_path = os.path.join(self.temp_dir, "geoip.dat")
            geosite_path = os.path.join(self.temp_dir, "geosite.dat")
            try:
                shutil.copyfile(os.path.join(sys._MEIPASS, "v2ray.exe"), v2ray_path)
                shutil.copyfile(os.path.join(sys._MEIPASS, "geoip.dat"), geoip_path)
                shutil.copyfile(os.path.join(sys._MEIPASS, "geosite.dat"), geosite_path)
                return v2ray_path
            except Exception as e:
                self.show_error(f"Failed to extract V2Ray executable: {e}")
                return None
        else:
            self.show_error("This application is not running as a bundled executable.")
            return None

    def generate_v2ray_config(self):
        config = {
            "log": {"access": "", "error": "", "loglevel": "warning"},
            "inbounds": [
                {
                    "tag": "socks",
                    "port": 10808,
                    "listen": "127.0.0.1",
                    "protocol": "socks",
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"],
                        "routeOnly": False
                    },
                    "settings": {
                        "auth": "noauth",
                        "udp": True,
                        "allowTransparent": False
                    }
                },
                {
                    "tag": "http",
                    "port": 10809,
                    "listen": "127.0.0.1",
                    "protocol": "http",
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"],
                        "routeOnly": False
                    },
                    "settings": {
                        "auth": "noauth",
                        "udp": True,
                        "allowTransparent": False
                    }
                }
            ],
            "outbounds": [
                {
                    "tag": "proxy",
                    "protocol": "vless",
                    "settings": {
                        "vnext": [{
                            "address": "sv0.roadenterprise.top",
                            "port": 46241,
                            "users": [{
                                "id": "723ab112-ab0f-4506-9968-717bfd67c8f1",
                                "alterId": 0,
                                "email": "t@t.tt",
                                "security": "auto",
                                "encryption": "none"
                            }]
                        }]
                    },
                    "streamSettings": {
                        "network": "ws",
                        "wsSettings": {
                            "path": "/",
                            "headers": {}
                        }
                    },
                    "mux": {
                        "enabled": False,
                        "concurrency": -1
                    }
                },
                {
                    "tag": "direct",
                    "protocol": "freedom",
                    "settings": {}
                },
                {
                    "tag": "block",
                    "protocol": "blackhole",
                    "settings": {
                        "response": {
                            "type": "http"
                        }
                    }
                }
            ],
            "routing": {
                "domainStrategy": "AsIs",
                "rules": [
                    {
                        "type": "field",
                        "inboundTag": ["api"],
                        "outboundTag": "api"
                    },
                    {
                        "type": "field",
                        "outboundTag": "direct",
                        "domain": [
                            "domain:example-example.com",
                            "domain:example-example2.com"
                        ]
                    },
                    {
                        "type": "field",
                        "outboundTag": "block",
                        "domain": ["geosite:category-ads-all"]
                    },
                    {
                        "type": "field",
                        "outboundTag": "direct",
                        "domain": ["geosite:cn"]
                    },
                    {
                        "type": "field",
                        "outboundTag": "direct",
                        "ip": ["geoip:private", "geoip:cn"]
                    }
                ]
            }
        }
        return json.dumps(config)

    def set_system_proxy(self, enable=True):
        proxy_socks = "127.0.0.1:10808"
        proxy_http = "127.0.0.1:10809"
        os_type = platform.system()

        try:
            if enable:
                if os_type == "Windows":
                    os.system(f'REG ADD "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f')
                    os.system(f'REG ADD "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /t REG_SZ /d "socks={proxy_socks};http={proxy_http}" /f')
                    os.system(f'REG ADD "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyOverride /t REG_SZ /d "<-loopback>" /f')
                elif os_type in ["Linux", "Darwin"]:
                    os.environ["http_proxy"] = f"http://{proxy_http}"
                    os.environ["https_proxy"] = f"http://{proxy_http}"
                    os.environ["ALL_PROXY"] = f"socks5://{proxy_socks}"
                else:
                    self.show_error("Unsupported OS for setting proxy.")
            else:
                if os_type == "Windows":
                    os.system('REG ADD "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f')
                elif os_type in ["Linux", "Darwin"]:
                    os.environ.pop("http_proxy", None)
                    os.environ.pop("https_proxy", None)
                    os.environ.pop("ALL_PROXY", None)
        except Exception as e:
            self.show_error(f"Error setting system proxy: {e}")

    def start_v2ray(self):
        config = self.generate_v2ray_config()
        v2ray_executable = self.extract_v2ray_executable()

        if v2ray_executable is None:
            return None

        try:
            process = subprocess.Popen(
                [v2ray_executable, "-config", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            process.stdin.write(config.encode('utf-8'))
            process.stdin.close()
            return process
        except Exception as e:
            self.show_error(f"Failed to start V2Ray: {e}")
            return None

    def toggle_connection(self):
        if self.v2ray_process is None:
            self.connect()
        else:
            self.disconnect()

    def connect(self):
        self.v2ray_process = self.start_v2ray()
        if self.v2ray_process is None:
            return

        self.set_system_proxy(enable=True)
        self.proxy_enabled = True
        self.power_button.configure(fg_color="#2e8b57")
        self.status_label.configure(text="Connected To")
        self.display_ping()

    def disconnect(self):
        if self.v2ray_process:
            self.v2ray_process.terminate()
            self.v2ray_process = None

        self.set_system_proxy(enable=False)
        self.proxy_enabled = False
        self.power_button.configure(fg_color="#4CAF50")
        self.status_label.configure(text="Disconnected")
        self.location_label.configure(text="Smart Location")

    def display_ping(self):
        address = "sv0.roadenterprise.top"
        try:
            start_time = time.time()
            response = subprocess.run(
                ["ping", "-n" if platform.system() == "Windows" else "-c", "1", address],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            end_time = time.time()

            if ("TTL" in response.stdout) or ("ttl" in response.stdout.lower()):
                ping_time = int((end_time - start_time) * 1000)
                self.location_label.configure(text=f"Smart Location ({ping_time}ms)")
            else:
                self.location_label.configure(text="Smart Location (timeout)")
        except Exception as e:
            self.show_error(f"Error checking connection: {e}")
            self.location_label.configure(text="Smart Location (error)")

    def show_error(self, message):
        if hasattr(self, 'root'):
            tk.messagebox.showerror("Error", message)
        else:
            print(f"Error: {message}", file=sys.stderr)

    def on_close(self):
        if self.v2ray_process:
            self.disconnect()
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)
        self.root.quit()

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
    app = VenoraVPN()
    app.run()
