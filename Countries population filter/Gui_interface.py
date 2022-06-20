from tkinter import *
from tksheet import Sheet
import sqlalchemy as sql
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

class Gui_interface(object):
    """a class for storing and operating on components from gui"""

    def __init__(self, title: str, data):
        self.data = data
        self.root = Tk()
        self.root.title(title)
        self.root.geometry("1000x700")
        self.create_table(self.root, self.data)
        filter_values = self.create_select_menu(self.root, self.data)
        buttons_frame = Frame(self.root, width=40, height=4)
        btn_filter = Button(buttons_frame, text='Filter', height=4, width=20, command=self.filter)
        btn_filter.grid(row=0, column=0, sticky=W)
        btn_analyze = Button(buttons_frame, text='Analyze', height=4, width=20, command=self.analyze)
        btn_analyze.grid(row=0, column=1, sticky=E)
        buttons_frame.grid(row=1, column=1)
        self.root.mainloop()

    def create_table(self, root: Tk, data):
        frame = Frame(root, width=700, height=500)
        frame.grid_columnconfigure(0, weight = 1)
        frame.grid_rowconfigure(0, weight = 1)
        self.sheet = Sheet(frame, width=700, height=500, data=[d.values() for d in data.select()], headers=data.active_table.columns.keys())
        self.sheet.enable_bindings()
        frame.grid(row = 0, column = 0, sticky = "nswe")
        self.sheet.grid(row = 0, column = 0, sticky = "nswe")

    def create_select_menu(self, root: Tk, data):
        selection = Frame(root, width=300, height=500)
        selection.grid(row=0, column=1)
        grid_iterator_y = 0
        self.enabled_checkboxes = {}
        for column in data.active_table.columns.keys()[2:4]:
            self.enabled_checkboxes[column] = {}
            grid_iterator_x = 0
            lbl = Label(selection, text=column)
            lbl.grid(row=grid_iterator_x, column=grid_iterator_y, sticky=W)
            grid_iterator_x += 1
            sel_values_from_column = sql.select(data.active_table.c[column])
            values_from_column = data.conn.execute(sel_values_from_column)
            set_from_select = sorted({value for value, in values_from_column})
            for value in set_from_select:
                self.enabled_checkboxes[column][value] = IntVar()
                checkBox = Checkbutton(selection, text=value, variable=self.enabled_checkboxes[column][value])
                checkBox.grid(row=grid_iterator_x, column=grid_iterator_y, sticky=W)
                grid_iterator_x += 1
            grid_iterator_y += 1

    def enabled_checkboxes_to_filter(self):
        filter_dict = {}
        for key in self.enabled_checkboxes:
            filter_dict[key] = []
            for value in self.enabled_checkboxes[key]:
                if self.enabled_checkboxes[key][value].get() == 1:
                    filter_dict[key].append(value)
        return filter_dict

    def filter(self):
        filter_dict = self.enabled_checkboxes_to_filter()
        filter_res = self.data.select(filter_dict)
        self.sheet.set_sheet_data(data = [d.values() for d in filter_res],
                                  reset_col_positions = True,
                                  reset_row_positions = True,
                                  redraw = True,
                                  verify = False,
                                  reset_highlights = False)

    def analyze(self):
        self.filter()
        column = 'population'
        analyze_window = Toplevel(self.root)
        analyze_window.title('Analysis')
        min, max, sum = self.get_stats(column)
        lbl_info = Label(analyze_window, text=f'Min: {min[0]} {min[1]}, Max: {max[0]} {max[1]}, Sum: {sum}')
        lbl_info.pack()
        self.create_chart(analyze_window, self.data.select_column(column, self.enabled_checkboxes_to_filter()))

    def create_chart(self, window, data: list):
        fig = Figure(figsize = (5, 5), dpi = 200)
        numbers, labels = [], []
        for row in data:
            labels.append(row[0])
            numbers.append(row[1])
        ax = fig.add_subplot(111)
        ax.pie(numbers, 
                explode=[(0.2 if x >= 20000000 else 0) for x in numbers],
                labels=[(labels[i] if numbers[i] >= 20000000 else '') for i in range(0, len(numbers))])
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, window)
        toolbar.update()
        canvas.get_tk_widget().pack()

    def get_stats(self, column: str):
        min = self.data.select_min('population', self.enabled_checkboxes_to_filter())
        max = self.data.select_max('population', self.enabled_checkboxes_to_filter())
        sum = self.data.select_sum('population', self.enabled_checkboxes_to_filter())
        return *[(d.values()[0], d.values()[1]) for d in min], *[(d.values()[0], d.values()[1]) for d in max], *[d.values()[0] for d in sum]