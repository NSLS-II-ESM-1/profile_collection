from ophyd.utils.errors import ReadOnlyError
print("This should raise an error because EPU is not writeable during shutdown.")
try:
    RE(Eph.move_to(90, grating='600', EPU='105', shutter='open'))
except ReadOnlyError:
    print("The test raised the expected error.")