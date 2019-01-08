"""Test hardware components of controller"""
import carie_controller.core as rc


def test_stepper_motor():
    """Test for stepper motor"""
    rc.water_reward(delay=1000)
