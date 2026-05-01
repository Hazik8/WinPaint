🎨 ArtiPaint Pro — a Python-based graphics editor
ArtiPaint Pro is a simple yet powerful open-source image editing application. It lets you paint with a brush, add text with custom fonts and colors, and move existing text directly on the canvas.

✨ Features
Feature Description
🖌️ Drawing: Brush with adjustable size (1–30 pixels) and color selection. Smooth, unbroken lines.
✍️ Adding Text: Text with a choice of font (all system fonts), size, and color. Add by clicking on the canvas.
🖱️ Moving Text: Select the text (in "Move Text" mode) and drag it anywhere on the image.
📂 Image Upload: PNG, JPG, JPEG, and BMP formats are supported.
💾 Save: Saves the result as a PNG or JPG (text and images are combined into a single layer).
🆕 New Canvas: Creates a blank canvas with the specified dimensions.
🗑️ Reset Drawings: Removes only brush strokes; text remains intact.
🔄 Merge Text: Glues the text to the background; after this, the text cannot be moved.

🖼️ Custom Icon
The app automatically uses the logo.png file (a square image) as its window icon. If the file is missing, no problem; the standard Tkinter icon is used.

🚀 Installation and Launch
1. Make sure you have Python 3.7+ installed
-------------------
bash              -
python --version  -
-------------------

2. Install the Pillow library
--------------------
bash               -
pip install Pillow -
--------------------
3. Download the script
Save the code from the artipaint_pro.py file (or copy it) to any folder.

4. (Optional) Add a logo
Place the logo.png file in the same folder—it will become the window icon.

5. Run the application
bash
python artipaint_pro.py

🎮 How to use
1.Select a mode in the top panel:
🖌️ Brush — draw on the canvas.
✍️ Text — click anywhere to add text.
🖱️ Move text — click on existing text and drag it.
2.Brush settings:
Color: "Brush color" button.
Size: slider.
3.Text settings (before adding):
Enter the text in the field.
Select the font, size, and color.
Click "Add Text" or click on the canvas in "Text" mode.
4.Working with files:
Load: File menu → Load or Ctrl+O.
Save: File menu → Save As or Ctrl+S.
New canvas: File menu → New Canvas.
5.Edit:
"Reset Drawings" erases all brush strokes.
"Merge Text with Background" makes the text part of the image (cannot be moved).

🛠️ Requirements
Python 3.7 or later
Pillow library (install via pip)
📁 Project Structure
------------------------------------------------
artipaint_pro/                                 -
│                                              -
├── artipaint_pro.py # Main application script -
├── logo.png # (Optional) window icon          -
└── README.md # This file                      -
------------------------------------------------
📜 License
The project is distributed under the MIT license. You are free to use, modify, and distribute the code.

🤝 Contributing
If you find a bug or want to add a new feature, create an issue or pull request on GitHub.
