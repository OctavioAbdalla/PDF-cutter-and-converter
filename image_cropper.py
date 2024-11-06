import tkinter as tk
from tkinter import filedialog
from image_reader import ImageReader
from create_xlsx_file import Create_Xslx_File
from pdf_to_image import PDFConverter
from PIL import ImageTk
import os

class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")
        self.root.geometry("900x800")

        self.handle_size = 8
        self.image = None
        self.file_name = None
        self.cropped_image = None
        self.rect = None
        self.handles = []
        self.on_handler = False
        
        self.image_reader = ImageReader()
        self.create_xlsx_file = Create_Xslx_File()
        self.pdf_to_image = PDFConverter()

        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=tk.YES, fill=tk.BOTH)
        self.canvas = tk.Canvas(self.frame)

        self.scrollbar_vertical = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scrollbar_horizontal = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X) 
        
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.canvas.config(xscrollcommand=self.scrollbar_horizontal.set, yscrollcommand=self.scrollbar_vertical.set)
        
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

        self.toolbar = tk.Frame(self.frame)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.open_button = tk.Button(self.toolbar, text="Open PDF", command=self.open_pdf) 
        self.open_button.pack(side=tk.LEFT)

        self.crop_button = tk.Button(self.toolbar, text="Crop PDF", command=self.crop_pdf)
        self.crop_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.toolbar, text="Process PDF", command=self.process_pdf)
        self.save_button.pack(side=tk.LEFT)

    def open_pdf(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.canvas.delete("all")
            converted_image = self.pdf_to_image.pdf_to_jpg(file_path)
            self.image = converted_image[0]           
            self.file_name = os.path.basename(file_path)
            self.tk_image = ImageTk.PhotoImage(self.image)
            
            self.canvas.config(scrollregion=(0, 0, self.tk_image.width(), self.tk_image.height()))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            
            self.selection_mode()
    
    def on_mousewheel(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")
    
    def selection_mode(self):
        if self.image:
            self.canvas.bind("<ButtonPress-1>", self.on_press)
            self.canvas.bind("<B1-Motion>", self.on_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)
    
    def on_press(self, event):
        x, y = self.get_adjusted_coordinates(event)
        item = self.canvas.find_closest(x, y)[0]
        if item in self.handles:
            self.on_handler = True
            return
        
        self.start_x = x
        self.start_y = y
       
        if self.rect:
            self.canvas.delete(self.rect)        
        
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_drag(self, event):
        if self.on_handler: return  
        x, y = self.get_adjusted_coordinates(event)
        self.end_x = x
        self.end_y = y
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)
        
        self.draw_handles()

    def on_release(self, event):
        x, y = self.get_adjusted_coordinates(event)
        item = self.canvas.find_closest(x, y)[0]
        if item not in self.handles:
            self.end_x = x
            self.end_y = y
    
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)
        self.on_handler = False
        
        if self.handles == []:
            self.draw_handles()
        else:
            self.update_handles_positions()
            
    def get_adjusted_coordinates(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_adjusted = x - self.canvas.winfo_x()
        y_adjusted = y - self.canvas.winfo_y()
        return x_adjusted, y_adjusted  
          
    def draw_handles(self):
        for handle in self.handles:
            self.canvas.delete(handle)
            
        self.handles = []

        handle_size = self.handle_size
        handle = self.canvas.create_rectangle(
            self.start_x - handle_size, self.start_y - handle_size, 
            self.start_x + handle_size, self.start_y + handle_size, 
            outline="red", fill="red"
        )
        self.handles.append(handle)

        handle = self.canvas.create_rectangle(
            self.end_x - handle_size, self.start_y - handle_size,
            self.end_x + handle_size, self.start_y + handle_size,
            outline="red", fill="red"
        )
        self.handles.append(handle)

        handle = self.canvas.create_rectangle(
            self.start_x - handle_size, self.end_y - handle_size,
            self.start_x + handle_size, self.end_y + handle_size,
            outline="red", fill="red"
        )
        self.handles.append(handle)

        handle = self.canvas.create_rectangle(
            self.end_x - handle_size, self.end_y - handle_size,
            self.end_x + handle_size, self.end_y + handle_size,
            outline="red", fill="red"
        )
        self.handles.append(handle)

        for handle in self.handles:
            self.canvas.tag_bind(handle, "<B1-Motion>", lambda event, h=handle: self.on_handle_drag(event, h))

    def on_handle_drag(self, event, handle):
        cur_x, cur_y = self.get_adjusted_coordinates(event)

        if handle == self.handles[0]:
            self.start_x = cur_x
            self.start_y = cur_y
        elif handle == self.handles[1]:
            self.end_x = cur_x
            self.start_y = cur_y
        elif handle == self.handles[2]:
            self.start_x = cur_x
            self.end_y = cur_y
        elif handle == self.handles[3]:
            self.end_x = cur_x
            self.end_y = cur_y
            
        self.update_handles_positions()
        
    def update_handles_positions(self):
        handle_size = self.handle_size
        self.canvas.coords(self.handles[0], self.start_x - handle_size, self.start_y - handle_size, self.start_x + handle_size, self.start_y + handle_size)
        self.canvas.coords(self.handles[1], self.end_x - handle_size, self.start_y - handle_size, self.end_x + handle_size, self.start_y + handle_size)
        self.canvas.coords(self.handles[2], self.start_x - handle_size, self.end_y - handle_size, self.start_x + handle_size, self.end_y + handle_size)
        self.canvas.coords(self.handles[3], self.end_x - handle_size, self.end_y - handle_size, self.end_x + handle_size, self.end_y + handle_size)
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)
        
    def crop_pdf(self):
        x0 = min(self.start_x, self.end_x)
        y0 = min(self.start_y, self.end_y)
        x1 = max(self.start_x, self.end_x)
        y1 = max(self.start_y, self.end_y)

        self.cropped_image = self.image.crop((x0, y0, x1, y1))
        self.cropped_tk_image = ImageTk.PhotoImage(self.cropped_image)
        self.image = self.cropped_image
        
        self.canvas.delete("all")
        
        self.canvas.config(scrollregion=(0, 0, self.cropped_tk_image.width(), self.cropped_tk_image.height()))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.cropped_tk_image)
        
    def process_pdf(self):
        if self.image:
            
            
            images = self.image_reader.split_and_clean_images(self.image)
            texts = self.image_reader.read_images(images)
            self.create_xlsx_file.create_table(texts, self.file_name)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
