#!/bin/env python3
from tkinter import *
from tkinter import filedialog

from PIL import Image, ImageFilter, ImageTk, ImageOps
from pluspluslib import *

if __name__ == "__main__":
    global FinalImage
    global input_img_filename
    global nb_pp_needed
    global current_palette
    global color_selected
    global grid_checked
    global canvas_image
    global final_PIL_image
    global final_PIL_image_grid
    global factor
    global output_image

    factor = 1.0
    canvas_image = None
    current_palette = pp_palette
    color_selected = list()
    grid_checked = 0
    input_img_filename = ""

    def open():
        global final_image
        global final_PIL_image
        global input_img_filename
        global canvas_image
        global factor
        input_img_filename = filedialog.askopenfilename(initialdir="/Desktop", title="Ouvrir une image")
        image_opened = Image.open(input_img_filename)
        final_image = ImageTk.PhotoImage(image_opened)
        if canvas_image == None:
            canvas_image = PictureCanvas.create_image(0, 0, image=final_image, anchor=NW)
        else:
            PictureCanvas.itemconfig(canvas_image, image = final_image)
        final_PIL_image = image_opened
        factor = 1.0
        DetailsSlider.set(0)


    def process(event=None):
        global input_img_filename
        global final_image
        global output_image
        global final_PIL_image
        global final_PIL_image_grid
        global current_palette
        global canvas_image
        global factor
        global grid_checked

        if input_img_filename == "":
            return

        pp_image, pp_image_grid, nb_pp = plusplusize_image(input_img_filename, pp_palette_in=current_palette, details=DetailsSlider.get()/100)

        w, h = pp_image.size
        pp_image_resized = pp_image.resize((int(w*factor), int(h*factor)))

        pp_image_resized_grid_nozoom = pp_image_grid.resize((int(w*factor), int(h*factor)))
        pp_image_resized_grid = pp_image_resized_grid_nozoom.filter(ImageFilter.FIND_EDGES)
        pp_image_resized_grid = ImageOps.invert(pp_image_resized_grid)

        merged_image = pp_image_resized.copy()
        if grid_checked.get() == 1:
            merged_image.putalpha(pp_image_resized_grid.convert('L'))
        final_image = ImageTk.PhotoImage(merged_image)
        output_image = merged_image

        final_PIL_image = pp_image
        final_PIL_image_grid = pp_image_resized_grid_nozoom
        PictureCanvas.itemconfig(canvas_image, image = final_image)
        nb_pp_needed.set(str(nb_pp) + " PlusPlus needed")

    win = Tk()
    win.title("Plusplusize")

    PictureFrame = Frame(win)
    PictureCanvas = Canvas(PictureFrame)
    PictureCanvas.pack(fill="both", expand=True)
    PictureFrame.pack(side=LEFT, fill="both", expand=True, anchor=NW)

    def do_zoom_key(event):
        global final_PIL_image
        global final_PIL_image_grid
        global final_image
        global output_image
        global factor
        global grid_checked

        zoom_increment = 0.1
        if event.char == '+':
            factor = factor + zoom_increment
        elif event.char == '-':
            factor = max(0.0, factor - zoom_increment)

        w, h = final_PIL_image.size
        final_PIL_image_resized = final_PIL_image.resize((int(w*factor), int(h*factor)))

        image_resized_grid = final_PIL_image_grid.filter(ImageFilter.FIND_EDGES)
        image_resized_grid = ImageOps.invert(image_resized_grid)
        merged_image = final_PIL_image_resized.copy()
        if grid_checked.get() == 1:
            merged_image.putalpha(image_resized_grid.resize((int(w*factor), int(h*factor))).convert('L'))
        final_image = ImageTk.PhotoImage(merged_image)
        output_image = merged_image
        PictureCanvas.itemconfig(canvas_image, image=final_image)

    def mouse_click(event):
        PictureCanvas.scan_mark(event.x, event.y)
        PictureCanvas.focus_set()

    PictureCanvas.bind("<Key>", do_zoom_key)
    PictureCanvas.bind('<ButtonPress-1>', mouse_click)
    PictureCanvas.bind("<B1-Motion>", lambda event: PictureCanvas.scan_dragto(event.x, event.y, gain=1))

    #Settings
    SettingsFrame = Frame(win, highlightthickness=1, highlightbackground="black")
    lbl = Label(SettingsFrame, text="Settings")
    lbl.grid(row=0, column=0)

    DetailsSlider = Scale(SettingsFrame, from_=0, to=100, command=process, orient=HORIZONTAL, label="Details")
    DetailsSlider.grid(row=1, column=0, sticky=W+N)

    def toggle_color():
        global current_palette
        global color_selected
        current_palette = list()
        for idx in range(0,int(len(pp_palette)/3)):
            if color_selected[idx].get() == 1:
                current_palette.extend([pp_palette[idx*3], pp_palette[idx*3+1], pp_palette[idx*3+2]])
        current_palette = tuple(current_palette)

        process(None)

    def export():
        global output_image
        fname = filedialog.asksaveasfilename(defaultextension=".png")
        if fname is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        output_image.save(fname)

    #Palette
    PaletteFrame = Frame(SettingsFrame)
    PaletteFrame.grid(row=2, column=0,sticky=W+N)
    lbl = Label(PaletteFrame, text="Color Palette")
    lbl.grid(row=0, column=1)
    for idx in range(0, int(len(pp_palette)/3)):
        ColorFrame = Frame(PaletteFrame)
        lbl = Label(ColorFrame, bg="#%02x%02x%02x" % (pp_palette[idx*3], pp_palette[idx*3+1], pp_palette[idx*3+2]), text=" ")
        lbl.grid(row=0, column=0, sticky='')
        color_selected.append(IntVar(value=1))
        btn = Checkbutton(ColorFrame, variable=color_selected[-1], command=toggle_color)
        btn.grid(row=1, column=0, sticky='')
        ColorFrame.grid(row=int(idx/3)+1, column=idx%3, sticky='')

    GridCheckBoxFrame = Frame(SettingsFrame)
    GridCheckBoxFrame.grid(row=3, column=0, sticky=W+N)
    grid_checked = IntVar(value=0)
    btn = Checkbutton(GridCheckBoxFrame, variable=grid_checked, command=process)
    btn.grid(row=0, column=0)
    lbl = Label(GridCheckBoxFrame, text="grid overlay")
    lbl.grid(row=0, column=1)

    #Result
    nb_pp_needed = StringVar()
    NbPPNeeded = Label(SettingsFrame, textvariable=nb_pp_needed)
    nb_pp_needed.set("0 PlusPlus needed")
    NbPPNeeded.grid(row=4, column=0, sticky=W+N)

    SettingsFrame.pack(side=RIGHT, anchor=NW)

    WinMenu = Menu(win)
    FileMenu = Menu(WinMenu, tearoff=0)
    FileMenu.add_command(label="Open", command=open)
    FileMenu.add_command(label="Export", command=export)
    WinMenu.add_cascade(label="File", menu=FileMenu)

    win.config(menu=WinMenu)
    win.mainloop()
