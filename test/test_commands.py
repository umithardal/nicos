from nicos import session
from nicos.commands import scan, count, move, maw, read
from test.utils import raises
from nicos.errors import UsageError, LimitError

motor = None

def setup_module():
    global motor
    session.loadSetup('axis')
    session.setMode('master')
    motor = session.getDevice('motor')

def teardown_module():
    session.unloadSetup()



def test_commands():
    session.setMode('slave')
    assert raises(UsageError, scan, motor, [0, 1, 2, 10])

    session.setMode('master')
    scan(motor, [0, 1, 2, 10])



    assert raises(UsageError, count, motor)
    count()



    assert raises(LimitError, move, motor, max(motor.abslimits)+1)

    positions = (min(motor.abslimits), 0, max(motor.abslimits))
    for pos in positions:
        move(motor, pos)
        motor.wait()
        assert motor.curvalue == pos

    for pos in positions:
        maw(motor, pos)
        assert motor.curvalue == pos

