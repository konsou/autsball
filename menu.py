# -*- coding: utf8 -*-
import pygame
import game
import menu_background_action
import music
import effect
import json
from server import Server
from client import Client
from pygame.locals import *
from colors import *
from constants import *
from assets import assets, load_assets
from ui_components import Button, ButtonGroup, LabelImageText, Checkbox, CheckboxGroup, Slider


def debug_run():
    window = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))
    pygame.display.set_caption("AUTSBall")
    clock = pygame.time.Clock()

    window.fill(BLACK)

    # Ladataan settingsit
    # TODO: Siirrä asetusten lataus assettien latauksen kanssa samaan?
    Settings.load()

    # Groupit
    static_visual_components_group = pygame.sprite.Group()
    music_player_group = pygame.sprite.Group()
    main_menu_group = ButtonGroup()
    settings_group = pygame.sprite.Group()
    ready_lobby_group = pygame.sprite.Group()
    player_menu_group = pygame.sprite.Group()

    # Music
    # HUOM! Inittien järjestys tärkeä!
    # 1) mixerin pre-init
    # 2) pygamen init
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
    pygame.init()
    music_player = music.MusicPlayer(pos='bottomright', screen='menu', group=music_player_group)
    music_player.volume = Settings.data['music_volume']
    if Settings.data['music_on']:
        music_player.play()

    # Assettien esilataus
    load_assets(window)

    # Logo
    logo_sprite = pygame.sprite.Sprite()
    logo_sprite.image = assets['gfx/AUTSBall_Logo.png']
    logo_sprite.rect = logo_sprite.image.get_rect()
    logo_sprite.rect.center = (400, 110)
    static_visual_components_group.add(logo_sprite)
    static_visual_components_group.draw(window)

    # Buttons
    practice_button = Button(Rect(275, 250, 200, 50), surface_images=['gfx/UI_practice_button_normal.png',
                                                                      'gfx/UI_practice_button_down.png',
                                                                      'gfx/UI_practice_button_highlight.png'])
    multiplayer_button = Button(Rect(275, 310, 270, 50), surface_images=['gfx/UI_multiplayer_button_normal.png',
                                                                         'gfx/UI_multiplayer_button_down.png',
                                                                         'gfx/UI_multiplayer_button_highlight.png'])
    player_button = Button(Rect(285, 375, 270, 50), surface_images=['gfx/UI_player_button_normal.png',
                                                                         'gfx/UI_player_button_down.png',
                                                                         'gfx/UI_player_button_highlight.png'])
    settings_button = Button(Rect(275, 430, 195, 50), surface_images=['gfx/UI_settings_button_normal.png',
                                                                      'gfx/UI_settings_button_down.png',
                                                                      'gfx/UI_settings_button_highlight.png'])
    quit_button = Button(Rect(275, 490, 195, 50), surface_images=['gfx/UI_quit_button_normal.png',
                                                                  'gfx/UI_quit_button_down.png',
                                                                  'gfx/UI_quit_button_highlight.png'])
    main_menu_group.add(practice_button)
    main_menu_group.add(multiplayer_button)
    main_menu_group.add(player_button)
    main_menu_group.add(settings_button)
    main_menu_group.add(quit_button)

    #MultiplayerLobby
    create_game_button = Button(Rect(50, 200, 250, 70), 'Create')
    join_game_button = Button(Rect(50, 300, 250, 70), 'Join')
    back_from_lobby_button = Button(Rect(50, 480, 250, 70), 'Main Menu')

    #ReadyLobby
    LabelImageText(group=ready_lobby_group, image_text='ready', position=(155, 400))
    ready_checkbox = Checkbox(group=ready_lobby_group, checked=False, position=(300, 405))
    start_game_button = Button(Rect(50, 300, 250, 70), 'Start')
    main_menu_from_ready_lobby_button = Button(Rect(50, 480, 250, 70), 'Main Menu')

    #Player menu
    settings_background = assets['gfx/UI_settings_background.png']
    LabelImageText(group=settings_group, image_text='ready', position=(250, 40))
    LabelImageText(group=settings_group, image_text='ready', position=(100, 160))

    ship_selection_checkbox_group = CheckboxGroup()
    ship_selection_1_checkbox = Checkbox(group=player_menu_group, checked=False, position=(60, 385),
                                    checkbox_group=ship_selection_checkbox_group)
    ship_selection_2_checkbox = Checkbox(group=player_menu_group, checked=False, position=(130, 385),
                                    checkbox_group=ship_selection_checkbox_group)
    ship_selection_3_checkbox = Checkbox(group=player_menu_group, checked=False, position=(220, 385),
                                    checkbox_group=ship_selection_checkbox_group)
    ship_selection_4_checkbox = Checkbox(group=player_menu_group, checked=True, position=(310, 385),
                                     checkbox_group=ship_selection_checkbox_group)
    ship_selection_5_checkbox = Checkbox(group=player_menu_group, checked=False, position=(400, 385),
                                    checkbox_group=ship_selection_checkbox_group)
    ship_selection_6_checkbox = Checkbox(group=player_menu_group, checked=False, position=(490, 385),
                                    checkbox_group=ship_selection_checkbox_group)
    ship_selection_7_checkbox = Checkbox(group=player_menu_group, checked=True, position=(590, 385),
                                     checkbox_group=ship_selection_checkbox_group)

    ship_selection_checkbox_group.set_checked_index(Settings.data['graphic_quality'])
    player_back_button = Button(rect=Rect(100, 475, 90, 60), surface_images=['gfx/UI_back_button_normal.png',
                                                                               'gfx/UI_back_button_down.png',
                                                                               'gfx/UI_back_button_highlight.png'])

    # player_name_field = Input_box()
    screen = pygame.display.set_mode((800, 600))


    active_mode = Modes.MainMenu
    practice_game = None
    multiplayer_game = None
    client_wait_for_player_data_after_start = False

    # Background action
    background_action = menu_background_action.BackgroundAction(window, darken=1)

    # Settings menu
    settings_background = assets['gfx/UI_settings_background.png']
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

    # Multiplayer stuff
    server_object = None
    client_object = None

    running = True
    while running:

        for event in pygame.event.get():
            if active_mode == Modes.MainMenu:
                if 'click' in practice_button.handleEvent(event):
                    active_mode = Modes.Practice
                    window.fill(BLACK)
                    # Lopetetaan background action
                    background_action.destroy()
                    del background_action
                    music_player.stop()

                    practice_game = game.AUTSBallGame(window, level_name='Vertical Challenge')
                    practice_game.add_player(0, team='red', ship_name='Muumi')
                    practice_game.add_player(1, team='green')
                    practice_game.add_player(2, team='red')
                    practice_game.add_player(3, team='green')
                    practice_game.start()
                if 'click' in multiplayer_button.handleEvent(event):
                    active_mode = Modes.MultiplayerLobby
                    window.fill(BLACK)
                if 'click' in player_button.handleEvent(event):
                    active_mode = Modes.PlayerMenu
                    window.fill(BLACK)
                if 'click' in settings_button.handleEvent(event):
                    active_mode = Modes.SettingsMenu
                if 'click' in quit_button.handleEvent(event):
                    running = False
            if active_mode == Modes.SettingsMenu:
                if 'click' in settings_back_button.handleEvent(event):
                    active_mode = Modes.MainMenu
                if 'click' in music_checkbox.handleEvent(event):
                    # Tallennetaan arvo settings-tiedostoon
                    Settings.data['music_on'] = music_checkbox.checked
                    Settings.save()
                    if music_checkbox.checked:
                        music_player.play()
                    else:
                        music_player.stop()
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
                        del practice_game
                        active_mode = Modes.MainMenu
                        window.fill(BLACK)
                        background_action = menu_background_action.BackgroundAction(window=window, darken=1)
                        static_visual_components_group.draw(window)
                        #music_player = music.MusicPlayer(pos='bottomright', screen='menu', group=music_player_group)
                        if Settings.data['music_on']:
                            music_player.play()
                            music_player.screen = 'menu'
            if event.type == pygame.QUIT:
                running = False
            if event.type == music.MUSIC_FINISHED:
                music_player.next()

            if active_mode == Modes.MultiplayerLobby:
                if 'click' in back_from_lobby_button.handleEvent(event):
                    active_mode = Modes.MainMenu
                    window.fill(BLACK)

                if 'click' in create_game_button.handleEvent(event):
                    active_mode = Modes.ReadyLobby
                    window.fill(BLACK)
                    server_object = Server()

                if 'click' in join_game_button.handleEvent(event):
                    client_object = Client()

                    while not client_object.try_to_join_server(clock):
                        pass

                    window.fill(BLACK)
                    active_mode = Modes.ReadyLobby

                if 'click' in multiplayer_button.handleEvent(event):
                    active_mode = Modes.MultiplayerLobby
                    #tähän pelaajan nimen kysely
                    #window.fill(BLACK)
                if 'click' in quit_button.handleEvent(event):
                    running = False

        if active_mode == Modes.MainMenu:
            window.fill(0)

            background_action.update()
            music_player_group.update()

            static_visual_components_group.draw(window)
            main_menu_group.draw(window)
            music_player_group.draw(window)

            effect.antialiasing(window, graphic_quality=Settings.data['graphic_quality'])

            pygame.display.update()
            clock.tick(GRAPHICS_FPS)
        elif active_mode == Modes.SettingsMenu:
            window.fill(0)

            background_action.update()
            music_player_group.update()

            window.blit(settings_background, (0, 0))

            settings_group.draw(window)
            settings_back_button.draw(window)
            music_player_group.draw(window)

            effect.antialiasing(window, graphic_quality=Settings.data['graphic_quality'])

            pygame.display.update()
            clock.tick(GRAPHICS_FPS)
        elif active_mode == Modes.Practice:
            practice_game.update()

        elif active_mode == Modes.PlayerMenu:
            if 'click' in player_back_button.handleEvent(event):
                active_mode = Modes.MainMenu

            window.fill(0)

            background_action.update()
            music_player_group.update()

            window.blit(settings_background, (0, 0))

            player_menu_group.draw(window)
            player_back_button.draw(window)
            music_player_group.draw(window)

           # effect.antialiasing(window, graphic_quality=Settings.data['graphic_quality'])

            pygame.display.update()
            clock.tick(GRAPHICS_FPS)

        elif active_mode == Modes.MultiplayerLobby:
            window.fill(0)

            background_action.update()
            music_player_group.update()
            static_visual_components_group.draw(window)

            create_game_button.draw(window)
            join_game_button.draw(window)
            back_from_lobby_button.draw(window)

            pygame.display.update()
            clock.tick(GRAPHICS_FPS)

        elif active_mode == Modes.ReadyLobby:
            window.fill(0)

            # Badfix
            try:
                background_action.update()
            except UnboundLocalError:
                pass
            music_player_group.update()
            static_visual_components_group.draw(window)

            ready_lobby_group.draw(window)
            if server_object is not None:
                start_game_button.draw(window)
                main_menu_from_ready_lobby_button.draw(window)
            else:
                main_menu_from_ready_lobby_button.draw(window)

            if 'click' in main_menu_from_ready_lobby_button.handleEvent(event):
                active_mode = Modes.MainMenu
                window.fill(BLACK)

            if server_object is not None:
                if 'click' in start_game_button.handleEvent(event):
                    if server_object is not None:
                        active_mode = Modes.MultiplayerGame
                        # Lopetetaan background action
                        background_action.destroy()
                        del background_action
                        music_player.stop()
                        window.fill(BLACK)
                        pygame.display.flip()

                        multiplayer_game = game.AUTSBallGame(window)
                        server_object.start_game(multiplayer_game, clock)

            if server_object is not None:
                server_object.update(clock)
            elif client_object is not None:
                if client_object.wait_for_server_start_game() and not client_wait_for_player_data_after_start:
                    # Lopetetaan background action
                    background_action.destroy()
                    del background_action
                    music_player.stop()

                    multiplayer_game = game.AUTSBallGame(window, client=True)
                    multiplayer_game.local_player_id = client_object.client_id
                    client_wait_for_player_data_after_start = True
                elif client_wait_for_player_data_after_start:
                    if client_object.wait_for_player_data_after_start(multiplayer_game):
                        window.fill(BLACK)

                        multiplayer_game.start()
                        active_mode = Modes.MultiplayerGame

            if 'click' in ready_checkbox.handleEvent(event):
                pass

            pygame.display.update()
            clock.tick(GRAPHICS_FPS)

        elif active_mode == Modes.MultiplayerGame:
            if server_object is not None:
                server_object.update(clock)
                #multiplayer_game.update()
            elif client_object is not None:
                client_object.send_input()
                try:
                    server_updates = client_object.get_server_updates()[0]
                except TypeError:
                    server_updates = None
                # print server_updates
                multiplayer_game.update(server_updates=server_updates)
                clock.tick(GRAPHICS_FPS)

    pygame.quit()

if __name__ == '__main__':
    debug_run()
