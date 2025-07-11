# Simple WMS Server and Client

This project provides a basic implementation of a Web Map Service (WMS) server using Flask and a corresponding desktop client built with Tkinter. The server can serve raster layers from local files, and the client allows users to request and display maps from the server.

---

## Features

### 🛰️ WMS Server (`geoserver.py`)
- Serves raster image layers (PNG, JPG, GIF, TIF) with associated TFW (world file) for georeferencing.
- Supports `GetCapabilities` request to list available layers and their bounding boxes.
- Supports `GetMap` request to generate and return map images based on specified layers, bounding box, dimensions, and format.
- Merges multiple requested layers into a single output image.

### 🖥️ WMS Client (`client.py`)
- Tkinter-based graphical user interface.
- Connects to a specified WMS server URL.
- Fetches and displays available layers from the server's `GetCapabilities` response.
- Allows users to:
  - Select multiple layers
  - Define a bounding box
  - Set image dimensions
  - Choose an output format (PNG, JPEG, GIF)
- Displays the generated map image with scrollbars for navigation.
- Shows the generated WMS request URL and status messages.

---

## Getting Started

### Prerequisites
- Python 3.x
- Required Python packages:
  ```bash
  pip install Flask Pillow requests numpy
  ```

### Project Structure
```
.
├── geoserver.py          # The WMS server application
├── client.py             # The WMS desktop client application
└── layers/               # Directory for your georeferenced raster layers
    ├── layer1.png
    ├── layer1.tfw
    ├── layer2.tif
    ├── layer2.tfw
    └── ...
```

---

## Setup and Running

### 1. Prepare Your Layers
Create a `layers/` directory in the same location as `geoserver.py`. Place your georeferenced raster images and their `.tfw` (world file) counterparts inside this directory.

**Example:**
```
layers/
├── my_map_area.png
└── my_map_area.tfw
```

A `.tfw` file contains georeferencing information. For example:
```
10.0
0.0
0.0
-10.0
100000.0
500000.0
```

### 2. Run the WMS Server
In a terminal:
```bash
python geoserver.py
```
The server starts on `http://localhost:5000` by default.

### 3. Run the WMS Client
In another terminal:
```bash
python client.py
```
A Tkinter GUI will open.

---

## Usage

- **Server URL:** Ensure the client’s "URL strežnika" is set to:  
  `http://localhost:5000/wms`
- **Load Layers:** Click "Naloži sloje" to fetch available layers.
- **Select Layers:** Use the checkboxes to choose which layers to request.
- **Set BBOX:** Enter the bounding box (min X, min Y, max X, max Y).
- **Image Format & Size:** Choose output format (PNG, JPEG, GIF) and image size.
- **Display Map:** Click "Prikaži" to fetch and display the map image.

---

## Configuration

### `geoserver.py`
Modify the `CONFIG` dictionary to set server settings:
```python
CONFIG = {
    "port": 5000,
    "layers_dir": "./layers",
    "default_srs": "XXX"  # Replace with actual SRS, e.g., "EPSG:4326"
}
```

> **Note:** The default SRS is currently a placeholder (`"XXX"`). Proper SRS handling and coordinate transformations should be implemented for a more robust solution.

---

## Limitations

- **Basic WMS Implementation:** Lacks full WMS standard support (e.g., no SLD, no OGC compliance).
- **SRS Handling:** Rudimentary; assumes consistent coordinate system across layers.
- **Error Handling:** Basic; can be expanded.
- **Performance:** In-memory image merging may slow down with large data.
- **Security:** No authentication or validation is implemented.
