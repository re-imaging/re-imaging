#!/usr/bin/env python
# coding: utf-8

import os
from tkinter import *
from PIL import ImageTk, Image
import time
import argparse

parser = argparse.ArgumentParser(description='Tool for labelling images by moving them into folders')

parser.add_argument('--verbose', action='store_true', help='verbose output')
parser.add_argument('--targetpath', help='set a target folder of images to operate on')

global args
args = parser.parse_args()

global targetpath
if args.targetpath is not None:
    targetpath = args.targetpath
else:
    # targetpath = "/home/rte/data/images/random/seq/0-100k/"
    targetpath = 'data/'

# create required directories
diagram_path = targetpath + "diagram/"
sensor_path = targetpath + "sensor/"
unsure_path = targetpath + "unsure/"

print("Image Labelling Tool")
print("Press left key for diagram, down for unsure, right for sensor, up for undo")
print("The Return key prints the totals")

class gui:
    def __init__(self, master):

        self.start = time.time()

        self.counter = 0

        self.master = master
        master.title("Image Labeling Tool")

        self.label = Label(master, text="Press left key for diagram, down for unsure, right for sensor, up for undo")
        self.label.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

        self.filepaths = self.init_images()

        self.test_image = Label(master)
        self.test_image.pack()

        self.show_next_image()

    def returnKey(self, e):
        now_time = time.time()
        print("running for:",now_time-self.start)
        print("counter:",self.counter)
        return

    def leftKey(self, e):
        print("moving image to diagram")
        f = self.filepaths[self.counter]
        print("rename:",targetpath + f)
        print("to:",diagram_path + f)
        os.rename(targetpath + f, diagram_path + f)
        self.counter += 1
        self.show_next_image()
        return
    def rightKey(self, e):
        print("moving image to sensor")
        f = self.filepaths[self.counter]
        os.rename(targetpath + f, sensor_path + f)
        self.counter += 1
        self.show_next_image()
        return
    def downKey(self, e):
        print("moving image to unsure")
        f = self.filepaths[self.counter]
        os.rename(targetpath + f, unsure_path + f)
        self.counter += 1
        self.show_next_image()
        return

    def undo(self, e):
        print("counter:",self.counter)
        if self.counter > 0:
            self.counter -= 1
        print("counter:",self.counter)
        # search for previous image
        last_filename = self.filepaths[self.counter]
        print("last_filename:",last_filename)
        for path in [diagram_path, sensor_path, unsure_path]:
            for root, dirs, files in os.walk(path):
                if last_filename in files:
                    last_file = os.path.join(root, last_filename)
                    print("last_file")
                    os.rename(last_file, targetpath + last_filename)
                    print("rename:",last_file, targetpath + last_filename)
        self.show_next_image()
        return

    def show_next_image(self):
        print(targetpath + self.filepaths[self.counter])
        im = Image.open(targetpath + self.filepaths[self.counter])
        photo = ImageTk.PhotoImage(im)

        self.test_image.configure(image=photo)
        self.test_image.image = photo
        return

    def init_images(self):
        filepaths = [f for f in os.listdir(targetpath) if os.path.isfile(os.path.join(targetpath, f))]
        print(len(filepaths))

        if os.path.isdir(diagram_path) is False:
            os.mkdir(diagram_path)
        if os.path.isdir(sensor_path) is False:
            os.mkdir(sensor_path)
        if os.path.isdir(unsure_path) is False:
            os.mkdir(unsure_path)
        return filepaths

def main():
    root = Tk()
    my_gui = gui(root)
    root.bind("<Return>", my_gui.returnKey)
    root.bind("<Left>", my_gui.leftKey)
    root.bind("<Down>", my_gui.downKey)
    root.bind("<Right>", my_gui.rightKey)
    root.bind("<Up>", my_gui.undo)
    root.mainloop()

if __name__ == '__main__':
    main()
