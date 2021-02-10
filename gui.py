import pygame as pg
from settings import *


class Inv_UI(pg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.ui
        self.items_group = pg.sprite.Group()
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.images = game.inv_UI
        self.image = self.images[0]
        self.items = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None}
        self.current_item = None
        self.index = 0
        self.rect = self.image.get_rect()
        self.x = (game.screen.get_size()[0] // 2) - (self.rect.size[0] // 2)
        self.y = self.game.screen.get_size()[1] - self.rect.size[1]
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        if self.game.camera.y == 0:
            self.set_bottom()
        if self.game.camera.y == (-(self.game.camera.h - HEIGHT)):
            self.set_top()
        self.items_group.update()

    def add_item(self, item) -> bool:
        for key, i in self.items.items():
            if i:
                if i.type == item.type and i.name == item.name and item.name is not None:
                    i.add_col(item.col)
                    item.kill()
                    return True
        for pos, itm in self.items.items():
            if not itm:
                item.set_pos(pos)
                self.items[pos] = item
                return True
        item.kill()
        return False

    def check_num_inv(self, event):
        keys = [pg.K_1, pg.K_2, pg.K_3, pg.K_4,
                pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9]
        for i in keys:
            if event.key == i:
                self.change_active(keys.index(i) + 1)
                self.current_item = self.items.get(keys.index(i) + 1)
                self.index = keys.index(i) + 1

    def change_active(self, index):
        self.image = self.images[index]

    def set_bottom(self):
        self.y = self.game.screen.get_size()[1] - self.rect.size[1]
        self.rect.y = self.y

    def set_top(self):
        self.y = 0
        self.rect.y = self.y


class Item(pg.sprite.Sprite):
    def __init__(self, inv: Inv_UI, image, item_type: str, col: int, exhaustible: bool, item_name=None, price=0):
        self.groups = inv.items_group, inv.game.ui
        self.image = image
        self.o_image = self.image.copy()
        pg.sprite.Sprite.__init__(self, self.groups)
        self.rect = self.image.get_rect()
        self.col = col
        self.exhaustible = exhaustible
        self.type = item_type
        self.name = item_name
        self.price = price
        self.inv = inv
        self.text_col()

    def set_pos(self, pos: int):
        self.pos = pos

    def update(self):
        self.y = self.inv.y + 25
        self.x = (30 + (self.pos - 1) * 62) + self.inv.x
        self.rect.x = self.x
        self.rect.y = self.y

    def del_col(self):
        if self.exhaustible:
            self.col -= 1
            if self.col <= 0:
                self.del_item()
        self.text_col()

    def del_item(self):
        self.kill()
        self.inv.current_item = None
        self.inv.items[self.pos] = None

    def add_col(self, col):
        if self.exhaustible:
            self.col += col
        self.text_col()

    def text_col(self):
        self.image = self.o_image.copy()
        if self.col != 1:
            font = pg.font.Font(None, 30)
            text = font.render(str(self.col), True, (255, 255, 255))
            pos = (self.image.get_rect(
            ).bottomright[0] - 30, self.image.get_rect().bottomright[1] - 25)
            self.image.blit(text, pos)


class Blackout(pg.sprite.Sprite):
    def __init__(self, size, group):
        self.groups = group
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface(size)
        self.image.set_alpha(200)
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 0
        self.rect.x = self.x
        self.rect.y = self.y


class Sleeping_box(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self.background = Blackout(self.game.screen.get_size(), self.game.ui)
        self.groups = self.game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = game.sleeping_box
        self.counter = 0
        self.rect = self.image.get_rect()
        self.x = (game.screen.get_size()[0] // 2) - (self.rect.size[0] // 2)
        self.y = (game.screen.get_size()[1] // 2) - (self.rect.size[1] // 2)
        self.rect.x = self.x
        self.rect.y = self.y
        self.game.player.blocked = True
        pg.mixer.music.fadeout(1000)
        self.game.night_snd.play(fade_ms=1000)

    def update(self):
        self.counter += self.game.clock.get_time()  # время в мс
        if self.counter >= 4000:
            print(self.counter)
            self.game.player.blocked = False
            self.kill()
            self.background.kill()
            self.game.night_snd.fadeout(1000)
            pg.mixer.music.play(fade_ms=1000, loops=-1)


class Balance_ui(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self.groups = self.game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = game.balance_ui
        self.o_image = self.image
        self.rect = self.image.get_rect()
        self.x = (game.screen.get_size()[0]) - (self.rect.size[0])
        self.y = 0
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        if self.game.camera.y == 0:
            self.set_bottom()
        if self.game.camera.y == (-(self.game.camera.h - HEIGHT)):
            self.set_top()
        self.balance_text()

    def set_bottom(self):
        self.y = self.game.screen.get_size()[1] - self.rect.size[1]
        self.rect.y = self.y

    def set_top(self):
        self.y = 0
        self.rect.y = self.y

    def balance_text(self):
        self.image = self.o_image.copy()
        font = pg.font.Font(None, 30)
        text = font.render(str(self.game.balance), True, (0, 0, 0))
        pos = (self.image.get_rect().topleft[0] + 20, self.image.get_rect().topleft[1] + 5)
        self.image.blit(text, pos)
