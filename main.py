import tkinter as tk
import math
class FontsDesigner:
    def __init__(self, root):
        self.root = root
        self.root.title("Fonts Designer App")

        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack()

        # created points
        self.points = []  # To store selected points
        self.size = 4
        self.dragged = None
        self.all_points = []
        # true if point is dragged, false if bezier
        self.point_dragged = True

        # curves
        # curves is a dictionary like tag:points
        self.curves = {}
        self.current_curve_tag = 0 # tag of curve just added or modified
        self.curves_tags = [0] # list of all curves tags

        # bind functions to left and right mouse clicks
        self.drag_data = {"item": None, "x": 0, "y": 0}  # Data for tracking dragging
        # bind left to add points
        self.canvas.bind("<Button-1>", self.add_point)
        # bind right to move and drag points
        self.canvas.bind("<Button-2>", self.select_point)
        self.canvas.bind("<B2-Motion>", self.drag)
        # self.canvas.bind("<ButtonRelease-2>", self.release_point)

        # buttons
        clear_button = tk.Button(root, text="Clear Points", command=self.clear_points)
        clear_button.pack()

        make_bezier_button = tk.Button(root, text="Make Bezier", command=self.make_bezier)
        make_bezier_button.pack()

    def select_point(self, event):
        x,y = event.x, event.y

        def flatten(xss):
            return [x for xs in xss for x in xs]

        # list of all points, the ones involved in curves as well as separate ones
        curves_nodes = flatten(self.curves.values())

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
                    print(self.current_curve_tag)
                    self.point_dragged = False

        # for p_x,p_y,id in curves_nodes:
        #     if x - self.size < p_x < x + self.size and y - self.size < p_y < y + self.size:
        #         self.dragged = (p_x,p_y,id)
        #         self.point_dragged = False

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
                # for tag, points in self.curves.items():
                #     for i in range(len(points)):
                #         if points[i][2] == point_id:
                #             self.current_curve_tag = tag
                #             self.curves[tag][i] = (x,y,point_id)
                #             print(self.current_curve_tag)
                #             self.update_bezier()
                #             break



    def update_bezier(self):
        # self.curve_tag = curve_tag
        self.canvas.delete('#' + str(self.current_curve_tag))
        line_points = [self.count_bezier(i / 10) for i in range(11)]
        # for each created curve we add a tag which will be its index in curves list
        # print(line_points)
        for i in range(len(line_points) - 1):
            x1, y1 = line_points[i]
            x2, y2 = line_points[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags=('#' + str(self.current_curve_tag)))

    # def release_point(self, event):
    #     x,y,id = self.dragged
    #


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

    def make_bezier(self):

        # print(self.points)
        # after Bezier Curve is created the points now make another geometrical structure
        # we delete points and add them to your curves dictionary
        new_tag = max(self.curves_tags) + 1 # new tag is the next biggest number in the list
        self.curves_tags.append(new_tag) # add new tag to the list
        self.current_curve_tag = new_tag # update current tag
        print(self.current_curve_tag)
        self.curves[self.current_curve_tag] = []

        self.curves[self.current_curve_tag] = self.points
        # when button is clicked all points are connected in Bezier Curve
        self.points = []
        line_points = [self.count_bezier(i/10) for i in range(11)]
        # for each created curve we add a tag which will be its index in curves list
        # print(line_points)
        for i in range(len(line_points) - 1):
            x1, y1 = line_points[i]
            x2, y2 = line_points[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags=('#' + str(self.current_curve_tag)))


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
