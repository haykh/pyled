# %%
from pyled.interface import Interface
from pyled.device import Device
from pyled.commands import CMD
import time
import math

# %%
control = Interface()
print(control)
control.sleep(0)
# %%

arr = [[(i * j % 3) % 2 for i in range(Device.HEIGHT)] for j in range(Device.WIDTH)]
# %%
control.display(0, arr)

# %%
control.brightness(0, 2)
# %%
