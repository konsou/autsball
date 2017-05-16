# -*- coding: utf8 -*-
import pygame
import game
import menu_background_action
import music
import effect
import groups
from pygame.locals import *
from colors import *
from constants import *
from ui_components import Button, ButtonGroup, LabelImageText, Checkbox, CheckboxGroup, Slider


def debug_run():
    window = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))
    pygame.display.set_caption("Menu test")
    clock = pygame.time.Clock()

    window.fill((0, 0, 0))

    static_visual_components_group = pygame.sprite.Group()
    music_player_group = pygame.sprite.Group()
    main_menu_group = ButtonGroup()
    settings_group = pygame.sprite.Group()

    # Logo
    logo_sprite = pygame.sprite.Sprite()
    logo_sprite.image = pygame.image.load('gfx/AUTSBall_logo.png').convert_alpha()
    logo_sprite.rect = logo_sprite.image.get_rect()
    logo_sprite.rect.center = (400, 110)
    static_visual_components_group.add(logo_sprite)
    static_visual_components_group.draw(window)

    # Buttons
    practice_button = Button(Rect(275, 250, 250, 70), 'Practice flight')
    multiplayer_button = Button(Rect(275, 325, 250, 70), 'Multiplayer')
    settings_button = Button(Rect(275, 400, 250, 70), 'Settings')
    quit_button = Button(Rect(275, 475, 250, 70), 'Quit')
    main_menu_group.add(practice_button)
    main_menu_group.add(multiplayer_button)
    main_menu_group.add(settings_button)
    main_menu_group.add(quit_button)

    active_mode = 'main_menu'
    practice_game = None

    # Music
    pygame.mixer.init()
    music_player = music.MusicPlayer(pos='bottomright', screen='menu', group=music_player_group)
    music_player.play()

    # Background action
    background_action = menu_background_action.BackgroundAction()
    # Tämä tummentaa tausta-actionin
    darken_surface = pygame.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]))
    darken_surface.set_alpha(128)

    # Settings menu
    LabelImageText(group=settings_group, image_text='settings', position=(250, 30))
    LabelImageText(group=settings_group, image_text='music', position=(100, 130))
    music_checkbox = Checkbox(group=settings_group, checked=True, position=(350, 130))
    LabelImageText(group=settings_group, image_text='volume', position=(140, 170))
    music_volume_slider = Slider(group=settings_group, position=(350, 180), value=music_player.volume)
    LabelImageText(group=settings_group, image_text='sounds', position=(100, 210))
    sounds_checkbox = Checkbox(group=settings_group, checked=True, position=(350, 210))
    LabelImageText(group=settings_group, image_text='volume', position=(140, 250))
    sound_volume_slider = Slider(group=settings_group, position=(350, 260), value=1.0)
    #LabelImageText(group=settings_group, image_text='quality', position=(100, 330))
    LabelImageText(group=settings_group, image_text='effects', position=(100, 350))
    LabelImageText(group=settings_group, image_text='off', position=(290, 310))
    LabelImageText(group=settings_group, image_text='low', position=(380, 310))
    LabelImageText(group=settings_group, image_text='med', position=(470, 310))
    LabelImageText(group=settings_group, image_text='high', position=(570, 310))
    effects_checkbox_group = CheckboxGroup()
    effects_off_checkbox = Checkbox(group=settings_group, checked=False, position=(310, 355),
                                    checkbox_group=effects_checkbox_group)
    effects_low_checkbox = Checkbox(group=settings_group, checked=False, position=(400, 355),
                                    checkbox_group=effects_checkbox_group)
    effects_med_checkbox = Checkbox(group=settings_group, checked=True, position=(490, 355),
                                    checkbox_group=effects_checkbox_group)
    effects_high_checkbox = Checkbox(group=settings_group, checked=False, position=(590, 355),
                                     checkbox_group=effects_checkbox_group)
    settings_back_button = Button(Rect(275, 475, 250, 70), 'Back')

    running = True
    while running:

        for event in pygame.event.get():
            if active_mode == 'main_menu':
                if 'click' in practice_button.handleEvent(event):
                    #print('practice button clicked')
                    active_mode = 'practice'
                    window.fill(BLACK)
                    # Lopetetaan background action
                    background_action.kill_me()
                    del background_action
                    music_player.stop()
                    #del music_player

                    practice_game = game.AUTSBallGame()
                    practice_game.add_player(0, team='red', ship_name='Rocket')
                    practice_game.add_player(1, team='green')
                    practice_game.add_player(2, team='red')
                    practice_game.add_player(3, team='green')
                    practice_game.start()
                    # music_player.stop()
                if 'click' in multiplayer_button.handleEvent(event):
                    print('multiplayer button clicked')
                if 'click' in settings_button.handleEvent(event):
                    active_mode = 'settings_menu'
                if 'click' in quit_button.handleEvent(event):
                    running = False
            if active_mode == 'settings_menu':
                if 'click' in settings_back_button.handleEvent(event):
                    active_mode = 'main_menu'
                if 'click' in music_checkbox.handleEvent(event):
                    # TODO: talleta arvo johonkin pysyvästi, että vaikuttaa pelin puolellakin ja uudelleen käynnistyksen jälkeen
                    if music_checkbox.checked:
                        music_player.play()
                    else:
                        music_player.stop()
                if 'drag' in music_volume_slider.handleEvent(event):
                    # TODO: talleta voimakkuusarvo johonkin
                    music_player.volume = music_volume_slider.value

                if 'click' in sounds_checkbox.handleEvent(event):
                    # TODO: disable/enable sound effects
                    pass
                if 'drag' in sound_volume_slider.handleEvent(event):
                    # TODO: talleta voimakkuusarvo johonkin
                    # TODO: muuta kaikkien sound effectien voimakkuus
                    pass

                if 'click' in effects_off_checkbox.handleEvent(event):
                    # TODO: muuta grafiikka-asetus vastaavaksi
                    pass
                if 'click' in effects_low_checkbox.handleEvent(event):
                    # TODO: muuta grafiikka-asetus vastaavaksi
                    pass
                if 'click' in effects_med_checkbox.handleEvent(event):
                    # TODO: muuta grafiikka-asetus vastaavaksi
                    pass
                if 'click' in effects_high_checkbox.handleEvent(event):
                    # TODO: muuta grafiikka-asetus vastaavaksi
                    pass

            if active_mode == 'practice':
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        practice_game.destroy()
                        #groups.empty_groups()
                        del practice_game
                        active_mode = 'main_menu'
                        window.fill(BLACK)
                        background_action = menu_background_action.BackgroundAction()
                        static_visual_components_group.draw(window)
                        #music_player = music.MusicPlayer(pos='bottomright', screen='menu', group=music_player_group)
                        music_player.play()
                        music_player.set_screen('menu')
            if event.type == pygame.QUIT:
                running = False
            if event.type == music.MUSIC_FINISHED:
                music_player.next()

        if active_mode == 'main_menu':
            window.fill(0)

            menu_background_action.background_group.update()
            music_player_group.update()

            menu_background_action.background_group.draw(window)
            window.blit(darken_surface, (0, 0))

            static_visual_components_group.draw(window)
            main_menu_group.draw(window)
            music_player_group.draw(window)

            pygame.display.update()
            clock.tick(GRAPHICS_FPS)
        elif active_mode == 'settings_menu':
            window.fill(0)

            menu_background_action.background_group.update()
            music_player_group.update()

            menu_background_action.background_group.draw(window)
            window.blit(darken_surface, (0, 0))

            settings_group.draw(window)
            settings_back_button.draw(window)
            music_player_group.draw(window)

            if effects_high_checkbox.checked:
                effect.antialiasing(window)

            pygame.display.update()
            clock.tick(GRAPHICS_FPS)

        elif active_mode == 'practice':
            practice_game.update()

    pygame.quit()

if __name__ == '__main__':
    debug_run()
