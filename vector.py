import math, pygame

class MoveVector:
    """ 
    Classi johon voi tallettaa liikevektorin joko kulma- tai summamuodossa ja tekee konversiot automaattisesti.
    HUOM! Angle radiaaneina!
    
    Sisältää seuraavat metodit:
        -set_vx, set_vy, set_vx_vy - nämä asettaa vx/vy:n arvot (summamuoto)
        -get_vx, get_vy, get_vx_vy - nämä palauttaa vx/vy:n arvot (summamuoto)
        -set_speed, set_direction, set_speed_direction - nämä asettaa vektorin pituuden ja/tai kulman (kulmamuoto)
        -get_speed, get_direction, get_speed_direction - nämä palauttaa vektorin pituuden ja/tai kulman (kulmamuoto)
        -get_all - palauttaa vektorin arvot sekä summa- että kulmamuodossa
        -add_to_vx(self, value): lisää vx:ään numeron
        -add_to_vy(self, value): lisää vy:hyn numeron
        -add_to_speed(self, value): lisää speediin numeron
        -add_to_direction(self, value): lisää directioniin numeron
        -add_vector(self, vector):  lisää tähän vektoriin toisen Vector-objektin
        -get_dot_product(self, vector): laskee tämän ja toisen vektorin pistetulon
        -normalize(self): Palauttaa vektorin, jolla on sama suunta mutta nopeus on 1 
        -normalize_ip(self):  Muuttaa vektorin nopeudeksi 1 pitäen suunnan samana (in-place)
    
    Tässä on ideana että kun kutsutaan get_(arvo) niin toimii täten:
        -jos arvo on jo määritetty (esim. vx) niin palauttaa sen suoraan
        -jos arvoa ei ole määritetty (on None) niin laskee sen ja tallettaa - näin useampi get-kutsu peräkkäin ei 
         tee turhia uudelleenlaskentoja joka kerta
    
    Kun set-metodeita kutsutaan niin toimii täten:
        -jos asetetaan vx ja/tai vy niin asetetaan speed ja direction Noneksi
        -jos asetetaan speed ja/tai direction niin asetetaan vx ja vy Noneksi
        Näistä sitten tietää että Noneksi asetettu arvo pitää laskea uusiksi sitten jos sitä joskus haetaan
            
    TODO: samalla logiikalla kulman muutos asteisiin
    """
    def __init__(self, vx=None, vy=None, speed=None, direction=None):
        # print("Creating vector with init values: vx, vy, speed, direction")
        # print(vx, vy, speed, direction)
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.direction = direction
        if (vx is None or vy is None) and (speed is None or direction is None):
            self.vx, self.vy, self.speed, self.direction = 0, 0, 0, 0

    def _clear_speed_direction(self):
        self.speed = None
        self.direction = None

    def _clear_vx_vy(self):
        self.vx = None
        self.vy = None

    def _calculate_speed_direction(self):
        self.speed = math.hypot(self.vx, self.vy)
        self.direction = math.atan2(self.vy, self.vx)

    def _calculate_vx_vy(self):
        self.vx = math.cos(self.direction) * self.speed
        self.vy = math.sin(self.direction) * self.speed

    def set_vx_vy(self, vx, vy):
        self.vx = vx
        self.vy = vy
        self._clear_speed_direction()

    def set_vx(self, vx):
        if self.vy is None:
            self._calculate_vx_vy()
        self.vx = vx
        self._clear_speed_direction()

    def set_vy(self, vy):
        if self.vx is None:
            self._calculate_vx_vy()
        self.vy = vy
        self._clear_speed_direction()

    def set_speed_direction(self, speed, direction):
        self.speed = speed
        self.direction = direction
        self._clear_vx_vy()

    def set_speed(self, speed):
        if self.direction is None:
            self._calculate_speed_direction()
        self.speed = speed
        self._clear_vx_vy()

    def set_direction(self, direction):
        if self.speed is None:
            self._calculate_speed_direction()
        self.direction = direction
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

    def get_speed_direction(self):
        if self.speed is None or self.direction is None:
            self._calculate_speed_direction()
        return self.speed, self.direction

    def get_speed(self):
        if self.speed is None or self.direction is None:
            self._calculate_speed_direction()
        return self.speed

    def get_direction(self):
        if self.speed is None or self.direction is None:
            self._calculate_speed_direction()
        return self.direction

    def get_all(self):
        if self.speed is None or self.direction is None:
            self._calculate_speed_direction()
        if self.vx is None or self.vy is None:
            self._calculate_vx_vy()
        return self.vx, self.vy, self.speed, self.direction

    def add_to_vx(self, value):
        self.vx = self.get_vx() + value
        self._clear_speed_direction()

    def add_to_vy(self, value):
        self.vy = self.get_vy() + value
        self._clear_speed_direction()

    def add_to_speed(self, value):
        self.speed = self.get_speed() + value
        self._clear_vx_vy()

    def add_to_direction(self, value):
        self.direction = self.get_direction() + value
        self._clear_vx_vy()

    def add_vector(self, vector):
        """ Lisää tähän vektoriin toisen Vector-objektin """
        self.add_to_vx(vector.get_vx())
        self.add_to_vy(vector.get_vy())
        self._clear_speed_direction()

    def get_dot_product(self, vector):
        """ Laskee kahden vektorin pistetulon """
        return (self.get_vx() * vector.get_vx()) + (self.get_vy() * vector.get_vy())

    def normalize(self):
        """ Palauttaa vektorin, jolla on sama suunta mutta nopeus on 1 """
        return MoveVector(speed=1, direction=self.get_direction())

    def normalize_ip(self):
        """ Muuttaa vektorin nopeudeksi 1 pitäen suunnan samana (in-place) """
        self.set_speed(1)
        self._clear_vx_vy()
