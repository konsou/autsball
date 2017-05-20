# -*- coding: utf-8 -*-
import pygame


def force_play_sound(sound, loops=0):
    """ 
    Soitetaan määritetty ääni jos se on olemassa, pakotetaan sille kanava auki
    Kanavan auki pakottamisessa on se idea että jos on hirveesti ääniä jo soimassa niin uudet äänet soi silti
    loops = sama kuin pygame.mixer.Sound.play():n loops, eli:

    The loops argument controls how many times the sample will be repeated after being played the first time.
    A value of 5 means that the sound will be played once, then repeated five times, and so is played a total of
    six times. The default value (zero) means the Sound is not repeated, and so is only played once. If loops is
    set to -1 the Sound will loop indefinitely (though you can still call stop() to stop it).
    """
    if sound is not None:
        pygame.mixer.find_channel(True).play(sound, loops)
