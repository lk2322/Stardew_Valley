import pygame as pg
from settings import *
import shop
import random
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        game.all_sprites.change_layer(self, PLAYER_LAYER)
        self.game = game
        # Animation
        self.__speed = 0.01
        self.__started = False
        self.__counter = 0
        self._state = 'down'
        self._index = 0
        self.blocked = False

        self.images = game.player_imgs
        self.image = self.images[self._state][0]
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(x, y)

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if not self.blocked:
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                self.vel.x = -PLAYER_SPEED
                self._state = 'left'
                self.__started = True
            if keys[pg.K_RIGHT] or keys[pg.K_d]:
                self.vel.x = PLAYER_SPEED
                self._state = 'right'
                self.__started = True
            if keys[pg.K_UP] or keys[pg.K_w]:
                self.vel.y = -PLAYER_SPEED
                self._state = 'up'
                self.__started = True
            if keys[pg.K_DOWN] or keys[pg.K_s]:
                self.vel.y = PLAYER_SPEED
                self._state = 'down'
                self.__started = True
            if self.vel.x != 0 and self.vel.y != 0:
                self.vel *= 0.7071
            if self.vel.x == 0 and self.vel.y == 0:
                self.__started = False
            if self.vel.x != 0 or self.vel.y != 0:
                if not self.game.step.get_busy():
                    self.game.step.play(self.game.step_snd)

    def collide_with_triggers(self):
        hits = pg.sprite.spritecollide(self, self.game.triggers, False)
        for hit in hits:
            hit.triggered()

    def collide_with_walls(self, dir_p):
        if dir_p == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
        if dir_p == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y

    def update(self):
        self.get_keys()
        self.pos += self.vel * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        if self.__started:
            self.__counter += self.__counter + 1 * self.__speed
            if self.__counter >= 1:
                self._index = (self._index + 1) % len(self.images)
                self.__counter = 0
                self.image = self.images[self._state][self._index]
        else:
            self._index = 0
            self.image = self.images[self._state][self._index]
        self.collide_with_triggers()


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = None
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class BaseTrigger(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.all_sprites, game.triggers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = None
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

    def triggered(self):
        pass


class Home_Trigger(BaseTrigger):
    def triggered(self):
        self.game.next_day()
        self.game.player.pos.y += 60


class Shop_Trigger(BaseTrigger):
    def triggered(self):
        shop.Shop(self.game)
        self.game.player.pos.y += 60


class Home(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        game.all_sprites.change_layer(self, HOME_LAYER)
        self.game = game
        self.image = game.home_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Cell(pg.sprite.Sprite):
    def __init__(self, game, x, y, image, *additional_groups):
        self.groups = [game.all_sprites]
        self.groups.extend(additional_groups)
        self.type = None
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.day = self.game.day
        self.image = image
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if self.type == 'arabale_wet':
            if self.day != self.game.day:
                self.type = 'arabale_dry'
                self.image = self.game.arable_land
        self.day = self.game.day


class Allow_or_Deny_cell(pg.sprite.Sprite):
    def __init__(self, game, x, y, image, *additional_groups):
        self.groups = [game.all_sprites]
        self.groups.extend(additional_groups)
        pg.sprite.Sprite.__init__(self, self.groups)
        game.all_sprites.change_layer(self, HIGHLIGHTING_LAYER)
        self.game = game
        self.image = image
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

    def update(self):
        x = self.game.mouse_pos_on_map[0]
        y = self.game.mouse_pos_on_map[1]
        x1, y1 = self.rect.topleft
        x3, y3 = self.rect.bottomright
        if not (x > x1 and y > y1 and x < x3 and y < y3):
            self.kill()


class Crop(pg.sprite.Sprite):
    def __init__(self, game, x, y, images: dict, c_day, price, name):
        self.groups = game.all_sprites, game.crops
        pg.sprite.Sprite.__init__(self, self.groups)
        game.all_sprites.change_layer(self, CROPS_LAYER)
        self.price = price
        self.game = game
        self.p_day = c_day
        self.c_day = c_day
        self.images = images
        self.image = self.images[0]
        self.name = name
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.gather = False

    def next_day(self):
        if self.game.day - self.p_day >= 1:
            if self.game.all_sprites.get_sprites_at((self.x, self.y))[0].type != 'arabale_wet':
                if random.randint(0, 1):
                    self.kill()
                return
            else:
                self.p_day = self.game.day
            if self.images.get(self.game.day - self.c_day):
                self.image = self.images.get(self.game.day - self.c_day)
            if max(self.images) <= self.game.day - self.c_day:
                self.gather = True
