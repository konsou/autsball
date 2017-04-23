import math


class MoveVector:
    """ 
    Classi johon voi tallettaa liikevektorin joko kulma- tai summamuodossa ja tekee konversiot automaattisesti.
    HUOM! Angle radiaaneina!
    
    Sisältää seuraavat metodit:
        -set_vx, set_vy, set_vx_vy - nämä asettaa vx/vy:n arvot (summamuoto)
        -get_vx, get_vy, get_vx_vy - nämä palauttaa vx/vy:n arvot (summamuoto)
        -set_magnitude, set_angle, set_magnitude_angle - nämä asettaa vektorin pituuden ja/tai kulman (kulmamuoto)
        -get_magnitude, get_angle, get_magnitude_angle - nämä palauttaa vektorin pituuden ja/tai kulman (kulmamuoto)
        -get_all - palauttaa vektorin arvot sekä summa- että kulmamuodossa
    
    Tässä on ideana että kun kutsutaan get_(arvo) niin toimii täten:
        -jos arvo on jo määritetty (esim. vx) niin palauttaa sen suoraan
        -jos arvoa ei ole määritetty (on None) niin laskee sen ja tallettaa - näin useampi get-kutsu peräkkäin ei 
         tee turhia uudelleenlaskentoja joka kerta
    
    Kun set-metodeita kutsutaan niin toimii täten:
        -jos asetetaan vx ja/tai vy niin asetetaan magnitude ja angle Noneksi
        -jos asetetaan magnitude ja/tai angle niin asetetaan vx ja vy Noneksi
        Näistä sitten tietää että Noneksi asetettu arvo pitää laskea uusiksi sitten jos sitä joskus haetaan
            
    TODO: joko tee parannuksia (dot product, metodit helpommille arvojen yhteenlaskuille) tai siirry käyttämään
          pygamen valmiita vektorijuttuja 
    TODO: samalla logiikalla kulman muutos asteisiin
    """
    def __init__(self, vx=None, vy=None, magnitude=None, angle=None):
        self.vx = vx
        self.vy = vy
        self.magnitude = magnitude
        self.angle = angle
        if vx is not None and vy is not None:
            pass
        elif magnitude is not None and angle is not None:
            pass
        else:
            self.vx, self.vy, self.magnitude, self.angle = 0, 0, 0, 0

    def _clear_magnitude_angle(self):
        self.magnitude = None
        self.angle = None

    def _clear_vx_vy(self):
        self.vx = None
        self.vy = None

    def _calculate_magnitude_angle(self):
        self.magnitude = math.hypot(self.vx, self.vy)
        self.angle = math.atan2(self.vy, self.vx)

    def _calculate_vx_vy(self):
        self.vx = math.cos(self.angle) * self.magnitude
        self.vy = math.sin(self.angle) * self.magnitude

    def set_vx_vy(self, vx, vy):
        self.vx = vx
        self.vy = vy
        self._clear_magnitude_angle()

    def set_vx(self, vx):
        self.vx = vx
        self._clear_magnitude_angle()

    def set_vy(self, vy):
        self.vy = vy
        self._clear_magnitude_angle()

    def set_magnitude_angle(self, magnitude, angle):
        self.magnitude = magnitude
        self.angle = angle
        self._clear_vx_vy()

    def set_magnitude(self, magnitude):
        self.magnitude = magnitude
        self._clear_vx_vy()

    def set_angle(self, angle):
        self.angle = angle
        self._clear_vx_vy()

    def get_vx_vy(self):
        if self.vx is None or self.vy is None:
            self._calculate_vx_vy()
        return (self.vx, self.vy)

    def get_vx(self):
        if self.vx is None or self.vy is None:
            self._calculate_vx_vy()
        return self.vx

    def get_vy(self):
        if self.vx is None or self.vy is None:
            self._calculate_vx_vy()
        return self.vy

    def get_magnitude_angle(self):
        if self.magnitude is None or self.angle is None:
            self._calculate_magnitude_angle()
        return self.magnitude, self.angle

    def get_magnitude(self):
        if self.magnitude is None or self.angle is None:
            self._calculate_magnitude_angle()
        return self.magnitude

    def get_angle(self):
        if self.magnitude is None or self.angle is None:
            self._calculate_magnitude_angle()
        return self.angle

    def get_all(self):
        if self.magnitude is None or self.angle is None:
            self._calculate_magnitude_angle()
        if self.vx is None or self.vy is None:
            self._calculate_vx_vy()
        return self.vx, self.vy, self.magnitude, self.angle

    def add_to_vx(self, value):
        self.vx = self.get_vx() + value
        self._clear_magnitude_angle()

    def add_to_vy(self, value):
        self.vy = self.get_vy() + value
        self._clear_magnitude_angle()

    def add_to_magnitude(self, value):
        self.magnitude = self.get_magnitude() + value
        self._clear_vx_vy()

    def add_to_angle(self, value):
        self.angle = self.get_angle() + value
        self._clear_vx_vy()

    def add_vector(self, vector):
        """ Lisää tähän vektoriin toisen Vector-objektin """
        self.add_to_vx(vector.get_vx())
        self.add_to_vy(vector.get_vy())