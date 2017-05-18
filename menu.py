# -*- coding: utf8 -*-
import pygame
import game
import menu_background_action
import music
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

    # Ladataan settingsit
    # TODO: Siirrä asetusten lataus assettien latauksen kanssa samaan?
    Settings.load()

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

    active_mode = Modes.MainMenu
    practice_game = None

    # Music
    pygame.mixer.init()
    music_player = music.MusicPlayer(pos='bottomright', screen='menu', group=music_player_group)
    music_player.volume = Settings.data['music_volume']
    if Settings.data['music_on']:
        music_player.play()

    # Background action
    background_action = menu_background_action.BackgroundAction()
    # Tämä tummentaa tausta-actionin
    darken_surface = pygame.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]))
    darken_surface.set_alpha(128)

    # Settings menu
    settings_background = pygame.image.load('gfx/UI_settings_background.png').convert_alpha()
    LabelImageText(group=settings_group, image_text='settings', position=(250, 40))
    LabelImageText(group=settings_group, image_text='music', position=(100, 160))
    music_checkbox = Checkbox(group=settings_group, checked=Settings.data['music_on'], position=(350, 160))
    LabelImageText(group=settings_group, image_text='volume', position=(140, 200))
    music_volume_slider = Slider(group=settings_group, position=(350, 210), value=music_player.volume)
    LabelImageText(group=settings_group, image_text='sounds', position=(100, 240))
    sounds_checkbox = Checkbox(group=settings_group, checked=Settings.data['sounds_on'], position=(350, 240))
    LabelImageText(group=settings_group, image_text='volume', position=(140, 280))
    sound_volume_slider = Slider(group=settings_group, position=(350, 290), value=Settings.data['sound_volume'])
    LabelImageText(group=settings_group, image_text='effects', position=(100, 380))
    LabelImageText(group=settings_group, image_text='off', position=(290, 340))
    LabelImageText(group=settings_group, image_text='low', position=(380, 340))
    LabelImageText(group=settings_group, image_text='med', position=(470, 340))
    LabelImageText(group=settings_group, image_text='high', position=(570, 340))
    effects_checkbox_group = CheckboxGroup()
    effects_off_checkbox = Checkbox(group=settings_group, checked=False, position=(310, 385),
                                    checkbox_group=effects_checkbox_group)
    effects_low_checkbox = Checkbox(group=settings_group, checked=False, position=(400, 385),
                                    checkbox_group=effects_checkbox_group)
    effects_med_checkbox = Checkbox(group=settings_group, checked=False, position=(490, 385),
                                    checkbox_group=effects_checkbox_group)
    effects_high_checkbox = Checkbox(group=settings_group, checked=True, position=(590, 385),
                                     checkbox_group=effects_checkbox_group)
    effects_checkbox_group.set_checked_index(Settings.data['graphic_quality'])
    settings_back_button = Button(rect=Rect(100, 475, 90, 60), surface_images=['gfx/UI_back_button_normal.png',
                                                                                'gfx/UI_back_button_down.png',
                                                                                'gfx/UI_back_button_highlight.png'])

    running = True
    while running:

        for event in pygame.event.get():
            if active_mode == Modes.MainMenu:
                if 'click' in practice_button.handleEvent(event):
                    active_mode = Modes.Practice
                    window.fill(BLACK)
                    # Lopetetaan background action
                    background_action.kill_me()
                    del background_action
                    music_player.stop()

                    practice_game = game.AUTSBallGame()
                    practice_game.add_player(0, team='red', ship_name='Rocket')
                    practice_game.add_player(1, team='green')
                    practice_game.add_player(2, team='red')
                    practice_game.add_player(3, team='green')
                    practice_game.start()
                if 'click' in multiplayer_button.handleEvent(event):
                    print('multiplayer button clicked')
                    #active_mode = Modes.MultiplayerLobby
                if 'click' in settings_button.handleEvent(event):
                    active_mode = Modes.SettingsMenu
                if 'click' in quit_button.handleEvent(event):
                    running = False
            if active_mode == Modes.SettingsMenu:
                if 'click' in settings_back_button.handleEvent(event):
                    active_mode = Modes.MainMenu
                if 'click' in music_checkbox.handleEvent(event):
                    if music_checkbox.checked:
                        music_player.play()
                    else:
                        music_player.stop()
                    # Tallennetaan arvo settings-tiedostoon
                    Settings.data['music_on'] = music_checkbox.checked
                    Settings.save()
                for event_string in music_volume_slider.handleEvent(event):
                    if event_string is 'drag':
                        music_player.volume = music_volume_slider.value
                    if event_string is 'up':
                        # Tallennetaan arvo settings-tiedostoon
                        Settings.data['music_volume'] = music_volume_slider.value
                        Settings.save()

                if 'click' in sounds_checkbox.handleEvent(event):
                    # TODO: disable/enable sound effects

                    # Tallennetaan arvo settings-tiedostoon
                    Settings.data['sounds_on'] = sounds_checkbox.checked
                    Settings.save()
                for event_string in sound_volume_slider.handleEvent(event):
                    if event_string is 'drag':
                        # TODO: talleta voimakkuusarvo johonkin
                        # TODO: muuta kaikkien sound effectien voimakkuus
                        pass
                    if event_string is 'up':
                        # Tallennetaan arvo settings-tiedostoon
                        Settings.data['sound_volume'] = sound_volume_slider.value
                        Settings.save()
                if 'click' in effects_off_checkbox.handleEvent(event):
                    # TODO: muuta grafiikka-asetus vastaavaksi

                    # Tallennetaan arvo settings-tiedostoon
                    Settings.data['graphic_quality'] = 0
                    Settings.save()
                if 'click' in effects_low_checkbox.handleEvent(event):
                    # TODO: muuta grafiikka-asetus vastaavaksi

                    # Tallennetaan arvo settings-tiedostoon
                    Settings.data['graphic_quality'] = 1
                    Settings.save()
                if 'click' in effects_med_checkbox.handleEvent(event):
                    # TODO: muuta grafiikka-asetus vastaavaksi

                    # Tallennetaan arvo settings-tiedostoon
                    Settings.data['graphic_quality'] = 2
                    Settings.save()
                if 'click' in effects_high_checkbox.handleEvent(event):
                    # TODO: muuta grafiikka-asetus vastaavaksi

                    # Tallennetaan arvo settings-tiedostoon
                    Settings.data['graphic_quality'] = 3
                    Settings.save()

            if active_mode == Modes.Practice:
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        practice_game.destroy()
                        #groups.empty_groups()
                        del practice_game
                        active_mode = Modes.MainMenu
                        window.fill(BLACK)
                        background_action = menu_background_action.BackgroundAction()
                        static_visual_components_group.draw(window)
                        #music_player = music.MusicPlayer(pos='bottomright', screen='menu', group=music_player_group)
                        if Settings.data['music_on']:
                            music_player.play()
                            music_player.set_screen('menu')
            if event.type == pygame.QUIT:
                running = False
            if event.type == music.MUSIC_FINISHED:
                music_player.next()

        if active_mode == Modes.MainMenu:
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
        elif active_mode == Modes.SettingsMenu:
            window.fill(0)

            menu_background_action.background_group.update()
            music_player_group.update()

            menu_background_action.background_group.draw(window)
            window.blit(darken_surface, (0, 0))
            window.blit(settings_background, (0, 0))

            settings_group.draw(window)
            settings_back_button.draw(window)
            music_player_group.draw(window)

            pygame.display.update()
            clock.tick(GRAPHICS_FPS)
        elif active_mode == Modes.Practice:
            practice_game.update()

    pygame.quit()

if __name__ == '__main__':
    debug_run()
