import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import re
import json
import math


class FontsDesigner:
    def __init__(self, root):
        self.root = root
        self.root.title("Fonts Designer App")

        self.canvas = tk.Canvas(root, width=500, height=500, bg="#F5F5F5")

        # background
        self.image = None
        self.filename = None
        # self.image = tk.PhotoImage(file="/Users/szymon/Documents/Projects/FontsMaker/letters/zdj.png", master=self.canvas)
        # self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

        self.canvas.pack()

        # created points
        self.points = []  # To store selected points
        self.size = 6
        self.dragged = None
        # true if point is dragged, false if bezier
        self.point_dragged = True

        # curves
        # curves is a dictionary like tag:points
        self.curves = {}
        self.current_curve_tag = 0  # tag of curve just added or modified
        self.curves_tags = [0]  # list of all curves tags
        self.quality = 100

        # modes
        self.delete_mode = False
        self.is_points_hiding_mode = False
        self.is_duplicate_mode = False
        self.extending_mode = False  # mode that takes care weather to extend or draw a new curve

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

        self.hide_points_button = tk.Button(root, text="Hide", command=self.toggle_hide)
        self.hide_points_button.pack()

        self.duplicate_point_button = tk.Button(root, text="Duplicate Point", command=self.toggle_duplicate)
        self.duplicate_point_button.pack(side=tk.RIGHT)

        # canvas setup
        delete_background_button = tk.Button(root, text="Remove Background", command=self.remove_bg)
        delete_background_button.pack(side=tk.RIGHT)

        # connect Bezier
        connect_curve_button = tk.Button(root, text="Connect Curves", command=self.connect_curve)
        connect_curve_button.pack(side=tk.RIGHT)

        # files management
        save_button = tk.Button(root, text="Save", command=self.export_image)
        save_button.pack(side=tk.LEFT)

        import_button = tk.Button(root, text="Import", command=self.import_image)
        import_button.pack(side=tk.LEFT)

        import_background = tk.Button(root, text="Import Background", command=self.load_and_center_image)
        import_background.pack(side=tk.LEFT)

        # canvas setup
        self.draw_grid()

    def remove_bg(self):
        self.canvas.delete('bg')

    def load_and_center_image(self, btn_run = True):

        if btn_run:
            filename = filedialog.askopenfilename(initialdir="/Users/szymon/Documents/Projects/FontsMaker/letters//",
                                                  title="Select a File",
                                                  filetypes=(("Text files",
                                                              "*.png"),))
            self.filename = filename

        if self.filename:
            pil_image = Image.open(self.filename)

            image_width, image_height = pil_image.size

            canvas_width = self.canvas.winfo_reqwidth()
            canvas_height = self.canvas.winfo_reqheight()

            scale_factor = min(canvas_width / image_width, canvas_height / image_height)

            pil_image = pil_image.resize((int(image_width * scale_factor), int(image_height * scale_factor)))

            self.image = ImageTk.PhotoImage(pil_image)

            x = (canvas_width - self.image.width()) // 2
            y = (canvas_height - self.image.height()) // 2

            # reset everything
            self.delete_tags_except(['grid'])
            self.curves = {}
            self.current_curve_tag = 0  # tag of curve just added or modified
            self.curves_tags = [0]

            # Create image on the canvas
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.image, tags="bg")
            self.canvas.tag_lower("bg")

    def draw_grid(self):
        # background grid
        for i in range(0, self.canvas.winfo_reqwidth(), 100):  # Change the '50' value to adjust the spacing
            self.canvas.create_line(i, 0, i, self.canvas.winfo_reqwidth(), fill='black',
                                    tags='grid')  # Draw vertical line
            self.canvas.create_line(0, i, self.canvas.winfo_reqwidth(), i, fill='black',
                                    tags='grid')  # Draw horizontal line

    def delete_tags_except(self, excepts):
        for id in self.canvas.find_all():
            if self.canvas.itemcget(id, "tags") not in excepts:
                self.canvas.delete(id)


    # TOGGLES
    def toggle_delete(self):
        if self.delete_mode:
            self.delete_button.configure(text="Delete")
        else:
            self.delete_button.configure(text="Draw")
        self.delete_mode = not self.delete_mode

    def toggle_hide(self):
        self.is_points_hiding_mode = not self.is_points_hiding_mode
        all_items = self.canvas.find_all()
        # hide points
        for id in all_items:
            tags = self.canvas.gettags(id)  # iterate through the tags to find the correct one
            for tag in tags:
                if re.match('##[0-9]+', tag):
                    if self.is_points_hiding_mode:
                        self.canvas.itemconfig(id, state='hidden')
                        self.hide_points_button.configure(text="Show")
                    else:
                        self.canvas.itemconfig(id, state='normal')
                        self.hide_points_button.configure(text="Hide")

    # on duplicate point set duplicate mode and reset other modes to default values
    def toggle_duplicate(self):
        self.is_duplicate_mode = not self.is_duplicate_mode
        self.delete_mode = False
        self.is_points_hiding_mode = False
        if self.is_duplicate_mode:
            self.duplicate_point_button.configure(text="Add Point Mode")
        else:
            self.duplicate_point_button.configure(text="Duplicate Point Mode")

    def export_image(self):
        filename = filedialog.asksaveasfilename(initialdir="/Users/szymon/Documents/Projects/FontsMaker/fonts//",
                                                title="Select a File",
                                                filetypes=(("Text files",
                                                            "*.txt"),))
        with open(filename, 'w') as file:
            json.dump(self.curves, file)
            file.close()

    def import_image(self):
        # when we import, get rid of everything in the canvas, except for background -bg and grid lines
        self.delete_tags_except(['bg', 'grid'])
        # get rid of everything in the memory, all points and curves data
        self.curves.clear()
        self.curves_tags = [0]
        self.current_curve_tag = 0
        self.points.clear()
        # read dictionary from the file

        filename = filedialog.askopenfilename(initialdir="/Users/szymon/Documents/Projects/FontsMaker/fonts//",
                                              title="Select a File",
                                              filetypes=(("Text files",
                                                         "*.txt"),))

        if filename:
            with open(filename, 'r') as file:
                imported = json.load(file)
                file.close()
                self.curves = {int(key): value for key, value in imported.items()}

            # restart canvas
            # self.draw_grid()
            self.redraw_curves()

    # function to iterate through all the curves on connect end of one with the beginning of the nearest
    def connect_curve(self):
        # find closest beginning to each ending
        beginnings = [points[0] for points in self.curves.values()]
        endings = [points[-1] for points in self.curves.values()]
        # iterating through endings and beginnings to find closest beginning
        for i in range(len(endings)):
            # reset colors
            self.canvas.itemconfig('#' + str(self.current_curve_tag), fill='blue')
            self.canvas.itemconfig('##' + str(self.current_curve_tag), fill='blue')
            min_dist = self.size  # size of the canvas as default value
            e_x, e_y, e_id = endings[i][0], endings[i][1], endings[i][2]
            beginning = None
            for j in range(len(beginnings)):
                # compare distances only between two distinct vurves
                if i != j:
                    b_x, b_y, b_id = beginnings[j][0], beginnings[j][1], beginnings[j][2]
                    # count distance to next start, compare with min_dist
                    if math.sqrt(((e_x - b_x) ** 2) + ((e_y - b_y) ** 2)) < min_dist:
                        min_dist = math.sqrt(((e_x - b_x) ** 2) + ((e_y - b_y) ** 2))
                        beginning = (b_x, b_y, b_id)

            if beginning is not None:
                # get curve tag

                tags = self.canvas.itemcget(e_id, "tags")[2::]  # to get curve id we need to get rid of '##'
                end_tag = int(tags)
                self.current_curve_tag = end_tag
                self.curves[end_tag][-1] = (beginning[0], beginning[1], e_id)  # update end value in curves dictionary
                self.current_curve_tag = end_tag
                valid_controls = self.draw_points(self.curves[self.current_curve_tag])
                self.curves[self.current_curve_tag] = valid_controls
                self.draw_bezier()

    # redraw curves after downloading from the file
    def redraw_curves(self):
        # iterate thorough dictionary and redraw each curve and its points
        for tag, points in self.curves.items():
            self.current_curve_tag = tag
            self.curves_tags.append(self.current_curve_tag)  # append redrawn curve tag to the list of tags on canvas
            # redraw points
            for point in points:
                x, y = point[0], point[1]
                point_id = self.canvas.create_oval(x - self.size, y - self.size, x + self.size, y + self.size,
                                                   fill="red")
                self.canvas.coords(point_id, x - self.size, y - self.size, x + self.size, y + self.size)
                self.points.append((x, y, point_id))
            # redraw curve
            self.add_new_curve(self.points)
            self.canvas.itemconfig(f"#{self.current_curve_tag}", fill="blue")
            self.canvas.itemconfig(f"##{self.current_curve_tag}", fill="blue")

        self.canvas.itemconfig(f"#{self.current_curve_tag}", fill="lightblue")

    # handle different behaviours of left click - adding points, deleteting points, extending curve
    def left_click(self, event):
        if not self.delete_mode and not self.is_duplicate_mode:
            self.add_point(event)
        elif self.delete_mode:
            self.delete_point(event)
        elif self.is_duplicate_mode:
            self.duplicate_point(event)

    # LEFT CLICK BEHAVIOURS
    def duplicate_point(self, event):
        x, y = event.x, event.y
        # list of points for newly generated curve
        new_control_points = []
        if self.current_curve_tag != 0:
            for i in range(len(self.curves[self.current_curve_tag])):
                p_x, p_y, p_id = self.curves[self.current_curve_tag][i][0], self.curves[self.current_curve_tag][i][1], \
                    self.curves[self.current_curve_tag][i][2]

                # some curve point has been clicked
                if x - self.size < p_x < x + self.size and y - self.size < p_y < y + self.size:
                    # self.curves[self.current_curve_tag].clear()  # clear bezier dictionary that belongs to this point
                    # self.canvas.delete(
                    #     f"##{self.current_curve_tag}")  # delete all points that belonged to this curve from the canvas

                    # duplication
                    new_point_one_x = (p_x - self.size)
                    new_point_two_x = (p_x + self.size)
                    new_control_points.append((new_point_one_x, p_y))
                    new_control_points.append((new_point_two_x, p_y))
                    new_control_points.extend(
                        self.curves[self.current_curve_tag][i + 1::])  # add rest points from the curve

                    # print(f"dupli: {self.curves[self.current_curve_tag]}")
                    valid_controls = self.draw_points(new_control_points)
                    self.canvas.itemconfig(f"##{self.current_curve_tag}", fill="lightblue")
                    # update control points
                    self.curves[self.current_curve_tag] = valid_controls
                    self.draw_bezier()
                    break
                else:
                    new_control_points.append((p_x, p_y))

    def delete_point(self, event):
        self.canvas.itemconfig(f"#{self.current_curve_tag}", fill="blue")
        self.canvas.itemconfig(f"##{self.current_curve_tag}", fill="blue")
        self.current_curve_tag = 0
        x, y = event.x, event.y
        # get closes identifier of an object
        id = self.canvas.find_closest(x, y)  # returns a tuple
        # check if there is anything close
        if len(id) > 0:
            # get tag of the closest item
            tags = self.canvas.itemcget(id[0], "tags")
            # if curve or point was clicked
            # tag of curve consists of #number
            if tags and re.match('\{#+[0-9]+\}\scurrent', tags):
                # rest of the curve has tag #int, find beginning of this kind of string
                b, e = re.search('\#[0-9]+', tags).span()
                self.canvas.delete(tags[b:e])  # delete curve with tag extracted from clicked point
                self.canvas.delete('#' + tags[b:e])  # point tag is just one # more
                # if currently deleted curve is the one selected, reset selected curve
                if self.current_curve_tag == int(tags[b + 1:e]):
                    self.current_curve_tag = 0
                del self.curves[int(tags[
                                    b + 1:e])]  # we extract number from curve tag given with #int, delete this curve from dictionary

            # deleting other points
            elif tags and 'current' == tags:
                self.canvas.delete('current')

    # RIGHT CLICK BEHAVIOURS
    def select_point(self, event):
        x, y = event.x, event.y
        # search in free points
        for p_x, p_y, id in self.points:
            if x - self.size < p_x < x + self.size and y - self.size < p_y < y + self.size:
                self.dragged = (p_x, p_y, id)
                self.point_dragged = True
                return

        # reset curve and points colors
        self.canvas.itemconfig(f"#{self.current_curve_tag}", fill="blue")
        self.canvas.itemconfig(f"##{self.current_curve_tag}", fill="blue")

        # search in curve points
        for tag, points in self.curves.items():
            for p_x, p_y, id in points:
                # check which curve was clicked
                if x - self.size < p_x < x + self.size and y - self.size < p_y < y + self.size:
                    self.dragged = (p_x, p_y, id)

                    self.current_curve_tag = tag
                    # change curve color as well as points color
                    self.canvas.itemconfig(f"#{self.current_curve_tag}", fill="lightblue")
                    self.canvas.itemconfig(f"##{self.current_curve_tag}", fill="lightblue")
                    self.point_dragged = False
                    return

        # turn off curve extending mode
        self.current_curve_tag = 0

    def drag(self, event):
        if self.dragged is not None:
            x, y = event.x, event.y
            n, m, point_id = self.dragged
            # move point with given id
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
                        self.curves[self.current_curve_tag][i] = (x, y, point_id)
                        self.canvas.coords(point_id, x - self.size, y - self.size, x + self.size, y + self.size)
                        # self.canvas.delete("##" + str(self.current_curve_tag))
                        # self.draw_points(self.curves[self.current_curve_tag], "##" + str(self.current_curve_tag))
                        self.draw_bezier()
                        return

    # redraws curve with given tag
    def draw_bezier(self):
        # print(self.current_curve_tag)
        self.canvas.delete('#' + str(self.current_curve_tag))
        line_points = [self.count_bezier(i / self.quality) for i in range(self.quality + 1)]
        # for each created curve we add a tag which will be its index in curves list
        for i in range(len(line_points) - 1):
            x1, y1 = line_points[i]
            x2, y2 = line_points[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill="lightblue", width=2, tags=('#' + str(self.current_curve_tag)))

    # draw curve points
    def draw_points(self, points):
        self.canvas.delete(
            f"##{self.current_curve_tag}")  # delete all points that belonged to this curve from the canvas
        new_points = []  # list for new points added
        for point in points:
            x, y = point[0], point[1]
            point_id = self.canvas.create_oval(x - self.size, y - self.size, x + self.size, y + self.size, fill='blue',
                                               tags="##" + str(self.current_curve_tag))
            self.canvas.coords(point_id, x - self.size, y - self.size, x + self.size, y + self.size)
            new_points.append((x, y, point_id))
        return new_points

    def add_point(self, event):
        x, y = event.x, event.y
        point_id = self.canvas.create_oval(x - self.size, y - self.size, x + self.size, y + self.size, fill="red")
        # this kind of curve tag indicates that we can add new curve
        if self.current_curve_tag == 0:
            self.canvas.coords(point_id, x - self.size, y - self.size, x + self.size, y + self.size)
            self.points.append((x, y, point_id))
        # extend curve
        else:
            new_point = (x, y, point_id)
            # add this point to the curve
            self.curves[self.current_curve_tag].append(new_point)
            color = self.canvas.itemcget('##' + str(self.current_curve_tag), 'fill')
            self.canvas.itemconfig(point_id, fill=color,
                                   tags='##' + str(self.current_curve_tag))  # change color if part of curve and add tag
            # self.canvas.delete("##" + str(self.current_curve_tag)) # delete all points before updating
            # self.draw_points(self.curves[self.current_curve_tag], "##" + str(self.current_curve_tag)) # redraw points
            self.draw_bezier()

    # buttons functionalities
    def clear_points(self):
        for x, y, point_id in self.points:
            self.canvas.delete(point_id)
        self.points = []

    # change colors of the points
    def change_points_colors(self, color):
        for x, y, id in self.points:
            self.canvas.itemconfig(id, fill=color)

    # change tags of the points
    def change_points_tags(self, tag):
        for x, y, point_id in self.points:
            self.canvas.addtag_withtag(tag, point_id)

    def make_bezier(self):
        # we want to draw Bezier only if there are points
        if self.points:
            self.canvas.itemconfig(f"#{self.current_curve_tag}", fill="blue")
            # print(self.points)
            # after Bezier Curve is created the points now make another geometrical structure
            # we delete points and add them to your curves dictionary
            new_tag = max(self.curves_tags) + 1  # new tag is the next biggest number in the list of curves tags

            self.curves_tags.append(new_tag)  # add new tag to the list
            self.current_curve_tag = new_tag  # update current tag
            # print(self.current_curve_tag)
            self.curves[self.current_curve_tag] = []
            self.add_new_curve(self.points)

    def add_new_curve(self, points):
        # # generate new color
        # color = _from_rgb((random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)))
        # # change colors of points to this random color
        self.change_points_colors('lightblue')
        # apply curve tags to points used to make curve
        self.change_points_tags('##' + str(self.current_curve_tag))

        self.curves[self.current_curve_tag] = points.copy()
        # when button is clicked all points are connected in Bezier Curve
        points.clear()
        # print(f"current curve points: {self.curves[self.current_curve_tag]}")
        # draw bezier curve
        self.draw_bezier()

    def count_bezier(self, t):
        n = len(self.curves[self.current_curve_tag])
        # beta_i^(0) for every control point is this very point
        beta_x = [node[0] for node in self.curves[self.current_curve_tag]]
        beta_y = [node[1] for node in self.curves[self.current_curve_tag]]
        for i in range(1, n + 1):
            for j in range(n - i):
                beta_x[j] = beta_x[j] * (1 - t) + beta_x[j + 1] * t
                beta_y[j] = beta_y[j] * (1 - t) + beta_y[j + 1] * t
        return beta_x[0], beta_y[0]


if __name__ == "__main__":
    root = tk.Tk()
    app = FontsDesigner(root)
    root.mainloop()
