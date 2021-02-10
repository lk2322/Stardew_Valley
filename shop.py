import pygame as pg
import gui
import assortment


class Shop():
    def __init__(self, game):
        self.game = game
        self.items_group = pg.sprite.Group()
        self.shop_bg_ui = Shop_UI_bg(self.game)
        self.shop_exit_ui = Shop_ui_exit(
            self.game, self, self.shop_bg_ui.rect.topright)
        self.shop_sell_ui = Shop_ui_sell(self.game, self, self.shop_bg_ui.rect.bottomright)
        x, y = 0, 0
        for name, info in assortment.assortment.items():
            pos = self.shop_bg_ui.rect.topleft[0] + 10 + x, self.shop_bg_ui.rect.topleft[1] + 40 + y
            Shop_ui_item(self.game, pos, name, info[0], info[1], self)
            x += 70
        self.game.player.blocked = True

    def kill_all(self):
        self.shop_bg_ui.kill()
        self.shop_exit_ui.kill()
        [item.kill() for item in self.items_group.sprites()]
        self.shop_sell_ui.kill()
        self.game.player.blocked = False


class Shop_UI_bg(pg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.shop_bg
        self.items = {}
        self.rect = self.image.get_rect()
        self.x = (game.screen.get_size()[0] // 2) - (self.rect.size[0] // 2)
        self.y = (game.screen.get_size()[1] // 2) - (self.rect.size[1] // 2)
        self.rect.x = self.x
        self.rect.y = self.y

    def trigger(self):
        pass


class Shop_ui_exit(pg.sprite.Sprite):
    def __init__(self, game, shop, pos: tuple):
        self.shop = shop
        self.groups = game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.shop_close_btn
        self.items = {}
        self.rect = self.image.get_rect()
        self.x = pos[0] - self.rect.size[0]
        self.y = pos[1]
        self.rect.x = self.x
        self.rect.y = self.y

    def trigger(self):
        self.shop.kill_all()
        self.game.button_snd.play()


class Shop_ui_item(pg.sprite.Sprite):
    def __init__(self, game, pos, item: str, item_imgs, price, shop):
        self.shop = shop
        self.game = game
        self.groups = self.shop.items_group, self.game.ui
        self.item_name = item
        self.price = price
        pg.sprite.Sprite.__init__(self, self.groups)
        self.item_imgs = item_imgs
        self.image = self.generate_item_imgs()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def generate_item_imgs(self):
        image_ui_item = self.item_imgs[0]
        image = self.game.shop_item.copy()
        pos = image.get_rect().size
        x = (pos[0] // 2) - (image_ui_item.get_size()[0] // 2)
        y = (pos[1] // 2) - (image_ui_item.get_size()[1] // 2)
        image.blit(image_ui_item, (x, y))
        font = pg.font.Font(None, 30)
        text = font.render(str(self.price), True, (0, 0, 0))
        pos = (image.get_rect().bottomright[0] - 40, image.get_rect().bottomright[1] - 25)
        image.blit(text, pos)
        return image

    def trigger(self):
        if self.game.balance >= self.price:
            res = self.game.hud_inv.add_item(
                gui.Item(self.game.hud_inv, self.item_imgs[0].copy(), 'seed', 1, True, self.item_name))
            if res:
                self.game.balance -= self.price
        self.game.button_snd.play()


class Shop_ui_sell(pg.sprite.Sprite):
    def __init__(self, game, shop, pos: tuple):
        self.shop = shop
        self.groups = game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.shop_sell
        self.items = {}
        self.rect = self.image.get_rect()
        self.x = pos[0] // 2 - self.rect.size[0] // 2 + 40
        self.y = pos[1] - 20 - self.rect.size[1]
        self.rect.x = self.x
        self.rect.y = self.y

    def trigger(self):
        items = self.game.hud_inv.items.copy().items()
        for pos, item in items:
            if not item:
                continue
            if item.price != 0:
                self.game.balance += item.price * item.col
                item.del_item()
        self.game.sell_snd.play()
