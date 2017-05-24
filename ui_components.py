# -*- coding: utf8 -*-
import pygame
import assets
from pygame.locals import *
from colors import *

pygame.font.init()


class Button(object):
    def __init__(self, rect=Rect(10, 10, 150, 50), text='Button', bgcolor=YELLOWISH, textcolor=BLACK, font_size=30,
                 surface_images=None):
        self._rect = rect
        self._text = text
        self._bgcolor = bgcolor
        self._textcolor = textcolor
        self._font = pygame.font.Font(None, font_size)

        self._buttonDown = False
        self._mouseOverButton = False
        self._lastMouseDownOverButton = False
        self._visible = True

        if surface_images is None:
            self.surfaceNormal = pygame.Surface(self._rect.size)
            self.surfaceDown = pygame.Surface(self._rect.size)
            self.surfaceHighlight = pygame.Surface(self._rect.size)
            self.has_text = True
        else:
            self.surfaceNormal = assets.assets[surface_images[0]]
            self.surfaceDown = assets.assets[surface_images[1]]
            self.surfaceHighlight = assets.assets[surface_images[2]]
            self.has_text = False

        self.update()

    def handleEvent(self, eventObj):
        if eventObj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN) or not self._visible:
            return []

        retVal = []

        hasExited = False
        if not self._mouseOverButton and self._rect.collidepoint(eventObj.pos):
            # mouse entered the button
            self._mouseOverButton = True
            self.mouseEnter(eventObj)
            retVal.append('enter')
        elif self._mouseOverButton and not self._rect.collidepoint(eventObj.pos):
            # mouse exited the button
            self._mouseOverButton = False
            hasExited = True

        if self._rect.collidepoint(eventObj.pos):
            # mouse event happened over the button
            if eventObj.type == MOUSEMOTION:
                self.mouseMove(eventObj)
                retVal.append('move')
            elif eventObj.type == MOUSEBUTTONDOWN:
                self._buttonDown = True
                self._lastMouseDownOverButton = True
                self.mouseDown(eventObj)
                retVal.append('down')
        else:
            if eventObj.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
                # Mouse up/down event happened off the button, no mouseClick()
                self._lastMouseDownOverButton = False

        doMouseClick = False
        if eventObj.type == MOUSEBUTTONUP:
            if self._lastMouseDownOverButton:
                doMouseClick = True
            self._lastMouseDownOverButton = False

            if self._buttonDown:
                self._buttonDown = False
                self.mouseUp(eventObj)
                retVal.append('up')

            if doMouseClick:
                self._buttonDown = False
                self.mouseClick(eventObj)
                retVal.append('click')

        if hasExited:
            self.mouseExit(eventObj)
            retVal.append('exit')

        return retVal

    def draw(self, surfaceObj):
        if self._visible:
            if self._buttonDown:
                surfaceObj.blit(self.surfaceDown, self._rect)
            elif self._mouseOverButton:
                surfaceObj.blit(self.surfaceHighlight, self._rect)
            else:
                surfaceObj.blit(self.surfaceNormal, self._rect)

    def update(self):
        width = self._rect.width
        height = self._rect.height

        if self.has_text:
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


class ButtonGroup(object):

    """
    Button-ryhmä koodin selkeyttämiseksi, piirtää kaikki ryhmän buttonit yhdelle draw-kutsulla
    """

    def __init__(self):
        self.buttons = []

    def add(self, button):
        self.buttons.append(button)

    def draw(self, surface_obj):
        for button in self.buttons:
            button.draw(surface_obj)


class LabelImageText(pygame.sprite.Sprite):

    def __init__(self, group=None, image_text=None, position=(0, 0)):
        pygame.sprite.Sprite.__init__(self, group)
        try:
            self.image = assets.assets['gfx/UI_text_%s.png' % image_text]
        except pygame.error:
            # Jos kuvaa ei löydy, käytä rendattua fonttia?
            self.image = pygame.Surface()
        self.rect = self.image.get_rect()
        self.rect.topleft = position


