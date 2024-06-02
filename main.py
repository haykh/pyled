# %%
from pyled.interface import Interface
from pyled.device import Device
from pyled.commands import CMD
import time
import math

if __name__ == "__main__":
    control = Interface(keep_alive=True)
    # control.remap()
    # print(control)
    #
    # # arr = [[(i * j % 3) % 2 for i in range(Device.HEIGHT)] for j in range(Device.WIDTH)]
    # # control.display(0, arr)
    #
    # control.paint(0, arr)
    #
    # control.brightness(0, 255)

    def func(n):
        arr = [
            [((i + n) * j % 3) % 2 for i in range(Device.HEIGHT)]
            for j in range(Device.WIDTH)
        ]
        # arr = [
        #     [
        #         (1 + math.cos(2 * math.pi * (i + n / 10) / Device.HEIGHT)) / 2
        #         for i in range(Device.HEIGHT)
        #     ]
        #     for j in range(Device.WIDTH)
        # ]
        return {"array": arr}

    # control.animate(0, "paint", func, fps=30)
    control.animate(0, "display", func, fps=60)

    control.sleep(0)
    control.sleep(1)
    try:
        del control
    except Exception as e:
        print(e)
