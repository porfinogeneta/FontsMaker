import tkinter as tk
from tkinter import filedialog
import re
import random
import json

from utils import _from_rgb
class FontsDesigner:
    def __init__(self, root):
        self.root = root
        self.root.title("Fonts Designer App")

        self.canvas = tk.Canvas(root, width=500, height=500, bg="white")
        self.canvas.pack()

        # created points
        self.points = []  # To store selected points
        self.size = 4
        self.dragged = None
        # true if point is dragged, false if bezier
        self.point_dragged = True

        # curves
        # curves is a dictionary like tag:points
        self.curves = {}
        self.current_curve_tag = 0 # tag of curve just added or modified
        self.curves_tags = [0] # list of all curves tags
        self.quality = 50

        # modes
        self.delete_mode = False
        self.is_points_hiding = False

        # bind functions to left and right mouse clicks
        self.drag_data = {"item": None, "x": 0, "y": 0}  # Data for tracking dragging
        # bind left to add points
        self.canvas.bind("<Button-1>", self.left_click)
        # bind right to move and drag points
        self.canvas.bind("<Button-2>", self.select_point)
        self.canvas.bind("<B2-Motion>", self.drag)
        # self.canvas.bind("<ButtonRelease-2>", self.release_point)

        # buttons
        clear_button = tk.Button(root, text="Clear Points", command=self.clear_points)
        clear_button.pack(side=tk.LEFT)

        self.delete_button = tk.Button(root, text="Delete", command=self.toggle_delete, bg="blue")
        self.delete_button.pack(side=tk.LEFT)

        make_bezier_button = tk.Button(root, text="Make Bezier", command=self.make_bezier)
        make_bezier_button.pack(side=tk.RIGHT)

        save_button = tk.Button(root, text="Save", command=self.export_image)
        save_button.pack(side=tk.RIGHT)

        import_button = tk.Button(root, text="Import", command=self.import_image)
        import_button.pack()

        self.hide_points_button = tk.Button(root, text="Hide", command=self.toggle_hide)
        self.hide_points_button.pack()

        self.draw_grid()


    def draw_grid(self):
        # background grid
        for i in range(0, 500, 100):  # Change the '50' value to adjust the spacing
            self.canvas.create_line(i, 0, i, 500, fill='black')  # Draw vertical line
            self.canvas.create_line(0, i, 500, i, fill='black')  # Draw horizontal line


    def toggle_delete(self):
        if self.delete_mode:
            self.delete_button.configure(text="Delete")
        else:
            self.delete_button.configure(text="Draw")
        self.delete_mode = not self.delete_mode

    def toggle_hide(self):
        self.is_points_hiding = not self.is_points_hiding
        all_items = self.canvas.find_all()
        # hide points
        for id in all_items:
            tags = self.canvas.gettags(id) # iterate through the tags to find the correct one
            for tag in tags:
                if re.match('##[0-9]+', tag):
                    if self.is_points_hiding:
                        self.canvas.itemconfig(id, state='hidden')
                        self.hide_points_button.configure(text="Show")
                    else:
                        self.canvas.itemconfig(id, state='normal')
                        self.hide_points_button.configure(text="Hide")



    def export_image(self):
        filename = filedialog.asksaveasfilename(initialdir="/Users/szymon/Documents/FontsMaker/fonts//",
                                              title="Select a File",
                                              filetypes=(("Text files",
                                                          "*.txt"),))
        with open(filename, 'w') as file:
            json.dump(self.curves, file)
            file.close()

    def import_image(self):
        # when we import, get rid of everything in the canvas
        self.canvas.delete("all")
        # get rid of everything in the memory, all points and curves data
        self.curves.clear()
        self.curves_tags = [0]
        self.current_curve_tag = 0
        self.points.clear()
        # read dictionary from the file

        filename = filedialog.askopenfilename(initialdir="/Users/szymon/Documents/FontsMaker/fonts//",
                                                title="Select a File",
                                                filetypes=(("Text files",
                                                            "*.txt"),))
        with open(filename, 'r') as file:
            imported = json.load(file)
            file.close()
            self.curves = {int(key): value for key, value in imported.items()}

        # restart canvas
        self.draw_grid()
        self.redraw_curves()


    def redraw_curves(self):
        # iterate thorough dictionary and redraw each curve and its points
        for tag, points in self.curves.items():
            self.current_curve_tag = tag
            self.curves_tags.append(self.current_curve_tag) # append redrawn curve tag to the list of tags on canvas
            # redraw points
            for point in points:
                x,y,_ = point
                point_id = self.canvas.create_oval(x - self.size, y - self.size, x + self.size, y + self.size, fill="red")
                self.canvas.coords(point_id, x - self.size, y - self.size, x + self.size, y + self.size)
                self.points.append((x, y, point_id))
            # redraw curve
            self.curve_count_and_draw()



    # handle different behaviours of left click
    def left_click(self, event):
        if not self.delete_mode:
            self.add_point(event)
        else:
            x, y = event.x, event.y
            # get closes identifier of an object
            id = self.canvas.find_closest(x,y) # returns a tuple
            # check if there is anything close
            if len(id) > 0:
                # get tag of the closest item
                tags = self.canvas.itemcget(id[0], "tags")
                # if curve or point was clicked
                # tag of curve consists of #number
                if tags and re.match('\{#+[0-9]+\}\scurrent', tags):
                    # rest of the curve has tag #int, find beginning of this kind of string
                    b,e = re.search('\#[0-9]+', tags).span()
                    self.canvas.delete(tags[b:e]) # delete curve with tag extracted from clicked point
                    self.canvas.delete('#' + tags[b:e]) # point tag is just one # more
                    del self.curves[int(tags[b+1:e])] # we extract number from curve tag given with #int, delete this curve from dictionary
                # deleting other points
                elif tags and 'current' == tags:
                    self.canvas.delete('current')



    def select_point(self, event):
        x,y = event.x, event.y

        # search in free points
        for p_x,p_y,id in self.points:
            if x - self.size < p_x < x + self.size and y - self.size < p_y < y + self.size:
                self.dragged = (p_x,p_y,id)
                self.point_dragged = True

        # search in curve points
        for tag, points in self.curves.items():
            for p_x, p_y, id in points:
                if x - self.size < p_x < x + self.size and y - self.size < p_y < y + self.size:
                    self.dragged = (p_x, p_y, id)
                    self.current_curve_tag = tag
                    self.point_dragged = False

    def drag(self, event):
        if self.dragged is not None:
            x, y = event.x, event.y
            n, m, point_id = self.dragged
            self.canvas.coords(point_id, x - self.size, y - self.size, x + self.size, y + self.size)

            # point is dragged
            if self.point_dragged:
                # finding the index of a dragged point
                # find a given point and replace it
                for i in range(len(self.points)):
                    if self.points[i][2] == point_id:
                        self.points[i] = (x, y, point_id)
            else:
                for i in range(len(self.curves[self.current_curve_tag])):
                    # if we found the point in a given curve, we update it
                    if self.curves[self.current_curve_tag][i][2] == point_id:
                        self.curves[self.current_curve_tag][i] = (x,y,point_id)
                        self.update_bezier()


    def update_bezier(self):
        print(self.current_curve_tag)
        self.canvas.delete('#' + str(self.current_curve_tag))
        line_points = [self.count_bezier(i / self.quality) for i in range(self.quality + 1)]
        # for each created curve we add a tag which will be its index in curves list
        # print(line_points)
        for i in range(len(line_points) - 1):
            x1, y1 = line_points[i]
            x2, y2 = line_points[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=5, tags=('#' + str(self.current_curve_tag)))

    def add_point(self, event):
        x, y = event.x, event.y
        point_id = self.canvas.create_oval(x - self.size, y - self.size, x + self.size, y + self.size, fill="red")
        self.canvas.coords(point_id, x - self.size, y - self.size, x + self.size, y + self.size)
        self.points.append((x, y, point_id))

    # buttons functionalities
    def clear_points(self):
        for x, y, point_id in self.points:
            self.canvas.delete(point_id)
        self.points = []




    # change colors of the points
    def change_points_colors(self, color):
        for x,y,id in self.points:
            self.canvas.itemconfig(id, fill=color)

    # change tags of the points
    def change_points_tags(self, tag):
        for x,y,point_id in self.points:
            self.canvas.addtag_withtag(tag, point_id)

    def make_bezier(self):

        # print(self.points)
        # after Bezier Curve is created the points now make another geometrical structure
        # we delete points and add them to your curves dictionary
        new_tag = max(self.curves_tags) + 1 # new tag is the next biggest number in the list of curves tags

        self.curves_tags.append(new_tag) # add new tag to the list
        self.current_curve_tag = new_tag # update current tag
        # print(self.current_curve_tag)
        self.curves[self.current_curve_tag] = []
        self.curve_count_and_draw()


    def curve_count_and_draw(self):
        # generate new color
        color = _from_rgb((random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)))
        # change colors of points to this random color
        self.change_points_colors(color)
        # apply curve tags to points used to make curve
        self.change_points_tags('##' + str(self.current_curve_tag))

        self.curves[self.current_curve_tag] = self.points
        # when button is clicked all points are connected in Bezier Curve
        self.points = []

        line_points = [self.count_bezier(i / self.quality) for i in range(self.quality)]
        # for each created curve we add a tag which will be its index in curves list
        # print(line_points)
        for i in range(len(line_points) - 1):
            x1, y1 = line_points[i]
            x2, y2 = line_points[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill='blue', width=5, tags=('#' + str(self.current_curve_tag)))

    def count_bezier(self, t):
        n = len(self.curves[self.current_curve_tag])


        # beta_i^(0) for every control point is this very point
        beta_x = [node[0] for node in self.curves[self.current_curve_tag]]
        beta_y = [node[1] for node in self.curves[self.current_curve_tag]]
        for i in range(1, n+1):
            for j in range(n-i):
                beta_x[j] = beta_x[j] * (1 - t) + beta_x[j+1]*t
                beta_y[j] = beta_y[j] * (1 - t) + beta_y[j+1]*t
        return beta_x[0], beta_y[0]

if __name__ == "__main__":
    root = tk.Tk()
    app = FontsDesigner(root)
    root.mainloop()
