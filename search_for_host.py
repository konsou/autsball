# -*- coding: utf8 -*-
import socket


def search_for_host(port):
    """
    Yrittää etsiä hostia lähiverkosta annetusta portista
    Käy läpi kaikki viimeisen oktetin 254 osoitetta ja yrittää yhdistää jokaiseen niistä hyvin lyhyellä timeoutilla
    Aloittaa omasta IP:stä ja etsii siitä alkaen sekä ylös- että alaspäin (näin löytää todennäköisesti nopeiten)
    Palauttaa serverin IP:n jos se löytyi, muuten None
    """
    timeout = 0.05
    success = 0
    my_ip = get_my_ip()

    try:
        ipsplit = my_ip.split(".")
    # Tulee jos my_ip on None:
    except AttributeError:
        ipsplit = None

    if ipsplit is not None:
        # Tämä käy läpi kaikki viimeisen oktetin 254 IP-osoitetta
        # alkaen omasta IP:stä, lähimmät ensin
        for a in range(1, 128):  # 254 / 2 + 1
            ipup = int(ipsplit[3]) + (a - 1)
            ipdown = int(ipsplit[3]) - a
            if ipup > 254:
                ipup -= 254

            if ipdown < 1:
                ipdown += 254

            for b in range(1, 3):
                if b == 1:
                    host = ipsplit[0] + "." + ipsplit[1] + "." + ipsplit[2] + "." + str(ipup)
                else:
                    host = ipsplit[0] + "." + ipsplit[1] + "." + ipsplit[2] + "." + str(ipdown)

                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(timeout)
                    s.connect((host, port))
                    s.close()
                    success = 1
                except (OSError, socket.error):
                    try:
                        s.close()
                    except AttributeError:
                        pass

            if success == 1:
                break

    if success == 1:
        return host
    else:
        return None


def get_my_ip():
    """
    Yrittää saada tietoon clientin oman (lokaalin) IP:n ja palauttaa sen,. Jos ei onnistu, palauttaa None.
    Yritetään parilla kolmella eri taktiikalla että toimisi mahdollisimman hyvin eri platformeilla
    """
    my_ip = None

    # Yritys 1:
    try:
        my_ip = socket.gethostbyname(socket.gethostname())
    except OSError:
        pass

    # Yritys 2:
    if my_ip is None:
        try:
            my_ip = socket.gethostbyname(socket.getfqdn())
        except OSError:
            pass

    # Yritys 3:
    # (Yritetään luoda socket ja yhdistää sillä Googleen ja otetaan siitä oma ip)
    if my_ip is None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('62.115.64.115', 80))  # google.fi
            my_ip = s.getsockname()[0]
            s.close()
        except (OSError, IndexError, AttributeError):
            pass

    return my_ip
