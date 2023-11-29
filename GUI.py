import tkinter as tk
import os
from tkinter import filedialog
from tkinter import messagebox
from data_loading import Data_loading
from data_processing import Data_process
from process_names import Find_keywords
from tkcalendar import DateEntry



class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Main window with load from api and load from files blocks"""

        # checkbox for reading xlsx files
        self.read_xlsx_var = tk.BooleanVar()
        self.read_xlsx_checkbox = tk.Checkbutton(self, text="Read XLSX files", variable=self.read_xlsx_var)
        self.read_xlsx_checkbox.grid(row=4, column=0, sticky=tk.W)

        # checkbox for finding keywords
        self.find_keywords_var = tk.BooleanVar()
        self.find_keywords_checkbox = tk.Checkbutton(self, text="Find keywords", variable=self.find_keywords_var)
        self.find_keywords_checkbox.grid(row=4, column=1, sticky=tk.W)

        # # save directory entry
        # self.save_label = tk.Label(self, text="Save directory:")
        # self.save_label.grid(row=0, column=0, sticky=tk.W)
        # self.save_entry = tk.Entry(self)
        # self.save_entry.grid(row=0, column=1)
        # self.save_button = tk.Button(self, text="Browse...", command=self.browse_save_directory)
        # self.save_button.grid(row=0, column=2)


        # browse directory with target files or target file
        self.directory_label = tk.Label(self, text="Directory:")
        self.directory_label.grid(row=2, column=0, sticky=tk.W)
        self.directory_entry = tk.Entry(self)
        self.directory_entry.grid(row=2, column=1)
        self.directory_button = tk.Button(self, text="Browse...", command=self.browse_directory)
        self.directory_button.grid(row=2, column=2)


        # checkboks for loading from directory or file
        self.dir_file_var = tk.StringVar()
        self.dir_file_var.set("Dir")
        self.rb1 = tk.Radiobutton(self, text="Папка", variable=self.dir_file_var, value="Dir")
        self.rb2 = tk.Radiobutton(self, text="Файл", variable=self.dir_file_var, value="File")
        self.rb1.grid(row=4, column=3, sticky='n')
        self.rb2.grid(row=4, column=4, sticky='n')

        # # category entry
        # self.category_label = tk.Label(self, text="Category:")
        # self.category_label.grid(row=1, column=0, sticky=tk.W)
        # self.category_entry = tk.Entry(self)
        # self.category_entry.grid(row=1, column=1)

        # selection entry
        self.selection_label = tk.Label(self, text="Filter values:")
        self.selection_label.grid(row=5, column=0, sticky=tk.W)
        self.selection_entry = tk.Entry(self)
        self.selection_entry.grid(row=5, column=1)

        # filte type
        self.sel_type_var = tk.StringVar()
        self.sel_type_var.set("Include")
        self.rb3 = tk.Radiobutton(self, text="Include", variable=self.sel_type_var, value="Include")
        self.rb4 = tk.Radiobutton(self, text="Exclude", variable=self.sel_type_var, value="Exclude")
        self.rb3.grid(row=5, column=3, sticky='n')
        self.rb4.grid(row=5, column=4, sticky='n')

        # language entry
        self.language_label = tk.Label(self, text="Language:")
        self.language_label.grid(row=7, column=2, sticky=tk.W)
        self.language_entry = tk.Entry(self)
        self.language_entry.grid(row=7, column=3)

        # Filter col name
        self.filter_col = tk.Label(self, text="Filter col:")
        self.filter_col.grid(row=6, column=3, sticky=tk.W)
        self.filter_col_entry = tk.Entry(self)
        self.filter_col_entry.grid(row=6, column=4)

        # checkbox for set dates
        self.set_dates_var = tk.BooleanVar(value=True)
        self.set_dates_checkbox = tk.Checkbutton(self, text="Set dates", variable=self.set_dates_var)
        self.set_dates_checkbox.grid(row=4, column=2, sticky=tk.W)

        # # checkbox for separate files
        # self.sep_files_var = tk.BooleanVar()
        # self.sep_files_checkbox = tk.Checkbutton(self, text="Separate files", variable=self.sep_files_var)
        # self.sep_files_checkbox.grid(row=2, column=3, sticky=tk.W)

        # browse markers file
        self.markers_label = tk.Label(self, text="Markers file:")
        self.markers_label.grid(row=6, column=0, sticky=tk.W)
        self.markers_entry = tk.Entry(self)
        self.markers_entry.grid(row=6, column=1)
        self.markers_button = tk.Button(self, text="Browse...", command=self.browse_markers)
        self.markers_button.grid(row=6, column=2)

        # name column entry
        self.name_colum_label = tk.Label(self, text="Name colum:")
        self.name_colum_label.grid(row=7, column=0, sticky=tk.W)
        self.name_colum_entry = tk.Entry(self)
        self.name_colum_entry.grid(row=7, column=1)

        # load data button
        self.load_button = tk.Button(self, text="Load data", command=self.load_data)
        self.load_button.grid(row=8, column=1)

        # quit button
        self.quit_button = tk.Button(self, text="Quit", command=self.master.destroy)
        self.quit_button.grid(row=8, column=2)




    def browse_directory(self):
        """Get dir or file to load for further processing"""
        if self.dir_file_var.get() == 'Dir':
            directory = filedialog.askdirectory()
        else:
            filetypes = [("CSV files", "*.csv"), ("XLSX files", "*.xlsx")]
            directory = filedialog.askopenfilenames(initialdir=".", filetypes=filetypes)
        self.directory_entry.delete(0, tk.END)
        self.directory_entry.insert(0, directory)

    def browse_markers(self):
        """Get file with markers list for marking function"""
        filetypes = [("Текстовые файлы", "*.txt"), ("XLSX files", "*.xlsx"), ("CSV files", "*.csv")]
        directory = filedialog.askopenfilenames(initialdir=".", filetypes=filetypes)
        self.markers_entry.delete(0, tk.END)
        self.markers_entry.insert(0, directory)
        pass


    def load_data(self):
        """Loading data from files, processing it (markers,keys, date) if selected.Results are saved in new files.
        Requires name of name colum for keywords, language in format - russian - for them and file or dir to load
        original data"""
        directory = self.directory_entry.get()
        read_xlsx = self.read_xlsx_var.get()
        find_keywords_var = self.find_keywords_var.get()
        selection = self.selection_entry.get().split(";")
        name_colum = self.name_colum_entry.get()
        filter_col = self.filter_col_entry.get()
        sort_type = self.sel_type_var.get()

        if self.markers_entry.get() == '':
            markers = None
        else:
            markers = self.markers_entry.get()[1:-1]
            name_colum = self.name_colum_entry.get()
        filepath = None
        if len(selection) != 2:
            selection = None
        else:
            selection = (selection[0], selection[1])
        set_dates = self.set_dates_var.get()
        if self.dir_file_var.get() != 'Dir':
            filepath = directory[1:-1]
            directory = None
            finalname = os.path.dirname(filepath)
        else:
            finalname = directory
        if not os.path.exists(os.path.normpath((finalname + '\\result'))):
            os.makedirs(finalname + '\\result')
        dl = Data_loading()
        data = dl.get_data(directory=directory, read_xlsx=read_xlsx, selection=selection,
                           set_dates=set_dates, filepath=filepath)
        dp = Data_process()
        dp.use_script(temp_frame=data, read_xlsx=read_xlsx, markers_file=markers, column=name_colum,
                      set_dates=set_dates, filepath=filepath,
                      finalname=os.path.normpath(finalname + '\\result\\final1'),
                      filter_col=filter_col,values=selection,sort_type=sort_type)
        if find_keywords_var:
            language = self.language_entry.get()
            fk = Find_keywords(language=language)
            fk.use(name_colum=name_colum, need_normalization=False, n_grams=1,
                   temp_frame=data, output_file=os.path.normpath(finalname + '\\result\\keywords1.xlsx'))
            fk.use(name_colum=name_colum, need_normalization=False, n_grams=3,
                   temp_frame=data, output_file=os.path.normpath(finalname + '\\result\\keywords3.xlsx'))


root = tk.Tk()
root.title("Data Processing App")
root.geometry("550x150")
root.resizable(False, False)
root.columnconfigure(3, minsize=50, weight=1)
root.columnconfigure(1, minsize=50, weight=1)

app = App(master=root)
app.mainloop()