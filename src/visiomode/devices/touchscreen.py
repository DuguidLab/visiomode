#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import datetime
import logging

import pygame as pg

import visiomode.config as conf
from visiomode import devices, models


class Touchscreen(devices.InputDevice):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.config = conf.Config()

    def get_response(self):
        touch_event = pg.event.get(eventtype=pg.FINGERDOWN)
        if touch_event:
            logging.debug(f"Touch event registered - {touch_event}")
            # Flatten list. This essentially throws out all touch events that happen at an epoch shorter than the FPS.
            touch_event = touch_event[0]
            pos_x = touch_event.x * self.config.width
            pos_y = touch_event.y * self.config.height
            dist_x = touch_event.dx * self.config.width
            dist_y = touch_event.dy * self.config.height
            name = "left" if pos_x >= (self.config.width / 2) else "right"
            return models.Response(
                timestamp=datetime.datetime.now().isoformat(),
                name=name,
                pos_x=pos_x,
                pos_y=pos_y,
                dist_x=dist_x,
                dist_y=dist_y,
            )
        return None
