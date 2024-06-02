from typing import Any, Callable
from .device import Device
from .commands import CMD


class Interface:
    def __init__(self, keep_alive: bool = False):
        self.devices = [
            Device(i, port, keep_alive) for i, port in enumerate(Interface.find_ports())
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

    def __del__(self):
        for dev in self.devices:
            del dev

    def __repr__(self):
        r = ""
        for dev in self.devices:
            r += f"{dev}\n"
        return r

    def remap(self) -> None:
        """
        Reverses the order of devices, essentially swapping their ID-s.
        """
        self.devices = self.devices[::-1]

    def animate(
        self,
        id: int,
        method: str,
        frames: Callable,
        fps: int = 30,
        ntimes: int = 100,
        brightness: int = 255,
    ) -> None:
        """
        Runs an animation on the device with the specified device method and routine for generating the arguments.

        Args:
            `id` (`int`): ID of the device.
            `method` (`str`): Name of the device method to render the pixels (e.g., 'paint', 'display').
            `frames` (`Callable`): Routine which takes a single variable as an argument (frame number) and returns all the keyword arguments passed to the device method.
            `fps` (`int`): Number of frames per second.
            `ntimes` (`int`): Total number of frames to run.
            `brightness` (`int`): Master brightness value (0 to 255).
        """
        self.devices[id].animate(method, frames, fps, ntimes, brightness)

    def paint(self, id: int, array: list[list[float]], brightness: int = 255) -> None:
        """
        Paints a greyscale image on the device.

        Args:
            `array` (`list[list[float]]`): A 2D array of greyscale values representing the image 0 <= value < 1.
            `brightness` (`int`): The brightness value to set.

        Raises:
            `ValueError`: If the dimensions of the input array do not match the device's screen size.
        """
        self.devices[id].paint(array, brightness)

    def display(self, id: int, array: list[list[bool]], brightness: int = 255) -> None:
        """
        Displays a binary image on the device.

        Args:
            `array` (`list[list[bool]]`): A 2D array of boolean values representing the image.
            brightness (`int`): The brightness value to set.

        Raises:
            `ValueError`: If the dimensions of the input array do not match the device's screen size or if the brightness value is out of range.
        """
        self.devices[id].display(array, brightness)

    def brightness(self, id: int, value: int) -> None:
        """
        Sets the brightness of the device.

        Args:
            `id` (`int`): ID of the device.
            `value` (`int`): The brightness value to set.

        Raises:
            `ValueError`: If the brightness value is out of range.
        """
        self.devices[id].brightness(value)

    def sleep(self, id: int) -> None:
        """
        Puts the device to sleep.

        Args:
            `id` (`int`): ID of the device.
        """
        self.devices[id].sleep()

    def wake(self, id: int) -> None:
        """
        Wakes the device from sleep.

        Args:
            `id` (`int`): ID of the device.
        """
        self.devices[id].wake()

    def command(
        self, id: int, command: CMD, params=[], expect_response=False
    ) -> None | bytes:
        """
        Sends a command to the device.

        Args:
            `id` (`int`): ID of the device.
            `command` (`CMD`): The command to send to the device.
            `params` (`list`): The list of parameters to send with the command.
            `expect_response` (`bool`): A flag to indicate whether to expect a response from the device.

        Returns:
            `bytes` | `None`: The response from the device if `expect_response` is set to `True`.
        """
        return self.devices[id].command(command, params, expect_response)
