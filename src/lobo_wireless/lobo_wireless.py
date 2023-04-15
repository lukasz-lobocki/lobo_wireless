#  Copyright (c) 2023 Lukasz Lobocki

import time
import network

DEBUG = False


class Wireless:
    """Implements wireless network controlling interface"""

    def __init__(self, ssid: str, password: str, attempts: int = 5, wait_loops: int = 5):
        assert type(ssid) is str and 2 <= len(ssid) <= 32, "ssid must be 2 <= len(str) <=32"
        assert type(password) is str, "password must be string"
        assert type(attempts) is int and 1 <= attempts <= 9, "attempts must be 1 <= int <= 9"
        assert type(wait_loops) is int and 1 <= wait_loops <= 9, "wait_loops must be 1 <= int <= 9"

        """ Instantiate wireless interface """
        self._wlan = network.WLAN(network.STA_IF)
        self._wlan.active(False)

        self._ssid = ssid
        self._password = password
        self._attempts = attempts
        self._wait_loops = wait_loops

        self._wlan.active(True)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(ssid={self._ssid})"

    @property
    def isconnected(self) -> bool:
        """
        Get connection status
        :return: Is wireless network connected
        """
        return self._wlan.isconnected()

    @property
    def wlan(self):
        """
        Get the wlan object
        :return: wlan object
        """
        return self._wlan

    @property
    def status(self) -> str:
        """
        Get the wlan status
        :return: message
        """
        return status_message(self._wlan.status())

    @property
    def ssid(self) -> str:
        """
        Get the SSID
        :return: Network name
        """
        return self._ssid

    @ssid.setter
    def ssid(self, ssid: str):
        """
        Set the SSID
        :param ssid: Network name
        """
        assert type(ssid) is str and 2 <= len(ssid) <= 32, "ssid must be 2 <= str <=32"
        self._ssid = ssid

    @property
    def password(self) -> None:
        """
        Get the password
        :return: None
        """
        return None

    @password.setter
    def password(self, password: str):
        """
        Set the password
        :param password: Network password
        """
        assert type(password) is str, "password must be string"
        self._password = password

    @property
    def attempts(self) -> int:
        """
        Get the number of connection attempts
        :return: Number of connection attempts
        """
        return self._attempts

    @attempts.setter
    def attempts(self, attempts: int):
        """
        Set the number of connection attempts
        :param attempts: Number of connection attempts
        """
        assert type(attempts) is int and 1 <= attempts <= 9, "attempts must be 1 <= int <= 9"
        self._attempts = attempts

    @property
    def wait_loops(self) -> int:
        """
        Get the number of wait loops
        :return: Number of wait loops
        """
        return self._wait_loops

    @wait_loops.setter
    def wait_loops(self, wait_loops: int):
        """
        Set the number of wait loops
        :param wait_loops: Number of wait loops
        """
        assert type(wait_loops) is int and 1 <= wait_loops <= 9, "wait_loops must be 1 <= int <= 9"
        self._wait_loops = wait_loops

    def available_wlans(self) -> list[tuple[bytes, bytes, int, int, int, bool]]:
        """
        Get available wireless networks
        :rtype: list
        :return: Available wireless networks [(ssid, bssid, channel, RSSI, security, hidden)]
        """
        # Wake up
        _wa = self._wlan.active()
        if not _wa:
            self._wlan.active(True)
            time.sleep(1)

        _ws: list | tuple = self._wlan.scan()

        # Reinstate state
        if not _wa:
            self._wlan.active(False)

        return _ws

    def connect(self) -> list[str]:
        """
        Connect to wireless network
        :return: Connection messages
        """
        """ Seconds of sleep per attempt"""
        _ATTEMPT_SLEEP = 15
        """Seconds of sleep per wait"""
        _WAIT_SLEEP = 7

        _output: list[str] = []

        # Nothing to do, emit IP
        if self._wlan.isconnected():
            _output.append("{i}".format(i=self._wlan.ifconfig()[0]))
            return _output

        # Wake up
        self._wlan.active(True)
        time.sleep(1)

        for _a in range(self._attempts, 0, -1):
            _output.append("WLAN {a}".format(a=_a))
            DEBUG and print("WLAN {a}".format(a=_a))

            # Attempt connection
            try:
                self._wlan.connect(self._ssid, self._password)
            except OSError as e:
                _output.append("{}. Probably wrong network password".format(e.args[0]))
                return _output
            time.sleep(1)

            # Wait l times or until connected
            for _l in (self._wait_loops, 0, -1):
                if self._wlan.isconnected():
                    # Emit IP, exit function
                    _output.append(" {i}".format(i=self._wlan.ifconfig()[0]))
                    return _output
                if _l > 1:
                    # Delay next loop
                    _output.append(" Wait {l}".format(l=_l))
                    DEBUG and print(" Wait {l}".format(l=_l))
                    time.sleep(_WAIT_SLEEP)

            # Unsuccessful, if still in the function
            _output.append("{m}".format(m=status_message(self._wlan.status())))
            DEBUG and print("{m}".format(m=status_message(self._wlan.status())))
            if _a > 1:
                time.sleep(_ATTEMPT_SLEEP)

        # Unsuccessful, if still in the function
        _output.append("WLAN connection failed")
        return _output

    def disconnect(self):
        """
        Disconnect from wireless network
        """
        if self._wlan.isconnected():
            self._wlan.disconnect()
            self._wlan.active(False)


def status_message(status: int) -> str:
    """
    Get status description
    :param status: Status code
    :return: Status description
    """
    _out = {}

    """ Messages dictionary "[s for s in dir(network) if "STAT_" in s] """
    _stats = [s for s in dir(network) if "STAT_" in s]

    for s in _stats:
        _out[getattr(network, s)] = s[5:]

    return _out.get(status, "ERROR {}?".format(status))


if __name__ == "__main__":
    DEBUG = True
    _wlan = Wireless(ssid=r"KTLT9000", password=r"enter-password-here")
    assert type(_wlan) is Wireless, "wlan is not instantiated"
    _available_wlans = _wlan.available_wlans()
    assert type(_available_wlans) is list
    print(_available_wlans)
    print(_wlan.connect())
    assert _wlan.isconnected is True, "wireless network not connected"
    print("assertion tests passed")
