#!/bin/bash

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -f "$HOME/nova_env/bin/activate" ]; then
    source "$HOME/nova_env/bin/activate"
fi

# Create desktop icon directory if it doesn't exist
mkdir -p ~/.local/share/applications/
mkdir -p ~/.local/share/icons/

# Create a desktop entry file
cat > ~/.local/share/applications/academic_scraper.desktop << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=Academic RAG Scraper
Comment=Scrape and index academic and technical content
Exec=bash -c 'source $HOME/nova_env/bin/activate && cd $HOME/Nova && python3 -m src.gui.scraper_gui'
Icon=$HOME/.local/share/icons/nova_scraper.png
Terminal=false
Categories=Education;Science;Development;
EOL

# Copy icon if it exists, or create a default one
if [ -f "../assets/nova_icon.png" ]; then
    cp "../assets/nova_icon.png" ~/.local/share/icons/nova_scraper.png
else
    # Create a simple text file as icon if ImageMagick is not available
    echo "Nova Scraper" > ~/.local/share/icons/nova_scraper.png
fi

# Make the desktop entry executable
chmod +x ~/.local/share/applications/academic_scraper.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications/

echo "Academic RAG Scraper installed successfully!"
echo "You can find it in your applications menu or run it from the terminal with:"
echo "source ~/nova_env/bin/activate && cd ~/Nova && python3 -m src.gui.scraper_gui"