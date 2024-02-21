# Bezier Curves Fonts Maker

This Python 3 Tkinter application combines the concept of drawing Bezier Curves to facilitate the creation of custom fonts.

## Editor Features

The editor allows users to:

- Select custom points
- Draw Bezier Curves
- Delete 'free points'
- Delete curves
- Hide points
- Save the curve in an app-friendly .txt format
- Import previous projects

<p align="center">
  <img src="https://github.com/porfinogeneta/FontsMaker/blob/master/editor.png" width="400px" height="400px"/>
</p>

## Example of Letter 'A'

Here's an example where the letter 'A' is created using just 6 Bezier Curves. The points that create each Bezier Curve are visible as small colorful dots.

<p align="center">
  <img src="https://github.com/porfinogeneta/FontsMaker/blob/master/points.png" style="width: 400px; height: 400px;"/>
</p>

# Manual

## Buttons Descriptions (Left to Right)

- **Free Points:** Red points added to the canvas when no curve is selected
- **Curve SELECTED:** Highlighted with 'light blue'
- **Clear Points:** Delete all free points
- **Delete/Draw:** Mode toggle for deleting curves with LEFT CLICK
    - Button says DRAW: In DELETE mode
    - Otherwise: In drawing mode - just LEFT CLICK to add points
- **Import:** Importing curve saved as .txt format (simple Python dictionary {curve_tag: [control_points]})
- **Import Background:** Import any .png file to redraw it on the canvas using Bezier Curves
- **Show/Hide:** Toggle to hide and show control points
    - Button says SHOW: Exit hide mode, see the points
    - Button says HIDE: Hide the points
- **Connect Curves:** Connect all close curves together - curve is considered 'close' when its end is 'point size' away from the beginning of the next curve
- **Remove Background:** Remove background you set; if there is no background, nothing happens
- **Duplicate Point Mode/Add Point Mode:** Toggle to add points in any place on Bezier Curve
    - Button says DUPLICATE PONT MODE: In ADD POINT MODE, just create curves normally
    - Button says ADD POINT MODE: You can only duplicate points on curves, no drawing ;(
- **Make Bezier:** Connects all 'free points' to one adjustable curve

### MOUSE CLICK FUNCTIONALITIES

- **LEFT CLICK:**
    - Curve extending/adding free points/deleting (functionality depends on MODE)
    (REMEMBER) - when delete mode is on you CAN'T draw, please deselect Delete Button
- **RIGHT CLICK:**
    - Control points moving/free points moving/curve selecting/curve deselecting

### TO CREATE A CURVE AND PLAY:

- EXIT delete mode or any other mode
- If curve is selected, it will extend it
- If curve is not selected, it will just add a 'free point' (red dot)

## CREDITS

- Font Created by Copying of one found on Pinterest - [Pinterest Link](https://pl.pinterest.com/pin/403846291594771476/visual-search/?x=16&y=16&w=414&h=540&cropSource=6&surfaceType=flashlight)
- All Build using tk inter - [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- My Github Repo - https://github.com/porfinogeneta/FontsMaker/tree/extended_version
