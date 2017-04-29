# -*- coding: utf8 -*-
import pygame, AUTSball
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

    # Logo
    logo_sprite = pygame.sprite.Sprite()
    logo_sprite.image = pygame.image.load('gfx/AUTSBall_logo.png').convert_alpha()
    logo_sprite.rect = logo_sprite.image.get_rect()
    logo_sprite.rect.topleft = (50, 30)
    static_visual_components_group.add(logo_sprite)
    static_visual_components_group.draw(window)

    # Buttons
    practice_button = Button(Rect(50, 330, 250, 70), 'Practice flight')
    multiplayer_button = Button(Rect(50, 405, 250, 70), 'Multiplayer')
    quit_button = Button(Rect(50, 480, 250, 70), 'Quit')

    active_mode = 'menu'
    practice_game = None

    # Music
    pygame.mixer.init()
    pygame.mixer.music.load('sfx/title_music_by_pera.ogg')
    pygame.mixer.music.play(-1)

    running = True
    while running:

        for event in pygame.event.get():
            if active_mode == 'menu':
                if 'click' in practice_button.handleEvent(event):
                    #print('practice button clicked')
                    active_mode = 'practice'
                    window.fill(BLACK)
                    practice_game = AUTSball.AUTSBallGame()
                    pygame.mixer.music.stop()
                if 'click' in multiplayer_button.handleEvent(event):
                    print('multiplayer button clicked')
                if 'click' in quit_button.handleEvent(event):
                    running = False
            if active_mode == 'practice':
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        del practice_game
                        active_mode = 'menu'
                        window.fill(BLACK)
                        static_visual_components_group.draw(window)
                        pygame.mixer.music.play(-1)
            if event.type == pygame.QUIT:
                running = False

        if active_mode == 'menu':
            practice_button.draw(window)
            multiplayer_button.draw(window)
            quit_button.draw(window)

            pygame.display.update()
            clock.tick(30)
        elif active_mode == 'practice':
            practice_game.update()

    pygame.quit()

if __name__ == '__main__':
    debug_run()
