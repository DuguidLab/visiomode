#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import visiomode.storage as storage


class TestRedisClient:
    rds = storage.RedisClient()

    def test_status_updating(self):
        status = "test"
        self.rds.set_status(status)
        assert self.rds.get_status() == status

    def test_subscribe_status(self):
        assert True
