#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import datetime
import pygame as pg
import visiomode.devices as devices
import visiomode.models as models
import visiomode.config as conf


class Touchscreen(devices.InputDevice):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.config = conf.Config()

    def get_response(self):
        touch_event = pg.event.get(eventtype=pg.FINGERDOWN)
        if touch_event:
            print(touch_event)
            # Flatten list. This essentially throws out all touch events that happen at an epoch shorter than the FPS.
            touch_event = touch_event[0]
            return models.Response(
                timestamp=datetime.datetime.now().isoformat(),
                pos_x=touch_event.x * self.config.width,
                pos_y=touch_event.y * self.config.height,
                dist_x=touch_event.dx * self.config.width,
                dist_y=touch_event.dy * self.config.height,
            )
        return None
