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
