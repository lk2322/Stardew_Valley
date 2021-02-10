import pygame as pg
from settings import *
import pytmx
from sprites import *


class Camera:
    def __init__(self, w: int, h: int, game):
        self.camera = pg.Rect(0, 0, w, h)
        self.w = w
        self.h = h
        self.game = game
        self.y = 0
        self.x = 0

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        self.x = -target.rect.centerx + int(WIDTH / 2)
        self.y = -target.rect.centery + int(HEIGHT / 2)
        self.x = min(0, self.x)  # left
        self.y = min(0, self.y)  # top
        self.x = max(-(self.w - WIDTH), self.x)  # right
        self.y = max(-(self.h - HEIGHT), self.y)  # bottom
        self.camera = pg.Rect(self.x, self.y, self.w, self.h)


class TileMap:
    def __init__(self, filename, game):
        tm = pytmx.load_pygame(filename)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm
        self.game = game

    def render(self):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        if layer.name == 'earth':
                            Cell(self.game, x*self.tmxdata.tilewidth, y *
                                 self.tmxdata.tileheight, tile, self.game.earth)
                            continue
                        Cell(self.game, x*self.tmxdata.tilewidth,
                             y*self.tmxdata.tileheight, tile)
        for tile_object in self.tmxdata.objects:
            if tile_object.name == 'wall':
                Obstacle(self.game, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name == 'home_sp':
                Home(self.game, tile_object.x, tile_object.y)
            if tile_object.name == 'home_trigger':
                Home_Trigger(self.game, tile_object.x, tile_object.y,
                             tile_object.width, tile_object.height)
            if tile_object.name == 'shop_trigger':
                Shop_Trigger(self.game, tile_object.x, tile_object.y,
                             tile_object.width, tile_object.height)


class Crops_group(pg.sprite.Group):
    def next_day(self):
        for i in self.sprites():
            i.next_day()
