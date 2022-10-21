.SILENT: build main

# Use the directory name (lowercase) as the image name
PROJECT_NAME=$(shell echo "$(shell basename $(PWD))" | tr '[:upper:]' '[:lower:]')

# Build the image
build:
	docker build -t $(PROJECT_NAME) .

# Open a bash terminal
bash:
	docker run --rm -it -v $(PWD):/workspace $(PROJECT_NAME) bash

# Run main script
shade:
	docker run --rm -v $(PWD):/workspace $(PROJECT_NAME) python3 src/hillshade.py

# Webmap generation
web:
	docker run --rm -v $(PWD):/workspace $(PROJECT_NAME) python3 src/web_map.py

# Make the hillshade first and then proceed to make the webmap WMTS folder
all: shade
	docker run --rm -v $(PWD):/workspace $(PROJECT_NAME) python3 src/web_map.py