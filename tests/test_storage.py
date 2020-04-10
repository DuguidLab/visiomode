#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import pytest
import visiomode.storage as storage


class TestRedisClient:
    rds = storage.RedisClient()

    def test_status_updating(self):
        """Test getting and setting status"""
        status = "active"
        self.rds.set_status(status)
        assert self.rds.get_status() == status

    def test_subscribe_status_nocallback(self):
        """Test status subscription without a callback"""
        # subscribe
        status_sub = self.rds.subscribe_status(threaded=False)
        # change the status
        self.rds.set_status("active")
        # see if the change was picked up, if not get_message will return None
        assert status_sub.get_message()

    def test_subscribe_status_callback(self):
        """Test a threaded status subscription with a callback"""

        def callback(_):
            """Dummy callback, if this is called the test passes"""
            assert True

        # subscribe
        status_sub = self.rds.subscribe_status(callback=callback, threaded=True)
        # change the status - if update is picked up the callback should pop up
        self.rds.set_status("stopped")

    def test_invalid_status(self):
        """Test whether setting an invalid key will raise the appropriate error."""
        with pytest.raises(storage.InvalidStatusCodeError):
            self.rds.set_status("noddy_key")