class Checkbox(pygame.sprite.Sprite):

    def __init__(self, group=None, checked=True, position=(0, 0), checkbox_group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self._unchecked_image = assets.assets['gfx/UI_checkbox_base.png']
        self._checked_image = assets.assets['gfx/UI_checkbox_checked.png']
        self._checked = checked
        if self._checked:
            self.image = self._checked_image
        else:
            self.image = self._unchecked_image
        self.rect = self.image.get_rect()
        self.rect.topleft = position

        self._buttonDown = False
        self._mouseOverButton = False
        self._lastMouseDownOverButton = False
        self._visible = True

        self._checkbox_group = checkbox_group
        if self._checkbox_group is not None:
            self._checkbox_group.add(self)

    def change_state(self, state=None, group_update=False):
        if state is None:
            self._checked = not self._checked
        else:
            self._checked = state

        if self._checked:
            self.image = self._checked_image
        else:
            self.image = self._unchecked_image

        if self._checkbox_group is not None and not group_update:
            self._checkbox_group.update_checkboxes(self)

    def _get_checked(self):
        return self._checked

    def _set_checked(self, state):
        self.change_state(state)

    def draw(self, surfaceObj):
        if self._visible:
            if self._checked:
                surfaceObj.blit(self._checked_image, self.rect)
            else:
                surfaceObj.blit(self._unchecked_image, self.rect)

    def handleEvent(self, eventObj):
        if eventObj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN) or not self._visible:
            return []

        retVal = []

        hasExited = False
        if not self._mouseOverButton and self.rect.collidepoint(eventObj.pos):
            # mouse entered the button
            self._mouseOverButton = True
            self.mouseEnter(eventObj)
            retVal.append('enter')
        elif self._mouseOverButton and not self.rect.collidepoint(eventObj.pos):
            # mouse exited the button
            self._mouseOverButton = False
            hasExited = True

        if self.rect.collidepoint(eventObj.pos):
            # mouse event happened over the button
            if eventObj.type == MOUSEMOTION:
                self.mouseMove(eventObj)
                retVal.append('move')
            elif eventObj.type == MOUSEBUTTONDOWN:
                self._buttonDown = True
                self._lastMouseDownOverButton = True
                self.mouseDown(eventObj)
                retVal.append('down')
        else:
            if eventObj.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
                # Mouse up/down event happened off the button, no mouseClick()
                self._lastMouseDownOverButton = False

        doMouseClick = False
        if eventObj.type == MOUSEBUTTONUP:
            if self._lastMouseDownOverButton:
                doMouseClick = True
            self._lastMouseDownOverButton = False

            if self._buttonDown:
                self._buttonDown = False
                self.mouseUp(eventObj)
                retVal.append('up')

            if doMouseClick:
                self._buttonDown = False
                self.mouseClick(eventObj)
                retVal.append('click')
                self.change_state()

        if hasExited:
            self.mouseExit(eventObj)
            retVal.append('exit')

        return retVal

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

    checked = property(_get_checked, _set_checked)


class CheckboxGroup(object):

    """
    Ryhmä checkboxeja, jossa on aina yksi ja vain yksi box checkattuna
    """

    def __init__(self):
        self.checkboxes = []
        self.checked_index = None

    def add(self, checkbox):
        self.checkboxes.append(checkbox)
        if checkbox.checked:
            self.checked_index = len(self.checkboxes)-1

    def update_checkboxes(self, checked_checkbox):
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox is not checked_checkbox:
                checkbox.change_state(state=False, group_update=True)
            else:
                self.checked_index = i
                # Varmistetaan että groupissa ainakin yksi checkbox on koko ajan checkattuna
                checked_checkbox.change_state(state=True, group_update=True)

    def set_checked_index(self, index):
        self.checkboxes[index].checked = True


class Slider(pygame.sprite.Sprite):

    """
    Slider, jonka arvo vaihtelee välillä 0.0-1.0
    """

    def __init__(self, group=None, position=(0, 0), value=1.0):
        pygame.sprite.Sprite.__init__(self, group)
        self._rail_image = assets.assets['gfx/UI_slide_base.png']
        self._knob_image = assets.assets['gfx/UI_slide_knob.png']
        self.image = self._rail_image
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self._knob_image_rect = self._knob_image.get_rect()
        self._knob_max = self.rect.width - self._knob_image_rect.width
        self._value = value
        self._set_value(self._value)
        self._buttonDown = False
        self._mouseOverButton = False

    def _set_value(self, value):
        self._value = value
        knob_position = int(self._knob_max * value)
        self.image = self._rail_image.copy()
        self.image.blit(self._knob_image, (knob_position, 0))

    def _get_value(self):
        return self._value

    def _move(self, position):
        value = position[0] - self.rect.left
        if value < 0:
            value = 0
        elif value > self._knob_max:
            value = self._knob_max

        value = value / float(self._knob_max)
        self._set_value(value)

    def handleEvent(self, eventObj):
        if eventObj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN):
            return []

        retVal = []

        if self.rect.collidepoint(eventObj.pos) or self._buttonDown:
            if eventObj.type == MOUSEMOTION and self._buttonDown:
                # muutetaan sliderin arvoa hiiren nappi pohjassa (drag)
                self._move(eventObj.pos)
                retVal.append('drag')
            elif eventObj.type == MOUSEBUTTONDOWN:
                self._buttonDown = True
                retVal.append('down')

        if eventObj.type == MOUSEBUTTONUP:
            if self._buttonDown:
                self._buttonDown = False
                retVal.append('up')

        return retVal

    value = property(_get_value, _set_value)


def draw_loading_bar(window, current, total, bar_width=400, bar_height=30, pos=(200, 335), color=BLACK):
    """
    Piirtää ruudulle latauspalkin.
    window - pygamen ruutuobjekti
    current - ladattavan jutun nykyinen arvo
    total - ladattavan jutun täysi arvo
    bar_width - latauspalkin leveys kun lataus on valmis
    bar_height - latauspalkin korkeus 
    pos - positio
    color - väri  
    """
    # TODO: muuta tämäkin classiksi
    current = float(current)  # vaatii tämän ettei tee integer divisionia
    width = min(bar_width, int(current / total * bar_width))  # lasketaan loading barin leveys
    height = bar_height
    loading_bar_surface = pygame.Surface((width, height))
    loading_bar_surface.fill(color)
    blitrect = window.blit(loading_bar_surface, pos)
    pygame.display.update(blitrect)  # päivitetään vain se osa ruudusta mitä tarvii