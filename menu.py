# -*- coding: utf8 -*-
import pygame, AUTSball, menu_background_action

from pygame.locals import *

WHITE = (255, 255, 255)
YELLOWISH = (212, 208, 100)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

pygame.font.init()


class Button(object):
    def __init__(self, rect=Rect(10, 10, 150, 50), text='Button', bgcolor=YELLOWISH, textcolor=BLACK, font_size=30):
        self._rect = rect
        self._text = text
        self._bgcolor = bgcolor
        self._textcolor = textcolor
        self._font = pygame.font.Font(None, font_size)

        self.buttonDown = False
        self.mouseOverButton = False
        self.lastMouseDownOverButton = False
        self._visible = True

        self.surfaceNormal = pygame.Surface(self._rect.size)
        self.surfaceDown = pygame.Surface(self._rect.size)
        self.surfaceHighlight = pygame.Surface(self._rect.size)

        self.update()

    def handleEvent(self, eventObj):
        if eventObj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN) or not self._visible:
            return []

        retVal = []

        hasExited = False
        if not self.mouseOverButton and self._rect.collidepoint(eventObj.pos):
            # mouse entered the button
            self.mouseOverButton = True
            self.mouseEnter(eventObj)
            retVal.append('enter')
        elif self.mouseOverButton and not self._rect.collidepoint(eventObj.pos):
            # mouse exited the button
            self.mouseOverButton = False
            hasExited = True

        if self._rect.collidepoint(eventObj.pos):
            # mouse event happened over the button
            if eventObj.type == MOUSEMOTION:
                self.mouseMove(eventObj)
                retVal.append('move')
            elif eventObj.type == MOUSEBUTTONDOWN:
                self.buttonDown = True
                self.lastMouseDownOverButton = True
                self.mouseDown(eventObj)
                retVal.append('down')
        else:
            if eventObj.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
                # Mouse up/down event happened off the button, no mouseClick()
                self.lastMouseDownOverButton = False

        doMouseClick = False
        if eventObj.type == MOUSEBUTTONUP:
            if self.lastMouseDownOverButton:
                doMouseClick = True
            self.lastMouseDownOverButton = False

            if self.buttonDown:
                self.buttonDown = False
                self.mouseUp(eventObj)
                retVal.append('up')

            if doMouseClick:
                self.buttonDown = False
                self.mouseClick(eventObj)
                retVal.append('click')

        if hasExited:
            self.mouseExit(eventObj)
            retVal.append('exit')

        return retVal

    def draw(self, surfaceObj):
        if self._visible:
            if self.buttonDown:
                surfaceObj.blit(self.surfaceDown, self._rect)
            elif self.mouseOverButton:
                surfaceObj.blit(self.surfaceHighlight, self._rect)
            else:
                surfaceObj.blit(self.surfaceNormal, self._rect)

    def update(self):
        width = self._rect.width
        height = self._rect.height

        self.surfaceNormal.fill(self._bgcolor)
        self.surfaceDown.fill(WHITE)
        self.surfaceHighlight.fill(GREEN)

        text_surface = self._font.render(self._text, True, self._textcolor)
        text_rect = text_surface.get_rect()
        text_rect.center = (int(width / 2), int(height / 2))
        self.surfaceNormal.blit(text_surface, text_rect)
        self.surfaceDown.blit(text_surface, text_rect)
        self.surfaceHighlight.blit(text_surface, text_rect)

    def mouseClick(self, event):
        pass

    def mouseEnter(self, event):
        pass

    def mouseMove(self, event):
        pass

    def mouseExit(self, event):
        pass

    def mouseDown(self, event):
        pass

    def mouseUp(self, event):
        pass

    def _propGetText(self):
        return self._text

    def _propSetText(self, text):
        self._text = text
        self.update()

    def _propGetRect(self):
        return self._rect

    def _propSetRect(self, newRect):
        self._rect = newRect
        self.update()

    def _propGetVisible(self):
        return self._visible

    def _propSetVisible(self, setting):
        self._visible = setting

    def _propGetTextColor(self):
        return self._textcolor

    def _propSetTextColor(self, setting):
        self._textcolor = setting
        self.update()

    def _propGetBgColor(self):
        return self._bgcolor

    def _propSetBgColor(self, setting):
        self._bgcolor = setting
        self.update()

    text = property(_propGetText, _propSetText)
    rect = property(_propGetRect, _propSetRect)
    visible = property(_propGetVisible, _propSetVisible)
    textcolor = property(_propGetTextColor, _propSetTextColor)
    bgcolor = property(_propGetBgColor, _propSetBgColor)


def debug_run():
    window = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Menu test")
    clock = pygame.time.Clock()

    window.fill((0, 0, 0))

    static_visual_components_group = pygame.sprite.Group()
    music_player_group = pygame.sprite.Group()

    # Logo
    logo_sprite = pygame.sprite.Sprite()
    logo_sprite.image = pygame.image.load('gfx/AUTSBall_logo.png').convert_alpha()
    logo_sprite.rect = logo_sprite.image.get_rect()
    logo_sprite.rect.center = (400, 110)
    static_visual_components_group.add(logo_sprite)
    static_visual_components_group.draw(window)

    # Buttons
    practice_button = Button(Rect(50, 330, 250, 70), 'Practice flight')
    multiplayer_button = Button(Rect(50, 405, 250, 70), 'Multiplayer')
    quit_button = Button(Rect(50, 480, 250, 70), 'Quit')

    practice_button.rect.center = (400, 250)
    multiplayer_button.rect.center = (400, 330)
    quit_button.rect.center = (400, 410)

    active_mode = 'menu'
    practice_game = None

    # Music
    pygame.mixer.init()
    music_player = music.MusicPlayer(pos='bottomright', screen='menu', group=music_player_group)
    music_player.play()
    # pygame.mixer.music.load('sfx/cavern_rain.ogg')
    # pygame.mixer.music.play(-1)

    # Background action
    background_action = menu_background_action.BackgroundAction()
    # Tämä tummentaa tausta-actionin
    darken_surface = pygame.Surface((800, 600))
    darken_surface.set_alpha(128)

    running = True
    while running:

        for event in pygame.event.get():
            if active_mode == 'menu':
                if 'click' in practice_button.handleEvent(event):
                    #print('practice button clicked')
                    active_mode = 'practice'
                    window.fill(BLACK)
                    # Lopetetaan background action
                    background_action.kill_me()
                    del background_action

                    practice_game = AUTSball.AUTSBallGame()
                    music_player.stop()
                if 'click' in multiplayer_button.handleEvent(event):
                    print('multiplayer button clicked')
                if 'click' in quit_button.handleEvent(event):
                    running = False
            if active_mode == 'practice':
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        practice_game.empty_groups()
                        del practice_game
                        active_mode = 'menu'
                        window.fill(BLACK)
                        background_action = menu_background_action.BackgroundAction()
                        static_visual_components_group.draw(window)
                        music_player.set_screen('menu')
            if event.type == pygame.QUIT:
                running = False
            if event.type == music.MUSIC_FINISHED:
                music_player.next()

        if active_mode == 'menu':
            window.fill(0)

            menu_background_action.background_group.update()
            music_player_group.update()

            menu_background_action.background_group.draw(window)
            window.blit(darken_surface, (0, 0))

            static_visual_components_group.draw(window)
            practice_button.draw(window)
            multiplayer_button.draw(window)
            quit_button.draw(window)
            music_player_group.draw(window)

            pygame.display.update()
            clock.tick(30)
        elif active_mode == 'practice':
            practice_game.update()

    pygame.quit()

if __name__ == '__main__':
    debug_run()
