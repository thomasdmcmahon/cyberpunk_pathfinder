# Cyberpunk Pathfinder

A real-world A* pathfinding visualizer with a cyberpunk-inspired aesthetic, built with Python, Pygame, NetworkX, and OSMnx.

The project visualizes how the A* algorithm explores city road networks step by step, with neon-lit trails, glowing nodes, and a dramatic reveal when the final path is found.

---

## Features

- Load real-world maps using [OSMnx](https://github.com/gboeing/osmnx)  
- Implemented A* pathfinding algorithm with step-by-step exploration  
- Cyberpunk-inspired visuals:  
  - Gradient backgrounds  
  - Neon glowing roads and trails  
  - Pulsing start/end nodes  
  - Fading exploration paths  
- Smooth exploration pacing with adjustable `STEPS_PER_FRAME`  
- Interactive: click to select start and goal nodes on the map  
- Final path visualization with pulsing neon glow  

---

## Current Look

- Dark gradient background  
- Faint neon roads  
- Glowing exploration trails  
- Cyan pulsing final path  
- Neon blue start and goal markers  

---

## Tech Stack

- Python 3  
- Pygame – rendering & animations  
- NetworkX – graph representation  
- OSMnx – downloading real road network data  

---

## Installation

```bash
# Clone repository
git clone https://github.com/thomasdmcmahon/cyberpunk-pathfinder.git
cd cyberpunk-pathfinder

# Create virtual environment
python -m venv venv
source venv/bin/activate   # mac/linux
venv\Scripts\activate      # windows

# Install dependencies
pip install -r requirements.txt

# Run the visualizer
python main.py
