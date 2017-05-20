# -*- coding: utf8 -*-
from pygame import *
from gloss import *


class Button(Sprite):

    def __init__(self, textures, position):
        Sprite.__init__(self, textures[0], position)
        self.textures = textures
        self._visible = True
        topleft_pos = self.position[0] - self.texture.half_width, self.position[1] - self.texture.half_height
        self._rect = Rect(topleft_pos, (self.texture.width, self.texture.height))

        self._buttonDown = False
        self._mouseOverButton = False
        self._lastMouseDownOverButton = False

        self.looper = 0.0

    def draw(self, position=None, rotation=0.0, origin=(0, 0), scale=1, color=Color.WHITE):
        if self._visible:
            if self._buttonDown:
                self.texture = self.textures[1]
            elif self._mouseOverButton:
                self.looper += 0.01
                if self.looper > 1.0:
                    self.looper = 0.0
                rotation = Gloss.smooth_step2(-3, 3, self.looper)
                self.texture = self.textures[2]
            else:
                self.texture = self.textures[0]
            Sprite.draw(self, position, rotation, origin, scale, color)

    def handle_event(self, event_obj):
        if event_obj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN) or not self._visible:
            return []

        retVal = []

        hasExited = False
        if not self._mouseOverButton and self._rect.collidepoint(event_obj.pos):
            # mouse entered the button
            self._mouseOverButton = True
            retVal.append('enter')
        elif self._mouseOverButton and not self._rect.collidepoint(event_obj.pos):
            # mouse exited the button
            self._mouseOverButton = False
            hasExited = True

        if self._rect.collidepoint(event_obj.pos):
            # mouse event happened over the button
            if event_obj.type == MOUSEMOTION:
                retVal.append('move')
            elif event_obj.type == MOUSEBUTTONDOWN:
                self._buttonDown = True
                self._lastMouseDownOverButton = True
                retVal.append('down')
        else:
            if event_obj.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
                # Mouse up/down event happened off the button, no mouseClick()
                self._lastMouseDownOverButton = False

        doMouseClick = False
        if event_obj.type == MOUSEBUTTONUP:
            if self._lastMouseDownOverButton:
                doMouseClick = True
            self._lastMouseDownOverButton = False

            if self._buttonDown:
                self._buttonDown = False
                retVal.append('up')

            if doMouseClick:
                self._buttonDown = False
                retVal.append('click')

        if hasExited:
            retVal.append('exit')

        return retVal