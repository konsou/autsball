import math


class MoveVector:
    """ 
    Classi johon voi tallettaa liikevektorin joko kulma- tai summamuodossa ja tekee konversiot automaattisesti.
    HUOM! Angle radiaaneina!
    Paitsi ettei oikein toimi ainakaan käytäntöön sovellettuna. Keksipä miten saa toimimaan kun olisi kätevä.
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
            # raise ValueError("x and y OR magnitude and angle need to be set!")

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