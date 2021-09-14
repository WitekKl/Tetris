import arcade
import random
import os
from typing import Optional

# wykorzystano:
# Paul Vincent Craven.
# https://arcade.academy/index.html
# https://www.kenney.nl/
# http://dig.ccmixter.org/
# muzyka jest dostępna na licencji Creative Commons

# definicja kształtów i rodzjów kolorów
ksztalt1 = [[1, 5, 9, 13], [4, 5, 6, 7], [6, 10, 13, 14], [4, 8, 9, 10], [5, 6, 9, 13], [4, 5, 6, 10], [5, 9, 13, 14],
            [8, 9, 10, 6], [5, 6, 10, 14], [8, 9, 10, 12], [5, 8, 9, 10], [5, 9, 10, 13], [4, 5, 6, 9], [6, 9, 10, 14],
            [5, 6, 10, 11], [6, 9, 10, 13], [5, 6, 8, 9], [5, 9, 10, 14], [5, 6, 9, 10]]
elementy = [[0, 2], [2, 4], [6, 4], [10, 4], [14, 2], [16, 2], [18, 1]]
colors = (arcade.color.BABY_BLUE, arcade.color.ORANGE, arcade.color.GOLD, arcade.color.GRAY, arcade.color.GREEN,
          arcade.color.CYAN, arcade.color.PURPLE, arcade.color.ALABAMA_CRIMSON, arcade.color.AVOCADO,
          arcade.color.BLUEBONNET, arcade.color.DARK_PASTEL_GREEN)

# definicja stałych
scale = 0.25
tile = 128
width, height = arcade.get_display_size()
sloik_x = 128
srodek = 12
sloik_y_bottom = 50
ile_wierszy = 20
sloik_y_top = sloik_y_bottom + ile_wierszy * tile * scale
wiel_elem = 32
MUSIC_VOLUME = 0.01
SCREEN_TITLE = "TETRIS"
SCREEN_WIDTH = width
SCREEN_HEIGHT = height

class GameOverView(arcade.View):
    # napisy na koniec gry
    def __init__(self):
        super().__init__()
        self.background = arcade.Sprite("tetris/galaxy2.png")
        self.background.left = self.background.bottom = 0
        self.level_sound = arcade.load_sound("tetris/level2.ogg")
        arcade.sound.play_sound(self.level_sound)

    def on_draw(self):
        arcade.start_render()
        self.background.draw()
        if self.window.score > 10:
            arcade.draw_text("Gratulacje, twoj wynik:  " + str(self.window.score), SCREEN_WIDTH / 2,
                             2 * SCREEN_HEIGHT / 3,
                             arcade.color.RED_BROWN, font_size=40, anchor_x="center", font_name="tetris/Hardsign")
        else:
            arcade.draw_text("Niezbyt dobrze, popraw sie, wynik:  :  " + str(self.window.score), SCREEN_WIDTH / 2,
                             2 * SCREEN_HEIGHT / 3,
                             arcade.color.RED_BROWN, font_size=40, anchor_x="center", font_name="tetris/Hardsign")
        arcade.draw_text("Nacisnij klawisz myszki by grac jeszcze raz", SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2,
                         arcade.color.RED_BROWN, font_size=40, anchor_x="center", font_name="tetris/Hardsign")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        self.window.score = 0
        game_view = GameView()
        self.window.show_view(game_view)


class Wybuch(arcade.Sprite):
    # wybuch w przypadku ułożenia całego wiersza
    def __init__(self, hit_box_algorithm):
        super().__init__()
        self.szybkosc = 0

        self.wybuch_textures = []
        self.scale = 1
        # ile tekstur ma wybuch
        for i in range(17):
            texture = arcade.load_texture(f"tetris/1_{i}.png")
            self.wybuch_textures.append(texture)

        # ustawienie początku tekstury na 0
        self.cur_texture = 0
        self.texture = self.wybuch_textures[self.cur_texture]
        self.hit_box = self.texture.hit_box_points

    def update(self):
        # aktualizacja - ustawienie szybkości i wszystkich tekstur do wybuchu
        self.szybkosc += 1
        if self.szybkosc == 5:
            self.cur_texture += 1
            if self.cur_texture < len(self.wybuch_textures):
                self.texture = self.wybuch_textures[self.cur_texture]
                self.szybkosc = 0
            else:
                self.remove_from_sprite_lists()
                self.cur_texture = 0
                self.szybkosc = 0


