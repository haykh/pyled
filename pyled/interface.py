from typing import Any
from .device import Device
from .commands import CMD


class Interface:
    def __init__(self):
        self.devices = [
            Device(i, port) for i, port in enumerate(Interface.find_ports())
        ]

    @staticmethod
    def find_ports() -> list[Any]:
        from serial.tools import list_ports

        ports = list_ports.comports()
        return [
            port
            for port in ports
            if port.vid == Device.FWK_VID and port.pid in Device.INPUTMODULE_PIDS
        ]

    @staticmethod
    def rgb2gray(pixel: tuple[int, int, int]) -> int:
        """
        Calculates the brightness of a pixel from an RGB triple.

        This function takes an RGB triple and calculates the brightness based on the average of the RGB values.
        It then applies a scaling factor to enhance the greyscale representation. The scaling factor is determined
        based on the calculated brightness value.

        Args:
            `pixel` (`tuple`): A tuple containing the RGB values of the pixel. Must be of length 3.

        Returns:
            `int`: The calculated brightness of the pixel after applying the scaling factor.

        Raises:
            `AssertionError`: If the length of the pixel tuple is not 3.

        """
        assert len(pixel) == 3
        assert all(0 <= x <= 255 for x in pixel)
        brightness = sum(pixel) / len(pixel)
        if brightness > 200:
            brightness = brightness
        elif brightness > 150:
            brightness = brightness * 0.8
        elif brightness > 100:
            brightness = brightness * 0.5
        elif brightness > 50:
            brightness = brightness
        else:
            brightness = brightness * 2
        return int(brightness)

    def __repr__(self):
        r = ""
        for dev in self.devices:
            r += f"{dev}\n"
        return r

    def paint(self, id: int, array: list[list[float]], brightness: int = 255) -> None:
        self.devices[id].paint(array, brightness)

    def display(self, id: int, array: list[list[bool]], brightness: int = 255) -> None:
        self.devices[id].display(array, brightness)

    def brightness(self, id: int, value: int) -> None:
        self.devices[id].brightness(value)

    def sleep(self, id: int) -> None:
        self.devices[id].sleep()

    def wake(self, id: int) -> None:
        self.devices[id].wake()

    def command(
        self, id: int, command: CMD, params=[], expect_response=False
    ) -> None | bytes:
        return self.devices[id].command(command, params, expect_response)
