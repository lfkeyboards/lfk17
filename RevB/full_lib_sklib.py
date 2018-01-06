# from skidl import Pin, Part, SchLib, SKIDL, TEMPLATE

# SKIDL_lib_version = '0.0.1'

# full_lib = SchLib(tool=SKIDL).add_parts(*[
#         Part(name='MX_LED',dest=TEMPLATE,tool=SKIDL,ref_prefix='M',num_units=2,fplist=['cherry'],do_erc=True,footprint='Keyboard:mxalps',pins=[
#             Pin(num='SW1',name='~',func=Pin.PASSIVE,do_erc=True),
#             Pin(num='SW2',name='~',func=Pin.PASSIVE,do_erc=True),
#             Pin(num='A',name='~',func=Pin.PASSIVE,do_erc=True),
#             Pin(num='K',name='~',func=Pin.PASSIVE,do_erc=True)]),
#         Part(name='1SS309',dest=TEMPLATE,tool=SKIDL,keywords='diode',description='1SS309 Quad Switching Diode Common Cathode',ref_prefix='D',num_units=4,fplist=['Housings_SOT-25-5', 'SC-74A'],do_erc=True,footprint='Keyboard:SC-74A',pins=[
#             Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
#             Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
#             Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
#             Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True),
#             Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
#             Pin(num='4',name='A',func=Pin.PASSIVE,do_erc=True),
#             Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
#             Pin(num='5',name='A',func=Pin.PASSIVE,do_erc=True)])])