class GameView(arcade.View):
    # główna część gry
    def __init__(self):
        super().__init__()

        arcade.set_background_color(arcade.color.BLUE_YONDER)
        # ustalenie zmiennych i spritów
        self.wybuch_list: Optional[arcade.SpriteList] = None
        self.ksztalty_list: Optional[arcade.SpriteList] = None
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False
        self.spacja = False
        self.czas = 0
        self.maksczas = 25
        self.nast = 0
        self.ktory = 0
        self.poczatek = 0
        self.ileobrotow = 2
        self.przes_x = 1
        self.przes_y = 0
        self.kolor = arcade.color.BABY_BLUE
        self.element_kolor = 0
        self.koniecopadania = 0
        self.czyprzesunac = 0
        self.zachowaj = 0
        self.jakiruch = "brak"
        self.kolizja = False
        self.czasreakcji = 0
        self.music = 0
        self.kolizja_sound = arcade.load_sound("tetris/upgrade.ogg")
        self.musicp = arcade.sound.load_sound("tetris/grapes_-_I_dunno.mp3")

        self.setup()

    def setup(self):
        # rysuj - tabela z pustą studnią i ramką
        self.poziom = 0
        self.musicp.play(MUSIC_VOLUME)
        self.wybuch_list = arcade.SpriteList()
        self.wybuch = Wybuch(hit_box_algorithm="Simple")
        self.background = arcade.Sprite("tetris/galaxy2.png")
        self.background.left = self.background.bottom = 0
        self.tabela = []
        for row in range(ile_wierszy + 1):
            self.tabela.append([])
            for column in range(srodek + 2):
                if column == srodek or column == 0 or row == ile_wierszy:
                    self.tabela[row].append(2)
                else:
                    self.tabela[row].append(0)

    def wybuchy(self, x, y):
        # ustalenie pozycji wybuchu przy całym rzędzie
        self.wybuch = Wybuch(hit_box_algorithm="Simple")
        self.wybuch.center_x = x
        self.wybuch.center_y = y
        self.wybuch.scale = 0.25
        self.wybuch.update()
        self.wybuch_list.append(self.wybuch)

    def on_key_press(self, key, modifiers):
        # sterowanie
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.M:
            if self.music == 0:
                self.music = 1
                self.musicp.stop()
            else:
                self.music = 0
                self.musicp.play(MUSIC_VOLUME)

    def on_key_release(self, key, modifiers):
        # cd sterowania
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False

    def losuj_element(self):
        # ustalenie danych do spadającego klocka
        self.ktory = random.randint(0, 6)
        self.element_kolor = random.randint(0, 10)
        self.kolor = colors[self.element_kolor]
        self.poczatek = elementy[self.ktory][0]
        self.ileobrotow = elementy[self.ktory][1]
        self.koniecopadania = 0
        self.czyprzesunac = 0
        self.zachowaj = 0
        self.kolizja = False
        self.nast = 0
        self.przes_y = 0
        self.przes_x = 1
        self.czas = 0
        self.maksczas = 25 - self.poziom
        self.czasreakcji = 0
        self.sprawdzenie()
        if self.kolizja == True:
            self.game_over()

    def sprawdzenie(self):
        # sprawdzenie czy klocek może spadać
        for i in range(4):
            for row in range(4):
                for column in range(4):
                    pole = ksztalt1[self.poczatek + self.nast][i]
                    if row + column * 4 == pole:
                        if self.tabela[row + self.przes_y][column + self.przes_x] > 1:
                            self.kolizja = True

    def usunwiersz(self):
        # usuwa cały wiersz złożony z klocków
        self.podwajanie_wyniku = 0
        for row in range(ile_wierszy):
            ile = 0
            for column in range(srodek + 1):
                if self.tabela[row][column] > 9:
                    ile += 1
            if ile == srodek - 1:
                for column in range(srodek - 1):
                    self.tabela[row][column + 1] = 0
                    x = wiel_elem * (column + 1) + sloik_x + scale * tile / 2
                    y = sloik_y_top - wiel_elem * row
                    self.wybuchy(x, y)
                self.przesunwiersze(row)

    def przesunwiersze(self, row):
        # przesuwa wiersze z góry na dół
        arcade.start_render()
        self.rysuj_siatke()
        arcade.pause(0.1)
        self.window.score += 1 + self.podwajanie_wyniku
        arcade.play_sound(self.kolizja_sound)
        self.podwajanie_wyniku += 1
        self.poziom += 1
        if self.poziom > 15:
            self.poziom = 15

        for newrow in range(row, 1, -1):
            for column in range(srodek - 1):
                stary = self.tabela[newrow - 1][column + 1]
                self.tabela[newrow][column + 1] = stary
                self.tabela[newrow - 1][column + 1] = 0

    def on_update(self, delta_time):
        # główna pętla programu
        self.wybuch_list.update()
        self.czas += 1
        if self.czasreakcji > 0:
            self.czasreakcji -= 1
        if self.up_pressed and self.czasreakcji == 0 and not self.down_pressed:
            self.czasreakcji = 10 - int(self.poziom / 4)
            tymnast = self.nast
            self.nast += 1
            if self.nast == self.ileobrotow:
                self.nast = 0
            self.sprawdzenie()
            if self.kolizja == True:

                self.nast = tymnast
                self.kolizja = False
            else:
                for row in range(ile_wierszy + 1):
                    for column in range(srodek + 2):
                        if self.tabela[row][column] == 1:
                            self.tabela[row][column] = 0
        if self.down_pressed and self.czasreakcji == 0 and not self.up_pressed:
            self.czasreakcji = 10 - int(self.poziom / 4)
            self.maksczas = 1
            self.czas = 1
        if self.left_pressed and not self.right_pressed and self.czasreakcji == 0:
            self.czasreakcji = 10 - int(self.poziom / 4)
            self.przes_x -= 1
            self.sprawdzenie()
            if self.kolizja == True:
                self.przes_x += 1
                self.kolizja = False
            for row in range(ile_wierszy + 1):
                for column in range(srodek + 2):
                    if self.tabela[row][column] == 1:
                        self.tabela[row][column] = 0
        if self.right_pressed and not self.left_pressed and self.czasreakcji == 0:
            self.czasreakcji = 10 - int(self.poziom / 4)
            self.przes_x += 1
            self.sprawdzenie()
            if self.kolizja == True:
                self.przes_x -= 1
                self.kolizja = False
            for row in range(ile_wierszy + 1):
                for column in range(srodek + 2):
                    if self.tabela[row][column] == 1:
                        self.tabela[row][column] = 0

        if self.czas == self.maksczas and self.zachowaj == 0:
            self.czas = 0
            for row in range(ile_wierszy + 1):
                for column in range(srodek + 2):
                    if self.tabela[row][column] == 1:
                        self.tabela[row][column] = 0
            self.przes_y += 1
            # sprawdzenie po wirtualnym opadaniu można faktycznie opaść
            if self.koniecopadania == 0 and self.czyprzesunac == 0:
                self.sprawdzenie()
                if self.kolizja == True:
                    self.koniecopadania = 1

        if self.koniecopadania == 0:
            for i in range(4):
                for row in range(4):
                    for column in range(4):
                        pole = ksztalt1[self.poczatek + self.nast][i]
                        if row + column * 4 == pole and self.zachowaj == 0:
                            self.tabela[row + self.przes_y][column + self.przes_x] = 1
        if self.koniecopadania == 1:
            self.koniecopadania = 0
            self.zachowaj = 1
            self.przes_y -= 1
            self.kolizja = False
            for i in range(4):
                for row in range(4):
                    for column in range(4):
                        pole = ksztalt1[self.poczatek + self.nast][i]
                        if row + column * 4 == pole:
                            self.tabela[row + self.przes_y][column + self.przes_x] = int(self.element_kolor + 10)
            self.usunwiersz()
            arcade.pause(0.1)
            self.losuj_element()

    def on_draw(self):
        # rysowania
        arcade.start_render()
        self.background.draw()
        self.rysuj_siatke()
        self.wynik()
        self.wybuch_list.draw()

    def rysuj_siatke(self):
        # dodatkowe tło z siatką
        for row in range(ile_wierszy + 1):
            for column in range(srodek + 1):
                wartosc = int(self.tabela[row][column])
                if wartosc == 0:
                    if int(column + row) % 2 == 0:
                        color = arcade.color.WHITE_SMOKE
                    else:
                        color = arcade.color.WHITE
                elif wartosc == 1:
                    color = self.kolor
                elif wartosc == 2:
                    color = arcade.color.BLACK_OLIVE
                else:
                    t1 = wartosc - 10
                    color = colors[t1]
                x = wiel_elem * column + sloik_x + scale * tile / 2
                y = sloik_y_top - wiel_elem * row
                arcade.draw_rectangle_filled(x, y, wiel_elem, wiel_elem, color)

    def wynik(self):
        # napsiy o wyniku
        arcade.draw_text("Wynik: " + str(self.window.score), width / 2, height / 2, arcade.color.RED_BROWN,
                         font_size=40, anchor_x="center", font_name="space/ok/Hardsign")
        if self.musicp.is_complete() and self.music == 0:
            self.musicp.play(MUSIC_VOLUME)

    def game_over(self):
        # koniec gry -wywołanie
        if self.music == 0:
            self.musicp.stop()
        arcade.pause(0.1)
        game_over_view = GameOverView()
        self.window.show_view(game_over_view)


def main():
    # główna metoda
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=full)
    window.score = 0
    menu_view = GameView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
