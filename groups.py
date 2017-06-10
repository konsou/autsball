# -*- coding: utf8 -*-
import pygame

# Sprite-ryhmät
PlayerGroup = pygame.sprite.Group()
LevelGroup = pygame.sprite.Group()
BulletGroup = pygame.sprite.Group()
BallGroup = pygame.sprite.Group()
PickupGroup = pygame.sprite.Group()
EffectGroup = pygame.sprite.Group()
TextGroup = pygame.sprite.Group()


def empty_groups():
    LevelGroup.empty()
    BallGroup.empty()
    PlayerGroup.empty()
    BulletGroup.empty()
    EffectGroup.empty()
    TextGroup.empty()
