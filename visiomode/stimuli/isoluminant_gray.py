#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import visiomode.stimuli as stimuli


class IsoluminantGray(stimuli.SolidColour):
    """Based gratings pixel value mean"""

    form_path = None

    def __init__(self, background, **kwargs):
        super().__init__(background, colour=(127, 127, 127))
