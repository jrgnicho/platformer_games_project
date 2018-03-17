#!/usr/bin/env python
import Tkinter as tk
from PIL import Image
import ImageTk
import pygame
import os

sw, sh = 200, 100

# load image in pygame
pygame.init()
surf = pygame.Surface((sw,sh))

# draw on surface
surf.fill(pygame.Color(0,0,0))
pygame.draw.circle(surf, pygame.Color(255,255,100), (sw/2,sh/2), 30)

# export as string / import to PIL
image_str = pygame.image.tostring(surf, 'RGBA')         # use 'RGB' to export
w, h      = surf.get_rect()[2:]
image     = Image.frombuffer('RGBA', (w, h), image_str,'raw','RGBA',0,1) # use 'RGB' to import

# create Tk window/widgets
root         = tk.Tk()

# Tk canvas
tkimage      = ImageTk.PhotoImage(image,(w,h)) # use ImageTk.PhotoImage class instead
canvas       = tk.Canvas(root)
canvas.create_image(w/2, h/2, image=tkimage)
#canvas.width = w
#canvas.height = h
canvas.pack(fill=tk.BOTH)

# create Tk button
text = tk.Button(root, text='Click')
text.pack()


root.mainloop()