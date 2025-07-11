import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import io
import json

class GeoServerClient:
    def __init__(self, root):
        self.root = root
        self.root.title("GeoServer Client")
        self.root.geometry("1000x800")
        
        self.server_url = "http://localhost:5000/wms"
        self.layers = []
        self.selected_layers = []
        
        self.setup_ui()
        self.load_capabilities()

    def setup_ui(self):
        # Glavni okvir
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Levi panel - kontrole
        control_frame = ttk.LabelFrame(main_frame, text="Kontrole", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # URL strežnika
        ttk.Label(control_frame, text="URL strežnika:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.url_entry = ttk.Entry(control_frame, width=30)
        self.url_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        self.url_entry.insert(0, self.server_url)
        
        ttk.Button(control_frame, text="Naloži sloje", command=self.load_capabilities).grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Seznam slojev
        ttk.Label(control_frame, text="Razpoložljivi sloji:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.layers_frame = ttk.Frame(control_frame)
        self.layers_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # BBOX
        ttk.Label(control_frame, text="BBOX:").grid(row=4, column=0, sticky=tk.W)
        
        bbox_frame = ttk.Frame(control_frame)
        bbox_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Label(bbox_frame, text="min X:").grid(row=0, column=0, sticky=tk.W)
        self.min_x_entry = ttk.Entry(bbox_frame, width=10)
        self.min_x_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        
        ttk.Label(bbox_frame, text="min Y:").grid(row=0, column=2, sticky=tk.W)
        self.min_y_entry = ttk.Entry(bbox_frame, width=10)
        self.min_y_entry.grid(row=0, column=3, sticky=tk.W)
        
        ttk.Label(bbox_frame, text="max X:").grid(row=1, column=0, sticky=tk.W)
        self.max_x_entry = ttk.Entry(bbox_frame, width=10)
        self.max_x_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 5))
        
        ttk.Label(bbox_frame, text="max Y:").grid(row=1, column=2, sticky=tk.W)
        self.max_y_entry = ttk.Entry(bbox_frame, width=10)
        self.max_y_entry.grid(row=1, column=3, sticky=tk.W)
        
        # Format slike
        ttk.Label(control_frame, text="Format slike:").grid(row=6, column=0, sticky=tk.W)
        
        self.format_var = tk.StringVar(value="image/png")
        format_frame = ttk.Frame(control_frame)
        format_frame.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(format_frame, text="PNG", variable=self.format_var, value="image/png").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.format_var, value="image/jpeg").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(format_frame, text="GIF", variable=self.format_var, value="image/gif").grid(row=0, column=2, sticky=tk.W)
        
        # Velikost slike
        ttk.Label(control_frame, text="Velikost slike:").grid(row=8, column=0, sticky=tk.W)
        
        size_frame = ttk.Frame(control_frame)
        size_frame.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(size_frame, text="Širina:").grid(row=0, column=0, sticky=tk.W)
        self.width_entry = ttk.Entry(size_frame, width=6)
        self.width_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        self.width_entry.insert(0, "800")
        
        ttk.Label(size_frame, text="Višina:").grid(row=0, column=2, sticky=tk.W)
        self.height_entry = ttk.Entry(size_frame, width=6)
        self.height_entry.grid(row=0, column=3, sticky=tk.W)
        self.height_entry.insert(0, "600")
        
        # Gumb za prikaz
        ttk.Button(control_frame, text="Prikaži", command=self.get_map).grid(row=10, column=0, columnspan=2, pady=10)
        
        # Informacije o URL-ju
        ttk.Label(control_frame, text="Generirani URL:").grid(row=11, column=0, sticky=tk.W, pady=(20, 5))
        self.url_info = ttk.Entry(control_frame, width=30)
        self.url_info.grid(row=12, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 10))
        
        # Desni panel - prikaz slike
        self.image_frame = ttk.LabelFrame(main_frame, text="Slika", padding="10")
        self.image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.image_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars za sliko
        self.h_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.v_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        # Statusna vrstica
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Pripravljen")

    def load_capabilities(self):
        """Naloži informacije o razpoložljivih slojih"""
        self.server_url = self.url_entry.get()
        
        try:
            self.status_var.set("Nalagam sloje...")
            self.root.update()
            
            # Pošlji GetCapabilities zahtevek
            response = requests.get(f"{self.server_url}?REQUEST=GetCapabilities")
            
            if response.status_code != 200:
                messagebox.showerror("Napaka", f"Strežnik vrnil napako: {response.status_code}")
                self.status_var.set("Napaka pri nalaganju slojev")
                return
                
            capabilities = response.json()
            self.layers = capabilities.get("layers", [])
            
            # Počisti obstoječe checkboxe
            for widget in self.layers_frame.winfo_children():
                widget.destroy()
                
            # Ustvari nove checkboxe za sloje
            self.layer_vars = {}
            for i, layer in enumerate(self.layers):
                layer_name = layer.get("name", f"Layer {i}")
                var = tk.BooleanVar(value=False)
                self.layer_vars[layer_name] = var
                
                ttk.Checkbutton(self.layers_frame, text=layer_name, variable=var).grid(row=i, column=0, sticky=tk.W)
            
            # Nastavi privzeti BBOX iz prvega sloja, če obstaja
            if self.layers:
                bbox = self.layers[0].get("bbox", [0, 0, 0, 0])
                self.min_x_entry.delete(0, tk.END)
                self.min_x_entry.insert(0, str(bbox[0]))
                
                self.min_y_entry.delete(0, tk.END)
                self.min_y_entry.insert(0, str(bbox[1]))
                
                self.max_x_entry.delete(0, tk.END)
                self.max_x_entry.insert(0, str(bbox[2]))
                
                self.max_y_entry.delete(0, tk.END)
                self.max_y_entry.insert(0, str(bbox[3]))
            
            self.status_var.set(f"Naloženih {len(self.layers)} slojev")
        
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Napaka", f"Napaka pri povezavi s strežnikom: {str(e)}")
            self.status_var.set("Napaka pri povezavi s strežnikom")
        
        except json.JSONDecodeError:
            messagebox.showerror("Napaka", "Neveljaven odgovor strežnika")
            self.status_var.set("Neveljaven odgovor strežnika")
        
        except Exception as e:
            messagebox.showerror("Napaka", f"Napaka: {str(e)}")
            self.status_var.set("Napaka")

    def get_map(self):
        """Pridobi in prikaži sliko iz WMS strežnika"""
        try:
            # Preveri, če so izbrani sloji
            selected_layers = []
            for layer_name, var in self.layer_vars.items():
                if var.get():
                    selected_layers.append(layer_name)
            
            if not selected_layers:
                messagebox.showwarning("Opozorilo", "Izberi vsaj en sloj")
                return
                
            # Pridobi BBOX
            try:
                min_x = float(self.min_x_entry.get())
                min_y = float(self.min_y_entry.get())
                max_x = float(self.max_x_entry.get())
                max_y = float(self.max_y_entry.get())
            except ValueError:
                messagebox.showerror("Napaka", "BBOX mora vsebovati veljavne številke")
                return
                
            # Pridobi velikost slike
            try:
                width = int(self.width_entry.get())
                height = int(self.height_entry.get())
                if width <= 0 or height <= 0:
                    raise ValueError("Dimenzije morajo biti pozitivne")
            except ValueError as e:
                messagebox.showerror("Napaka", f"Neveljavne dimenzije slike: {str(e)}")
                return
                
            # Sestavi parametre zahtevka
            params = {
                'REQUEST': 'GetMap',
                'LAYERS': ','.join(selected_layers),
                'BBOX': f"{min_x},{min_y},{max_x},{max_y}",
                'WIDTH': width,
                'HEIGHT': height,
                'FORMAT': self.format_var.get(),
                'SRS': 'XXX',  # privzeta vrednost
                'STYLES': ''
            }
            
            # Sestavi URL
            url = self.server_url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
            self.url_info.delete(0, tk.END)
            self.url_info.insert(0, url)
            
            # Pošlji zahtevek
            self.status_var.set("Pridobivam sliko...")
            self.root.update()
            
            response = requests.get(url, stream=True)
            
            if response.status_code != 200:
                messagebox.showerror("Napaka", f"Strežnik vrnil napako: {response.status_code}")
                self.status_var.set("Napaka pri pridobivanju slike")
                return
                
            # Prikaži sliko
            image_data = io.BytesIO(response.content)
            img = Image.open(image_data)
            self.img_tk = ImageTk.PhotoImage(img)
            
            # Počisti obstoječo sliko
            self.canvas.delete("all")
            
            # Nastavi velikost platna
            self.canvas.config(scrollregion=(0, 0, width, height))
            
            # Prikaži sliko
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)
            
            self.status_var.set(f"Slika prikazana: {width}x{height} ({self.format_var.get()})")
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Napaka", f"Napaka pri povezavi s strežnikom: {str(e)}")
            self.status_var.set("Napaka pri povezavi s strežnikom")
        
        except Exception as e:
            messagebox.showerror("Napaka", f"Napaka: {str(e)}")
            self.status_var.set("Napaka pri prikazu slike")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeoServerClient(root)
    root.mainloop()