#!/bin/env python3
from collections import Counter
from PIL import Image

horizontal_pp_pattern = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (1, -1), (3, -1), (1, 1), (3, 1)]
vertical_pp_pattern = [(0, 0), (-1, -1), (0, -1), (1, -1), (0, -2), (0, 1), (1, 1), (-1, 1), (0, 2)]
pp_palette = (228, 231, 226,  # white
              240, 230, 0,  # basic yellow
              240, 100, 0,  # basic orange
              200, 0, 0,  # basic red
              80, 0, 120,  # basic purple
              50, 50, 150,  # basic blue
              0, 145, 75,  # basic green
              150, 150, 150,  # basic grey
              100, 60, 50,  # basic brown
              35, 35, 35,  # basic black
              230, 190, 165,  # basic peach
              255, 0, 100,  # neon pink
              65, 0, 190,  # neon blue
              0, 175, 50,  # neon green
              225, 255, 0,  # neon yellow
              255, 83, 44,  # neon orange
              215, 215, 215,  # neon transparent
              240, 235, 80,  # pastel yellow
              160, 120, 210,  # pastel purple
              150, 190, 230,  # pastel blue
              180, 240, 135,  # pastel green
              245, 110, 175,  # pastel pink
              )

def plusplusize_image(filename, pp_palette_in=pp_palette, details=0.25):

    #Read image
    image_in = Image.open(filename)
    image_in_copy = image_in.copy()

    #Display image
    w, h = image_in.size
    w_org = w
    h_org = h

    nb_pp_width = (w/3) * details

    # Put image in portrait mode
    rotated = False
    if max(w,h) == h:
        image_in = image_in.rotate(90, expand=True)
        w, h = image_in.size
        rotated = True
    nb_pp_height = int(nb_pp_width * h / w)

    w_output_image = max(int(nb_pp_width / 2) * 6 + 1 + (nb_pp_width % 2) * 4, int(nb_pp_width / 2) * 6 + 1 + 1 + (nb_pp_width % 2) * 2)
    h_output_image = max(int(nb_pp_height / 2) * 6 + 1 + 1 + (nb_pp_height % 2) * 2, int(nb_pp_height / 2) * 6 + 1 + (nb_pp_height % 2) * 4)

    #Applying a filter to the image
    image_in.thumbnail((w_output_image, h_output_image))

    pal_image= Image.new("P", (1,1))
    #pp_palette = (0,0,0, 255,0,0, 0,255,0, 0,0,255, 255,255,255, 255,255,0, 0,255,255, 255,0,255)
    pp_palette = pp_palette_in + (0,0,0)*(256-int(len(pp_palette_in)/3))
    pal_image.putpalette( pp_palette )
    image_in = image_in._new(image_in.im.convert("P", 0, pal_image.im))

    pxl_in = image_in.load()
    w, h = image_in.size

    nb_pp_width = min(int((w - 1) / 6) + int((w + 1) / 6), int((w - 2) / 6) + int((w + 2) / 6))
    nb_pp_height = min(int((h + 2) / 6) + int((h - 2) / 6), int((h + 1) / 6) + int((h - 1) / 6))

    w_output_image = max(int(nb_pp_width / 2) * 6 + 1 + (nb_pp_width % 2) * 4, int(nb_pp_width / 2) * 6 + 1 + 1 + (nb_pp_width % 2) * 2)
    h_output_image = max(int(nb_pp_height / 2) * 6 + 1 + 1 + (nb_pp_height % 2) * 2, int(nb_pp_height / 2) * 6 + 1 + (nb_pp_height % 2) * 4)

    image_out = Image.new('RGB', (w_output_image, h_output_image), color=(255, 255, 255))
    pxl_out = image_out.load()
    image_out_grid = Image.new('RGB', (w_output_image, h_output_image), color=(255, 255, 255))
    pxl_out_grid = image_out_grid.load()

    i2 = 2
    j2 = 0
    horizontal = True
    previous_start_horizontal = False
    for i in range(0, nb_pp_height):
        for j in range(0, nb_pp_width):
            if j == 0:
                if previous_start_horizontal:
                    previous_start_horizontal = False
                    horizontal = False
                    j2 = 2
                else:
                    previous_start_horizontal = True
                    horizontal = True
                    j2 = 0

            freq_c = []

            if horizontal:
                for p in horizontal_pp_pattern:
                    freq_c.append(pxl_in[(j2 + p[0], i2 + p[1])])

                color_index = sorted(freq_c, key=Counter(freq_c).get, reverse=True)[0]

                for p in horizontal_pp_pattern:
                    pxl_out[(j2 + p[0], i2 + p[1])] = tuple(pp_palette[color_index*3:color_index*3+3])
                    pxl_out_grid[(j2 + p[0], i2 + p[1])] = (0, 0, 0)

                j2 += 5
                horizontal = False
            else:
                for p in vertical_pp_pattern:
                    freq_c.append(pxl_in[(j2 + p[0], i2 + p[1])])

                color_index = sorted(freq_c, key=Counter(freq_c).get, reverse=True)[0]

                for p in vertical_pp_pattern:
                    pxl_out[(j2 + p[0], i2 + p[1])] = tuple(pp_palette[color_index*3:color_index*3+3])
                    pxl_out_grid[(j2 + p[0], i2 + p[1])] = (255, 255, 255)

                j2 += 1
                horizontal = True
        i2 += 3

    image_out = image_out.resize((w_org, h_org), resample=Image.NEAREST)
    image_out_grid = image_out_grid.resize((w_org, h_org), resample=Image.NEAREST)

    image_out = image_out.convert(mode="RGB")
    image_out_grid = image_out_grid.convert(mode="RGB")

    if rotated:
        image_out = image_out.rotate(-90, expand=True)
        image_out_grid = image_out_grid.rotate(-90, expand=True)

    if details == 0.0:
        image_out = image_in_copy

    return image_out, image_out_grid, nb_pp_width*nb_pp_height
