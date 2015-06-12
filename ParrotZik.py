import sys
if sys.platform == "darwin":
    import lightblue
else:
    import bluetooth

import ParrotProtocol
from BeautifulSoup import BeautifulSoup

class ParrotZik(object):
    def __init__(self, addr=None):
        uuids = ["0ef0f502-f0ee-46c9-986c-54ed027807fb",
                 "8B6814D3-6CE7-4498-9700-9312C1711F63"]

        if sys.platform == "darwin":
            service_matches = lightblue.findservices(
                name="Parrot RFcomm service", addr=addr)
        else:
            for uuid in uuids:
                service_matches = bluetooth.find_service(uuid=uuid,
                                                         address=addr)
                if service_matches:
                    break

        if len(service_matches) == 0:
            print "Failed to find Parrot Zik RFCOMM service"
            self.sock = ""
            return

        if sys.platform == "darwin":
            first_match = service_matches[0]
            port = first_match[1]
            name = first_match[2]
            host = first_match[0]
        else:
            first_match = service_matches[0]
            port = first_match["port"]
            name = first_match["name"]
            host = first_match["host"]

        print "Connecting to \"%s\" on %s" % (name, host)

        if sys.platform == "darwin":
            self.sock = lightblue.socket()
        else:
            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.connect((host, port))

        self.sock.send('\x00\x03\x00')
        data = self.sock.recv(1024)

        self.BatteryLevel = 100
        self.BatteryCharging = False

    @property
    def battery_state(self):
        data = self.get("/api/system/battery/get")
        return data.answer.system.battery["state"]

    @property
    def battery_level(self):
        data = self.get("/api/system/battery/get")
        try:
            if data.answer.system.battery["level"] != '':
                self.BatteryLevel = data.answer.system.battery["level"]
            if data.answer.system.battery["state"] == 'charging':
                self.BatteryCharging = True
            else:
                self.BatteryCharging = False
        except Exception:
            pass

        try:
            print "notification received" + data.notify["path"]
        except Exception:
            pass

        return self.BatteryLevel

    @property
    def version(self):
        data = self.get("/api/software/version/get")
        try:
            return data.answer.software["version"]
        except KeyError:
            return data.answer.software['sip6']

    @property
    def friendly_name(self):
        data = self.get("/api/bluetooth/friendlyname/get")
        return data.answer.bluetooth["friendlyname"]

    @property
    def auto_connect(self):
        data = self.get("/api/system/auto_connection/enabled/get")
        return self._result_to_bool(
            data.answer.system.auto_connection["enabled"])

    @auto_connect.setter
    def auto_connect(self, arg):
        self.set("/api/system/auto_connection/enabled/set", arg)

    @property
    def anc_phone_mode(self):
        data = self.get("/api/system/anc_phone_mode/enabled/get")
        return self._result_to_bool(
            data.answer.system.anc_phone_mode["enabled"])

    @property
    def noise_cancel(self):
        data = self.get("/api/audio/noise_cancellation/enabled/get")
        try:
            return self._result_to_bool(
                data.answer.audio.noise_cancellation["enabled"])
        except AttributeError:
            return False

    @noise_cancel.setter
    def noise_cancel(self, arg):
        self.set("/api/audio/noise_cancellation/enabled/set", arg)

    @property
    def lou_reed_mode(self):
        data = self.get("/api/audio/specific_mode/enabled/get")
        try:
            return self._result_to_bool(
                data.answer.audio.specific_mode["enabled"])
        except TypeError:
            return False

    @lou_reed_mode.setter
    def lou_reed_mode(self, arg):
        self.set("/api/audio/specific_mode/enabled/set", arg)

    @property
    def concert_hall(self):
        data = self.get("/api/audio/sound_effect/enabled/get")
        try:
            return self._result_to_bool(
                data.answer.audio.sound_effect["enabled"])
        except AttributeError:
            return False

    @concert_hall.setter
    def concert_hall(self, arg):
        self.set("/api/audio/sound_effect/enabled/set", arg)

    def _result_to_bool(self, result):
        if result == "true":
            return True
        elif result == "false":
            return False
        else:
            raise AssertionError(result)

    def get(self, message):
        message = ParrotProtocol.getRequest(message)
        return self.send_message(message)

    def set(self, message, arg):
        message = ParrotProtocol.setRequest(message, str(arg).lower())
        return self.send_message(message)

    def send_message(self, message):
        try:
            self.sock.send(str(message))
        except Exception:
            self.sock = ""
            return
        if sys.platform == "darwin":
            data = self.sock.recv(30)
        else:
            data = self.sock.recv(7)
        data = self.sock.recv(1024)
        data = BeautifulSoup(data)
        return data

    def close(self):
        self.sock.close()
