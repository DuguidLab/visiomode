#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import flask_socketio as sock


class SessionNamespace(sock.Namespace):
    def on_connect(self, data):
        print('connected')
        print(data)

    def on_disconnect(self):
        pass

    def on_event(self):
        pass
