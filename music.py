# -*- coding: utf-8 -*-
import pygame
import game
import random
import tinytag
import groups


"""
Pitää sisällään seuraavaa:

class MusicPlayer(pygame.sprite.Sprite): taustamusiikin soittajaclass, osaa näyttää infoblurbin biisistä
class MusicFile(object): lukee tiedoston tagit ja tallettaa tiedon siitä, missä ruuduissa biisiä saa soittaa
MUSIC_FINISHED -pygame-eventti. Tämä nousee kun biisi on soitettu loppuun. Silloin pitää kutsua MusicPlayer.next()

Katso luokkien ja metodien docstringeistä lisää.
"""

# TODO: eriytä kaikki biisit ja biiseistä tehdyt soittolistat toisistaan

# Kustomieventti kappaleiden soiton händläämiseen
MUSIC_FINISHED = pygame.USEREVENT + 1


class MusicPlayer(pygame.sprite.Sprite):
    """
    class MusicPlayer(pygame.sprite.Sprite):
    
    Musiikin soittajaclassi. Osaa seuraavaa:
     -shuffle/ei shufflea
     -näyttää hienon infoblurbin kun biisi vaihtuu
     -osaa soittaa vain niitä biisejä, jotka on määritelty valideiksi käytössä olevaan ruutuun (game/menu/etc.)
     
     __init__:issä ottaa vastaan seuraavia argumentteja:
      -pos: 'topleft', 'topright', 'bottomleft' tai 'bottomright' - infoblurbin positio
      -shuffle: 1/0
      -screen: (string) - tämä määrittää missä ruudussa ollaan ja soittaa sen perusteella oikeaa musaa
      -group: pygame.sprite.Group 
      -window_size: ikkunan koko että osaa laskea infoblurbin position oikein
      
      HUOM HUOM! Toistaiseksi biisit pitää lisätä käsin __init__-osioon!
      
    """
    def __init__(self, pos='topleft', shuffle=1, screen='menu', group=None, window_size=(800, 600)):
        pygame.sprite.Sprite.__init__(self, group)
        self._shuffle = shuffle
        self._screen = screen

        # Infopläjäyksen graffa-init
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect()
        self._window_size = window_size

        # pos = 'topleft', 'topright', 'bottomleft' tai 'bottomright'
        self.pos = pos

        # Värit
        self.text_color = (255, 255, 255)
        self.bg_color = (127, 51, 0)
        self.border_color = (173, 69, 0)

        # Asemointi
        self.info_padding = 10
        self.border_width = 5
        self.screen_border_margin = 10

        # Fadeout - counter alkaa counter_startista ja vähentää siitä
        # Muuttaa alfa-arvoa jos counter on välillä 0...255
        self.fadeout_counter = 0
        self.fadeout_counter_start = 1000
        self.fadeout_decrement = 5

        self.playlist = []
        ############################################################
        # HUOM HUOM! Toistaiseksi biisit pitää lisätä käsin tähän! #
        ############################################################
        # self.playlist.append(MusicFile(filename='sfx/short_1.ogg', artist='PeraSpede',
        #                                title='Short Music', allowed_screens=('menu', 'game')))
        # self.playlist.append(MusicFile(filename='sfx/short_2.ogg', artist='PeraSpede',
        #                                title='Short Music 2', allowed_screens=('menu',)))
        # self.playlist.append(MusicFile(filename='sfx/short_3.ogg', artist='PeraSpede',
        #                               title='Short Music 3', allowed_screens=('menu', 'game')))
        self.playlist.append(MusicFile(filename='sfx/mouse_meets_robot.ogg', allowed_screens='game'))
        self.playlist.append(MusicFile(filename='sfx/cavern_rain.ogg', allowed_screens='menu'))
        if shuffle:
            self.shuffle_playlist()
        self.playlist_pointer = 0
        pygame.mixer.music.set_endevent(MUSIC_FINISHED)

    def play(self):
        """ 
        Soittaa playlist[]:issä olevan playlist_pointer:in määrittämän tähän ruutuun validin biisin. 
        Jos soittolista on käyty loppuun niin aloitetaan alusta (shufflettaen jos niin määritetty).
        """
        try:
            current_song = self.playlist[self.playlist_pointer]
        except IndexError:
            # Jos playlist on loppu niin aletaan alusta
            if self._shuffle:
                self.shuffle_playlist()
            self.playlist_pointer = 0
            current_song = self.playlist[0]

        # Tarkastetaan onko biisi validi tähän ruutuun
        if self._screen in current_song.allowed_screens:
            pygame.mixer.music.load(current_song.filename)
            pygame.mixer.music.play()
            # Näytetään infoblurb
            self.now_playing(current_song)
            # print("Now playing:", current_song.filename, current_song.title, current_song.artist)
        else:
            # Song not allowed in this screen. Next!
            self.next()

    def update(self):
        """ Tämä laskee infoblurbin fadeoutin """
        if self.fadeout_counter > 0:
            self.fadeout_counter -= self.fadeout_decrement
            # Jos fadeout_counter on välillä 0..255 niin asetetaan alpha siitä
            if 255 >= self.fadeout_counter >= 0:
                self.image.set_alpha(self.fadeout_counter)
            # Kuva tyhjäksi kun ollaan päästy nollaan
            if self.fadeout_counter <= 0:
                self.image = pygame.Surface((0, 0))
                self.rect = self.image.get_rect()

    def stop(self):
        pygame.mixer.music.stop()

    def now_playing(self, current_song):
        """ Näyttää soivan biisin tiedot ruudulla (infoblurb)"""
        # Tekstit
        line1 = "Now playing:"
        line2 = current_song.title
        line3 = "by " + current_song.artist

        # Teksteistä kuvat
        font1 = pygame.font.Font(None, 24)
        font2 = pygame.font.Font(None, 48)
        font3 = pygame.font.Font(None, 24)
        textimg1 = font1.render(line1, 1, self.text_color, self.bg_color)
        textimg2 = font2.render(line2, 1, self.text_color, self.bg_color)
        textimg3 = font3.render(line3, 1, self.text_color, self.bg_color)

        # Lasketaan pläjäyksen koko
        x_size = max(textimg1.get_width(), textimg2.get_width(), textimg3.get_width()) + self.info_padding * 2
        y_size = textimg1.get_height() + textimg2.get_height() + textimg3.get_height() + self.info_padding * 2

        # Piirretään pläjäys self.imageen
        self.image = pygame.Surface((x_size, y_size))
        self.image.fill(self.bg_color)
        pygame.draw.rect(self.image, self.border_color, (0, 0, x_size, y_size), self.border_width)

        self.image.blit(textimg1, (self.info_padding, self.info_padding))
        self.image.blit(textimg2, (self.info_padding, self.info_padding + textimg1.get_height()))
        self.image.blit(textimg3, (self.info_padding, self.info_padding + textimg1.get_height() + textimg2.get_height()))

        # Määritetään alpha ettei myöhemmin herjaa kun sitä muutetaan
        self.image.set_alpha(255)

        self.rect = self.image.get_rect()
        self._calculate_rect_position()

        self.fadeout_counter = self.fadeout_counter_start

    def _calculate_rect_position(self):
        if self.pos == 'topleft':
            self.rect.topleft = (self.screen_border_margin, self.screen_border_margin)
        elif self.pos == 'topright':
            self.rect.topright = (self._window_size[0] - self.screen_border_margin, self.screen_border_margin)
        elif self.pos == 'bottomleft':
            self.rect.bottomleft = (self.screen_border_margin, self._window_size[1] - self.screen_border_margin)
        else:
            self.rect.bottomright = (self._window_size[0] - self.screen_border_margin, self._window_size[1] - self.screen_border_margin)

    def set_screen(self, screen):
        self._screen = screen
        self.next()

    def shuffle_playlist(self):
        random.shuffle(self.playlist)

    def next(self):
        self.playlist_pointer += 1
        self.play()


class MusicFile(object):
    """ Kertoo filen tiedot - filenamen, artistin, titlen ja sallitut ruudut """
    def __init__(self, filename=None, allowed_screens=('game',)):
        self.filename = filename

        # Luetaan tagit
        tag = tinytag.TinyTag.get(filename)
        self.artist = tag.artist
        self.title = tag.title

        # Kertoo missä ruuduissa tätä saa soittaa - tuple/lista
        self.allowed_screens = allowed_screens


def debug_run():
    window = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Music test")
    clock = pygame.time.Clock()

    window.fill((0, 0, 0))

    # Music
    pygame.init()
    pygame.mixer.init()
    music_player = MusicPlayer(screen='game', window_size=(800, 600), pos='bottomleft', group=groups.TextGroup)
    music_player.play()

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MUSIC_FINISHED:
                music_player.next()

        window.fill(0)
        groups.TextGroup.update()
        groups.TextGroup.draw(window)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == '__main__':
    debug_run()
