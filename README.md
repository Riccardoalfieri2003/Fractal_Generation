# Interactive Fractal Taxonomy Studio 🎨🌀

A lightweight, interactive Python application built with **Pygame** and **NumPy** that turns freehand user sketches into self-similar mathematical fractals in real-time. 

Created as a fun side-project to explore mathematical chaos, complex dynamics, and spatial transformations.

---

## 🚀 Features

* **Freehand Canvas:** Draw any single-stroke shape or seed curve directly on the interactive canvas.
* **7 Fractal Taxonomy Engines:** Instantly transform your drawing into different fractal families (based on the Wikipedia classification):
  1. **Escape-Time Sets:** Classical Julia set dynamics ($Z \mapsto Z^2 + c$) parameterized by your drawing.
  2. **Iterated Function Systems (IFS):** Recursive vector transformation collages.
  3. **L-System Rewriting:** Rule-based string rewriting derived from stroke vectors.
  4. **Strange Attractors:** Chaotic Clifford Attractor mapping.
  5. **Random / DLA:** Diffusion-Limited Aggregation seeded on your stroke.
  6. **Finite Subdivision:** Barycentric triangular mesh subdivision.
  7. **Subdivision Links:** Braid loop geometry generated along path segments.
* **Interactive Navigation:** Smooth pan (left-click drag) and infinite zoom (mouse wheel scroll) across generated structures.

---

## 🛠️ Installation & Setup

### Prerequisites
Make sure you have Python 3.8+ installed.

### Install Dependencies
```bash
pip install pygame numpy
```

### Run the Application
```bash
python window.py
```

---

## 📁 Project Structure

* `window.py` - Pygame GUI implementation, control panel, buttons, and user event handling.
* `fractal.py` - Core mathematical computation engines, vector math, and rendering pipelines.

---

## 🎮 How to Use

1. Draw a continuous stroke or shape on the canvas using your mouse.
2. Click any of the **7 Fractal Generator** buttons in the right sidebar.
3. **Scroll Wheel** to Zoom in/out.
4. **Left Click + Drag** to Pan around the generated fractal space.
5. Click **Clear Drawing** to reset and sketch a new initiator shape!
