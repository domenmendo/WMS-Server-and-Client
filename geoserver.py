from flask import Flask, request, send_file
import os
import io
from PIL import Image
import numpy as np
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Konfiguracija strežnika
CONFIG = {
    "port": 5000,
    "layers_dir": "./layers",
    "default_srs": "XXX"
}

# Razred za rastrski sloj
class RasterLayer:
    def __init__(self, name, image_path, tfw_path):
        self.name = name
        self.image_path = image_path
        self.tfw_path = tfw_path
        self.image = None
        self.tfw_data = None
        self.load_tfw()
        self.load_image()
        
    def load_tfw(self):
        with open(self.tfw_path, 'r') as f:
            lines = f.readlines()
            self.tfw_data = {
                'x_pixel_size': float(lines[0].strip()),
                'x_rotation': float(lines[1].strip()),
                'y_rotation': float(lines[2].strip()),
                'y_pixel_size': float(lines[3].strip()),  # Negativna vrednost
                'x_top_left': float(lines[4].strip()),
                'y_top_left': float(lines[5].strip())
            }
    
    def load_image(self):
        self.image = Image.open(self.image_path)
        self.width, self.height = self.image.size
    
    def get_bbox(self):
        """Vrne bounding box sloja"""
        x_min = self.tfw_data['x_top_left']
        y_max = self.tfw_data['y_top_left']
        x_max = x_min + self.width * self.tfw_data['x_pixel_size']
        y_min = y_max + self.height * self.tfw_data['y_pixel_size']  # y_pixel_size je negativen
        return [x_min, y_min, x_max, y_max]
    
    def clip_to_bbox(self, bbox, width, height):
        """Obreži sliko na podani bounding box in jo prilagodi na želeno velikost"""
        # Konverzija iz geografskih koordinat v koordinate slike
        requested_x_min, requested_y_min, requested_x_max, requested_y_max = bbox
        
        # Izračun koordinat v pikslih
        image_x_min = int((requested_x_min - self.tfw_data['x_top_left']) / self.tfw_data['x_pixel_size'])
        image_y_min = int((requested_y_max - self.tfw_data['y_top_left']) / self.tfw_data['y_pixel_size'])
        image_x_max = int((requested_x_max - self.tfw_data['x_top_left']) / self.tfw_data['x_pixel_size'])
        image_y_max = int((requested_y_min - self.tfw_data['y_top_left']) / self.tfw_data['y_pixel_size'])
        
        # Preveri, če je bbox izven slike
        if (image_x_max < 0 or image_y_max < 0 or 
            image_x_min >= self.width or image_y_min >= self.height):
            return None
        
        # Omeji koordinate na velikost slike
        image_x_min = max(0, image_x_min)
        image_y_min = max(0, image_y_min)
        image_x_max = min(self.width, image_x_max)
        image_y_max = min(self.height, image_y_max)
        
        # Obreži sliko
        cropped_image = self.image.crop((image_x_min, image_y_min, image_x_max, image_y_max))
        
        # Prilagodi velikost
        if width and height:
            resized_image = cropped_image.resize((width, height), Image.LANCZOS)
            return resized_image
        return cropped_image

# Nalaganje slojev
layers = {}

def load_layers():
    if not os.path.exists(CONFIG["layers_dir"]):
        os.makedirs(CONFIG["layers_dir"])
        logging.warning(f"Created layers directory: {CONFIG['layers_dir']}")
        return
    
    for filename in os.listdir(CONFIG["layers_dir"]):
        if filename.endswith(".tfw"):
            base_name = filename[:-4]
            layer_name = base_name
            tfw_path = os.path.join(CONFIG["layers_dir"], filename)
            
            # Poišči pripadajočo sliko
            image_path = None
            for ext in ['.tif', '.jpg', '.png', '.gif']:
                possible_path = os.path.join(CONFIG["layers_dir"], base_name + ext)
                if os.path.exists(possible_path):
                    image_path = possible_path
                    break
                    
            if image_path:
                layers[layer_name] = RasterLayer(layer_name, image_path, tfw_path)
                logging.info(f"Loaded layer: {layer_name}")
            else:
                logging.warning(f"No image file found for TFW: {filename}")

# WMS zahtevki
@app.route('/wms', methods=['GET'])
def wms():
    # Pridobi parametre zahtevka
    request_type = request.args.get('REQUEST', 'GetMap')
    
    if request_type == 'GetCapabilities':
        return get_capabilities()
    elif request_type == 'GetMap':
        return get_map(request.args)
    else:
        return "Napačna zahteva", 400

def get_capabilities():
    """Vrne informacije o razpoložljivih slojih"""
    capabilities = {
        "version": "1.1.1",
        "layers": []
    }
    
    for layer_name, layer in layers.items():
        bbox = layer.get_bbox()
        capabilities["layers"].append({
            "name": layer_name,
            "bbox": bbox,
            "width": layer.width,
            "height": layer.height
        })
    
    return json.dumps(capabilities)

def get_map(params):
    """Generira sliko na podlagi WMS zahtevka"""
    try:
        # Pridobi parametre
        width = int(params.get('WIDTH', 800))
        height = int(params.get('HEIGHT', 600))
        bbox_str = params.get('BBOX', '')
        layers_str = params.get('LAYERS', '')
        format_str = params.get('FORMAT', 'image/png')
        
        # Parsiranje BBOX
        if not bbox_str:
            return "Manjka BBOX parameter", 400
            
        bbox = [float(x) for x in bbox_str.split(',')]
        if len(bbox) != 4:
            return "Napačen format BBOX", 400
        
        # Parsiranje LAYERS
        if not layers_str:
            return "Manjka LAYERS parameter", 400
            
        requested_layers = layers_str.split(',')
        
        # Preveri, če vsi zahtevani sloji obstajajo
        for layer_name in requested_layers:
            if layer_name not in layers:
                return f"Sloj {layer_name} ne obstaja", 404
        
        # Pripravi prazno sliko
        result_image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        
        # Dodaj sloje od spodaj navzgor
        for layer_name in requested_layers:
            layer = layers[layer_name]
            clipped_image = layer.clip_to_bbox(bbox, width, height)
            
            if clipped_image:
                # Pretvori v RGBA, če ni že
                if clipped_image.mode != 'RGBA':
                    clipped_image = clipped_image.convert('RGBA')
                
                # Združi sliko z rezultatom
                result_image = Image.alpha_composite(result_image, clipped_image)
        
        # Pripravi format izhoda
        output_format = format_str.split('/')[-1].lower()
        
        # Pretvori v ustrezen format (PNG, JPG, GIF)
        if output_format == 'jpeg' or output_format == 'jpg':
            # JPEG ne podpira prosojnosti, zato pretvorimo v RGB
            result_image = result_image.convert('RGB')
            img_format = 'JPEG'
        elif output_format == 'gif':
            img_format = 'GIF'
        else:  # privzeto png
            img_format = 'PNG'
        
        # Shrani v pomnilnik in vrni
        img_io = io.BytesIO()
        result_image.save(img_io, format=img_format)
        img_io.seek(0)
        
        return send_file(img_io, mimetype=f'image/{output_format}')
    
    except Exception as e:
        logging.error(f"Error processing GetMap request: {str(e)}")
        return f"Napaka pri obdelavi zahteve: {str(e)}", 500

if __name__ == '__main__':
    load_layers()
    app.run(host='0.0.0.0', port=CONFIG["port"], debug=True)