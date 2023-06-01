import pygame as pg
from PIL import Image
import numpy as np
import cv2 as cv
from collections import defaultdict
from settings import *

_ = False
mini_map = [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 2],
    [1, _, _, 2, 2, 2, 2, _, _, _, 2, 2, 2, _, _, 1],
    [2, _, _, _, _, _, 2, _, _, _, 2, _, 2, _, _, 2],
    [2, _, _, _, _, _, 2, _, _, _, 2, _, 2, _, _, 1],
    [1, _, _, 2, 2, 2, 2, _, _, _, _, _, _, _, _, 2],
    [2, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 2],
    [2, _, _, _, 1, _, _, _, 2, _, _, _, _, _, _, 2],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, _, _, 2, 1, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, _, _, 2, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, _, _, 2, 1, 1, 1],
    [1, 1, 3, 1, 1, 1, 1, 1, 1, 2, _, _, 2, 1, 1, 1],
    [1, 4, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, _, _, 2, _, _, _, _, _, 3, 4, _, 4, 3, _, 1],
    [1, _, _, 5, _, _, _, _, _, _, 3, _, 3, _, _, 1],
    [1, _, _, 2, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, 4, _, _, _, _, _, _, 4, _, _, 4, _, _, _, 1],
    [1, 1, 3, 3, _, _, 3, 3, 1, 3, 3, 1, 3, 1, 1, 1],
    [1, 1, 1, 3, _, _, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 3, 4, _, _, 4, 3, 3, 3, 3, 3, 3, 3, 3, 1],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, 5, _, _, _, 5, _, _, _, 5, _, _, _, 3],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]


class Map:
    def __init__(self, game):
        self.game = game
        self.mini_map = mini_map
        self.world_map = {}
        self.test_map = {}
        self.rows = len(self.mini_map)
        self.cols = len(self.mini_map[0])
        self.spawnX = 0
        self.spawnY = 0
        #self.get_map()
        self.get_map_from_image()

    def get_map(self):
        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i, j)] = value

    
    def get_map_from_image(self, path = 'maps/test2.png'):
        im = Image.open(path, 'r')
        im = im.convert('RGB')

        width, height = im.size
        self.rows = width
        self.cols = height

        for y in range(height):
            for x in range(width):
                pixel = im.getpixel((x, y))
                value = COLOR_TO_TEXTURE.get(pixel, False) 
                if value and value != "spawn":
                    self.world_map[(x,y)] = value
                
                if value == "spawn":
                    self.spawnX = x
                    self.spawnY = y
        
    def draw(self):
        tile_size = 10  # Adjust the tile size according to your needs
        floor_color = (0, 0, 255)  # Color for the first tier
        wall_color = (255, 0, 0)   # Color for the second tier

        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                if value:
                    x = i * tile_size
                    y = j * tile_size
                    rect = (x, y, tile_size, tile_size)
                    pg.draw.rect(self.game.screen, floor_color, rect)

                    if value == 2:
                        rect = (x, y - tile_size, tile_size, tile_size)
                        pg.draw.rect(self.game.screen, wall_color, rect)

      