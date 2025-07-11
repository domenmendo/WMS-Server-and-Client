Simple WMS Server and Client

This project provides a basic implementation of a Web Map Service (WMS) server using Flask and a corresponding desktop client built with Tkinter. The server can serve raster layers from local files, and the client allows users to request and display maps from the server.
Features
WMS Server (geoserver.py)

    Serves raster image layers (PNG, JPG, GIF, TIF) with associated TFW (world file) for georeferencing.

    Supports GetCapabilities request to list available layers and their bounding boxes.

    Supports GetMap request to generate and return map images based on specified layers, bounding box, dimensions, and format.

    Merges multiple requested layers into a single output image.

WMS Client (client.py)

    Tkinter-based graphical user interface.

    Connects to a specified WMS server URL.

    Fetches and displays available layers from the server's GetCapabilities response.

    Allows users to select multiple layers, define a bounding box, set image dimensions, and choose an output format (PNG, JPEG, GIF).

    Displays the generated map image with scrollbars for navigation.

    Shows the generated WMS request URL and status messages.

Getting Started
Prerequisites

    Python 3.x

    Flask

    Pillow (PIL)

    requests

    numpy (used by Pillow internally for some operations, good to have)

You can install the required Python packages using pip:

pip install Flask Pillow requests numpy

Project Structure

.
├── geoserver.py
├── client.py
└── layers/
    ├── layer1.png
    ├── layer1.tfw
    ├── layer2.tif
    ├── layer2.tfw
    └── ...

    geoserver.py: The WMS server application.

    client.py: The WMS desktop client application.

    layers/: A directory where your raster image files (e.g., .png, .jpg, .tif) and their corresponding world files (.tfw) should be placed. Each image-TFW pair represents a single WMS layer.

Setup and Running
1. Prepare Your Layers

Create a layers directory in the same location as geoserver.py. Place your georeferenced raster images and their .tfw (world file) counterparts inside this directory.

Example:

layers/
├── my_map_area.png
└── my_map_area.tfw

A .tfw file contains georeferencing information. For example:

10.0
0.0
0.0
-10.0
100000.0
500000.0

(This example is illustrative; actual values depend on your image and coordinate system.)
2. Run the WMS Server

Open a terminal or command prompt, navigate to the project directory, and run the server:

python geoserver.py

The server will start on http://localhost:5000 by default. You should see log messages indicating which layers are loaded.
3. Run the WMS Client

Open another terminal or command prompt, navigate to the project directory, and run the client:

python client.py

The Tkinter GUI application will open.
Usage

    Server URL: Ensure the "URL strežnika" (Server URL) in the client is set to http://localhost:5000/wms (or wherever your server is running).

    Load Layers: Click the "Naloži sloje" (Load Layers) button. The client will send a GetCapabilities request to the server and populate the "Razpoložljivi sloji" (Available Layers) list with checkboxes.

    Select Layers: Check the boxes next to the layers you want to display.

    Set BBOX: Enter the minimum X, minimum Y, maximum X, and maximum Y coordinates for your desired map area in the "BBOX" fields.

    Image Format & Size: Choose the desired image format (PNG, JPEG, GIF) and specify the output width and height for the map image.

    Display Map: Click the "Prikaži" (Display) button. The client will send a GetMap request to the server, and the resulting map image will be displayed in the right panel. The generated URL will also be shown.

Configuration
Server (geoserver.py)

You can modify the CONFIG dictionary in geoserver.py to change the server port, layers directory, or default SRS (Spatial Reference System).

CONFIG = {
    "port": 5000,
    "layers_dir": "./layers",
    "default_srs": "XXX" # Placeholder, consider setting a real SRS like "EPSG:4326"
}

Note: The default_srs is currently a placeholder ("XXX"). For a more robust WMS, you would need to implement proper SRS handling and coordinate transformations.
Limitations

    Basic WMS Implementation: This is a simplified WMS server and client. It does not support all WMS operations or advanced features like SLD (Styled Layer Descriptor), complex coordinate transformations, or OGC compliance.

    SRS Handling: The SRS handling is rudimentary. The client currently assumes 'XXX' as the SRS, and the server does not perform true coordinate system transformations based on SRS. Layers are expected to be in a consistent coordinate system.

    Error Handling: While some error handling is present, it can be expanded for production use.

    Performance: For large images or many layers, performance might be limited due to in-memory image processing.

    Security: No security measures are implemented.

Contributing

Feel free to fork this repository, open issues, or submit pull requests to improve the project.
License

[Specify your license here, e.g., MIT, Apache 2.0, etc.]
