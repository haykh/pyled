from typing import Callable
from .commands import CMD


class Device:
    import serial

    WIDTH = 9
    HEIGHT = 34
    RESPONSE_SIZE = 32

    FWK_MAGIC = [0x32, 0xAC]
    FWK_VID = 0x32AC
    LED_MATRIX_PID = 0x20
    QTPY_PID = 0x001F
    INPUTMODULE_PIDS = [LED_MATRIX_PID, QTPY_PID]

    @staticmethod
    def send_col(sconn: serial.Serial, colid: int, values: list[int]) -> None:
        """
        Stages greyscale values for a single column.

        Args:
            `sconn` (`serial.Serial`): The serial connection object to the device.
            `colid` (`int`): The ID of the column to stage the greyscale values for.
            `values` (`list[int]`): The list of greyscale values to stage.

        """
        sconn.write(Device.FWK_MAGIC + [CMD.StageGreyCol, colid] + values)

    @staticmethod
    def commit_cols(sconn: serial.Serial):
        """
        Commits the changes from sending individual columns with `send_col()` function, displaying the matrix.

        Args:
            `sconn` (`serial.Serial`): The serial connection object to the device.

        """
        sconn.write(Device.FWK_MAGIC + [CMD.DrawGreyColBuffer, 0x00])

    def __init__(self, id: int, port) -> None:
        self.id = id
        self.port = port
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def execute(
        self, command: Callable[[serial.Serial], None], expect_response=False
    ) -> None | bytes:
        """
        Executes a command on the device.

        Args:
            `command` (`Callable`): The command to execute on the device (a callable with the serial connection as an argument).
            `expect_response` (`bool`): A flag to indicate whether to expect a response from the device.

        Returns:
            `None` | `bytes`: The response from the device if `expect_response` is set to `True`.

        Raises:
            `RuntimeError`: If the device is not connected.
            `IOError`: If an I/O error occurs during the execution of the command.
            `Exception`: If an unexpected error occurs during the execution of the command.
        """
        if not self.connected:
            raise RuntimeError("Device is not connected")
        import serial

        try:
            with serial.Serial(self.port.device, 115200) as sconn:
                command(sconn)
                if expect_response:
                    return sconn.read(Device.RESPONSE_SIZE)

        except (IOError, OSError) as ex:
            self.disconnect()
            raise IOError(f"Error: {ex}")
        except Exception as ex:
            raise RuntimeError(f"Error: {ex}")

    def paint(self, array: list[list[float]], brightness: int = 255) -> None:
        """
        Paints a greyscale image on the device.

        Args:
            `array` (`list[list[float]]`): A 2D array of greyscale values representing the image 0 <= value < 1.
            `brightness` (`int`): The brightness value to set.

        Raises:
            `ValueError`: If the dimensions of the input array do not match the device's screen size.
        """
        if len(array) != Device.WIDTH or any(
            len(row) != Device.HEIGHT for row in array
        ):
            raise ValueError("Invalid dimensions for the input array")
        assert 0 <= brightness <= 255
        import serial

        def paint_image(sconn: serial.Serial, arr: list[list[float]]) -> None:
            for colid in range(Device.WIDTH):
                Device.send_col(
                    sconn,
                    colid,
                    [
                        (
                            (int(val * (brightness + 1)) if val >= 0 else 0)
                            if val < 1
                            else brightness
                        )
                        for val in arr[colid]
                    ],
                )
            Device.commit_cols(sconn)

        self.execute(lambda sconn: paint_image(sconn, array))

    def display(self, array: list[list[bool]], brightness: int = 255) -> None:
        """
        Displays a binary image on the device.

        Args:
            `array` (`list[list[bool]]`): A 2D array of boolean values representing the image.
            brightness (`int`): The brightness value to set.

        Raises:
            `ValueError`: If the dimensions of the input array do not match the device's screen size or if the brightness value is out of range.
        """
        if len(array) != Device.WIDTH or any(
            len(row) != Device.HEIGHT for row in array
        ):
            raise ValueError("Invalid dimensions for the input array")

        vals = [0 for _ in range(39)]
        for i, v in enumerate([a for ar in array for a in ar]):
            if v:
                vals[int(i / 8)] |= 1 << i % 8

        self.command(CMD.Draw, vals)
        self.brightness(brightness)

    def brightness(self, value: int) -> None:
        """
        Sets the brightness of the device.

        Args:
            `value` (`int`): The brightness value to set.

        Raises:
            `ValueError`: If the brightness value is out of range.
        """
        assert 0 <= value <= 255
        self.command(CMD.Brightness, [value])

    def sleep(self) -> None:
        """
        Puts the device to sleep.
        """
        self.command(CMD.Sleep, [True])

    def wake(self) -> None:
        """
        Wakes the device from sleep.
        """
        self.command(CMD.Sleep, [False])

    def command(self, command: CMD, params=[], expect_response=False) -> None | bytes:
        """
        Sends a command to the device.

        Args:
            `command` (`CMD`): The command to send to the device.
            `params` (`list`): The list of parameters to send with the command.
            `expect_response` (`bool`): A flag to indicate whether to expect a response from the device.

        Returns:
            `bytes` | `None`: The response from the device if `expect_response` is set to `True`.
        """
        return self.execute(
            lambda sconn: sconn.write(Device.FWK_MAGIC + [command] + params),
            expect_response,
        )

    @property
    def version(self) -> str:
        """
        Gets the firmware version of the device.
        """
        res = self.command(CMD.Version, expect_response=True)
        if not res:
            return "Unknown"
        major = res[0]
        minor = (res[1] & 0xF0) >> 4
        patch = res[1] & 0xF
        pre_release = res[2]
        version = f"{major}.{minor}.{patch}"
        if pre_release:
            version += " (Pre-release)"
        return version

    def __repr__(self) -> str:
        r = f"Device {self.id}\n"
        r += f"  Status:   [{'connected' if self.connected else 'disconnected'}]\n"
        r += f"  Port:     {self.port.device}\n"
        r += f"  VID:      0x{self.port.vid:04X}\n"
        r += f"  PID:      0x{self.port.pid:04X}\n"
        r += f"  SN:       {self.port.serial_number}\n"
        r += f"  Product:  {self.port.product}\n"
        r += f"  Firmware: {self.version}\n"
        return r
