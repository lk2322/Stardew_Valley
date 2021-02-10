import pygame as pg
from core import Camera, TileMap, Crops_group
from settings import *
from sprites import Player, Obstacle, Home, Allow_or_Deny_cell, Crop
from assortment import assortment
import pickle
import shop
import random
import crops
import os
import gui
import math


def load_data_ui():
    path = r'assets\farm\resized\inv_ui'
    files = []
    for filename in os.listdir(path):
        image = pg.image.load(os.path.join(path, filename)).convert_alpha()
        image = pg.transform.scale(image, (600, 75))
        files.append(image)
    return files


def load_player_anim() -> dict:
    path = r'assets\farm\resized\player'
    anim = {}
    for folder in os.listdir(path):
        anim[folder] = []
        path2 = os.path.join(path, folder)
        for filename in os.listdir(path2):
            anim[folder].append(pg.image.load(
                os.path.join(path2, filename)).convert_alpha())
    return anim


def check_len(pos, player) -> bool:
    leng = math.sqrt(
        ((player.rect.centerx - pos[0])**2) +
        ((player.rect.centery - pos[1])**2)
    )
    if leng > LEN_LIMIT:
        return True
    return False


class Game:
    def __init__(self, name: str = 'Farm', w: int = 1920, h: int = 1080, fps: int = 30):
        pg.init()
        self.screen = pg.display.set_mode((w, h))
        pg.display.set_caption(name)
        self.clock = pg.time.Clock()
        self.fps = fps
        self.load_data()
        self.new()
        self.run()

    def load_data(self):
        self.player_imgs = load_player_anim()
        self.home_img = pg.image.load(r'assets\farm\resized\farm_home.png').convert_alpha()
        self.arable_land = pg.image.load(r'assets\farm\resized\arable.png').convert_alpha()
        self.arable_land_w = pg.image.load(r'assets\farm\resized\arable_w.png').convert_alpha()
        self.inv_UI = load_data_ui()
        self.a_image = pg.image.load(r'assets\farm\resized\allow.png').convert_alpha()
        self.d_image = pg.image.load(r'assets\farm\resized\deny.png').convert_alpha()
        self.sleeping_box = pg.image.load(
            r'assets\farm\resized\sleeping_box.png').convert_alpha()
        # TODO убрать это
        self.hoe = pg.image.load(r'assets\farm\resized\Tools\hoe.png').convert_alpha()
        self.hoe = pg.transform.scale(self.hoe, (40, 35))
        self.boil = pg.image.load(r'assets\farm\resized\Tools\bailer.png').convert_alpha()
        self.boil = pg.transform.scale(self.boil, (40, 35))

        self.shop_close_btn = pg.image.load(r'assets\farm\resized\shop\close_btn.png').convert_alpha()
        self.shop_bg = pg.image.load(r'assets\farm\resized\shop\shop_bg.png').convert_alpha()
        self.shop_item = pg.image.load(r'assets\farm\resized\shop\item.png').convert_alpha()
        self.shop_sell = pg.image.load(r'assets\farm\resized\shop\textBox.png').convert_alpha()

        self.balance_ui = pg.image.load(r'assets\farm\resized\balance.png').convert_alpha()
        # sounds
        self.step = pg.mixer.Channel(2)
        pg.mixer.music.load(r'assets\farm\sounds\summer_day.wav')
        pg.mixer.music.play(-1)

        self.sell_snd = pg.mixer.Sound(r'assets\farm\sounds\sell.wav')
        self.step_snd = pg.mixer.Sound(r'assets\farm\sounds\sandyStep.wav')
        self.step_snd.set_volume(0.3)

        self.button_snd = pg.mixer.Sound(r'assets\farm\sounds\button1.wav')
        self.night_snd = pg.mixer.Sound(r'assets\farm\sounds\night_time.wav')
        self.water_snd = [pg.mixer.Sound(r'assets\farm\sounds\water_lap1.wav'), pg.mixer.Sound(
            r'assets\farm\sounds\water_lap2.wav'), pg.mixer.Sound(r'assets\farm\sounds\water_lap3.wav')]
        self.seeds_snd = pg.mixer.Sound(r'assets\farm\sounds\seeds.wav')
        self.seeds_snd.set_volume(0.05)
        self.harvest_snd = pg.mixer.Sound(r'assets\farm\sounds\harvest.wav')
        self.harvest_snd.set_volume(0.1)

    def new(self):
        self.ui = pg.sprite.LayeredUpdates()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.earth = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.crops = Crops_group()
        self.triggers = pg.sprite.Group()
        self.day = 0
        self.balance = 500
        self.map = TileMap('map1.tmx', self)
        self.map.render()
        self.map_rect = self.screen.get_rect()
        self.load_data()
        self.player = Player(self, 500, 300)
        self.hud_inv = gui.Inv_UI(self)
        self.balance_gui = gui.Balance_ui(self)
        self.hud_inv.add_item(
            gui.Item(self.hud_inv, self.hoe.copy(), 'hoe', 1, False))
        self.hud_inv.add_item(
            gui.Item(self.hud_inv, self.boil.copy(), 'bailer', 1, False))
        self.camera = Camera(self.map.width, self.map.height, self)

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(self.fps) / 1000
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()
        self.ui.update()
        self.camera.update(self.player)
        ms_pos = pg.mouse.get_pos()
        pos = (ms_pos[0] - self.camera.x,
               ms_pos[1] - self.camera.y)
        self.mouse_pos_on_map = pos
        sprite = self.all_sprites.get_sprites_at(pos)
        if sprite and not self.player.blocked:
            if not any(isinstance(x, Allow_or_Deny_cell) for x in sprite):
                if self.earth not in sprite[0].groups or check_len(pos, self.player):
                    Allow_or_Deny_cell(
                        self, sprite[0].x, sprite[0].y, self.d_image)
                else:
                    Allow_or_Deny_cell(
                        self, sprite[0].x, sprite[0].y, self.a_image)

    def draw(self):
        self.screen.fill((0, 0, 0))
        pg.display.set_caption("{:.0f}  Day: {}".format(
            self.clock.get_fps(), self.day))
        self.screen.blit(self.screen, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            if sprite.image:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
        # UI
        for sprite in self.ui:
            self.screen.blit(sprite.image, sprite.rect)
        pg.display.flip()

    def next_day(self):
        self.day += 1
        gui.Sleeping_box(self)
        self.crops.next_day()

    def on_click(self, event):
        if event.button == 1:
            pos = (event.pos[0] - self.camera.x,
                   event.pos[1] - self.camera.y)
            sprites = self.all_sprites.get_sprites_at(pos)
            for sprite in sprites:
                if isinstance(sprite, Player):
                    continue
                if self.hud_inv.current_item:
                    if self.earth.has(sprite) and (not check_len(pos, self.player)) and \
                            self.hud_inv.current_item.type == 'hoe':
                        sprite.image = self.arable_land
                        sprite.type = 'arabale_dry'
                    if self.earth.has(sprite) and (not check_len(pos, self.player)) and \
                            self.hud_inv.current_item.type == 'bailer' and sprite.type == 'arabale_dry':
                        sprite.image = self.arable_land_w
                        sprite.type = 'arabale_wet'
                        random.choice(self.water_snd).play()
                    if not any(isinstance(x, Crop) for x in sprites):
                        if self.earth.has(sprite) and (not check_len(pos, self.player)) and \
                                self.hud_inv.current_item.type == 'seed' and \
                                (sprite.type == 'arabale_dry' or sprite.type == 'arabale_wet'):
                            crop = assortment[self.hud_inv.current_item.name]
                            Crop(self, sprite.x,
                                 sprite.y, crop[0], self.day, crop[2], self.hud_inv.current_item.name)
                            self.seeds_snd.play()
                            self.hud_inv.current_item.del_col()
                if isinstance(sprite, Crop):
                    if sprite.gather:
                        self.hud_inv.add_item(
                            gui.Item(self.hud_inv, sprite.image.copy(), 'finished_product', 1, True, \
                                     price=sprite.price, item_name=sprite.name))
                        sprite.kill()
                        self.harvest_snd.play()
            pos = event.pos
            ui = self.ui.get_sprites_at(pos)
            for sprite in ui:
                if isinstance(sprite, shop.Shop_ui_exit) or isinstance(sprite, shop.Shop_ui_item) \
                        or isinstance(sprite, shop.Shop_ui_sell):
                    sprite.trigger()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
            if event.type == pg.KEYDOWN:
                self.hud_inv.check_num_inv(event)
            if event.type == pg.MOUSEBUTTONDOWN:
                self.on_click(event)
            # Движение игрока обрабатываются в sprites.Player


if __name__ == '__main__':
    Game(w=WIDTH, h=HEIGHT, fps=60)
