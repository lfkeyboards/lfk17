#!/usr/bin/env python3
import os
from collections import defaultdict
from pprint import pprint
from skidl import (
    Net,
    Part,
    Pin,
    generate_netlist,
    TEMPLATE,
    SchLib,
    SKIDL,
    lib_search_paths
)

matrix_to_mcu = {
    "Row1": "PB7",
    "Row2": "PD3",
    "Row3": "PD4",
    "Row4": "PD5",
    "Row5": "PD6",

    "Col1": "PA7",
    "Col2": "PD7",
    "Col3": "PE0",
    "Col4": "PE1",
}

skidl_lib = SchLib('lfk17_lib_sklib.py', tool=SKIDL)  # Create a SKiDL library object from the new file.

switch = Part(skidl_lib, 'MX_LED', TEMPLATE, footprint="Keyboard:MXALPS", tool=SKIDL)
diode = Part(skidl_lib, '1SS309', TEMPLATE, footprint="Keyboard:SC-74A", tool=SKIDL)
diode = Part(skidl_lib, '1SS309', TEMPLATE, footprint="Keyboard:SC-74A", tool=SKIDL)

nets = defaultdict(Net)
row_nets = []
col_nets = []
diode_nets = []


parts = {
    'SW_1': switch(ref='SW_1', d_ref='D1', d_pin=4, row=1, col=1, rgb=1),
    'SW_2': switch(ref='SW_2', d_ref='D1', d_pin=3, row=1, col=2, rgb=17),
    'SW_3': switch(ref='SW_3', d_ref='D1', d_pin=1, row=1, col=3, rgb=18),
    'SW_4': switch(ref='SW_4', d_ref='D1', d_pin=5, row=1, col=4, rgb=23),

    'SW_5': switch(ref='SW_5', d_ref='D2', d_pin=4, row=2, col=1, rgb=2),
    'SW_6': switch(ref='SW_6', d_ref='D2', d_pin=3, row=2, col=2, rgb=19),
    'SW_7': switch(ref='SW_7', d_ref='D2', d_pin=1, row=2, col=3, rgb=22),
    'SW_8': switch(ref='SW_8', d_ref='D3', d_pin=5, row=3, col=4, rgb=24),

    'SW_9': switch(ref='SW_9', d_ref='D3', d_pin=4, row=3, col=1, rgb=3),
    'SW_10': switch(ref='SW_10', d_ref='D3', d_pin=3, row=3, col=2, rgb=6),
    'SW_11': switch(ref='SW_11', d_ref='D3', d_pin=1, row=3, col=3, rgb=9),

    'SW_12': switch(ref='SW_12', d_ref='D4', d_pin=4, row=4, col=1, rgb=4),
    'SW_13': switch(ref='SW_13', d_ref='D4', d_pin=3, row=4, col=2, rgb=7),
    'SW_14': switch(ref='SW_14', d_ref='D4', d_pin=1, row=4, col=3, rgb=10),
    'SW_15': switch(ref='SW_15', d_ref='D5', d_pin=5, row=5, col=4, rgb=11),

    'SW_16': switch(ref='SW_16', d_ref='D5', d_pin=4, row=5, col=1, rgb=5),
    'SW_17': switch(ref='SW_17', d_ref='D5', d_pin=1, row=5, col=3, rgb=8),

    'D1': diode(ref='D1', row=1, x=1.0, y=1.0),
    'D2': diode(ref='D2', row=2, x=1.0, y=2.0),
    'D3': diode(ref='D3', row=3, x=1.0, y=3.0),
    'D4': diode(ref='D4', row=4, x=1.0, y=4.0),
    'D5': diode(ref='D5', row=5, x=1.5, y=5.0),
}
led_matrix_a = [
    ['SW_1', 'SW_2', 'SW_3', 'SW_4', None, None, None, None, None],
    ['SW_5', 'SW_6', 'SW_7', 'SW_8', None, None, None, None, None],
    ['SW_9', 'SW_10', 'SW_11', None, None, None, None, None, None],
    ['SW_12', 'SW_13', 'SW_14', 'SW_15', None, None, None, None, None],
    ['SW_16', 'SW_17', None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
]
led_matrix_b = [
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
]


def row_from_diode_net(net):
    diodes = [pin.part for pin in net.pins if pin.part.ref.startswith("D")]
    if len(diodes) != 1:
        print("WTF {} is connected to multiple diodes")
        return
    cathode_pins = diodes[0]["K"]
    cathode_row = cathode_pins[0].nets[0]  # At least one cathode is a member of this net
    if cathode_row not in row_nets:
        print("Diode {} is not connected to any row")
    # List of all nets connected to cathodes on this diode
    for pin in cathode_pins:
        for net in pin.nets:
            if net != cathode_row:
                print("More than one net attached to diode's cathode")
    return cathode_row


def validate_switches():
    matrix_check = defaultdict(list)
    for ref, switch in ((ref, switch) for (ref, switch) in parts.items() if ref.startswith("S")):
        pins = {
            "MX1": {
                "column": None,
                "diode": None,
                "row": None
            },
            "MX2": {
                "column": None,
                "diode": None,
                "row": None
            }
        }
        switch_valid = True
        for pin in pins:
            valid_row = False
            valid_col = False
            # find the pins connected to columns
            pin_nets = [net for net in switch[pin].nets if net in col_nets]
            if len(pin_nets) > 1:
                print("WTF {} is connected to multiple columns")
            elif len(pin_nets) == 1:
                pins[pin]["column"] = pin_nets[0].name
                if switch.col != int(pins[pin]["column"][3:]):
                    print("ERR: {ref} nets do not match definition:".format(ref=ref))
                    print("     Expected C{}, found {}".format(switch.col, pins[pin]["column"]))
                    break
                else:
                    valid_col = True

            pin_nets = [net for net in switch[pin].nets if net in diode_nets]
            if len(pin_nets) > 1:
                print("WTF {} is connected to multiple columns")
            elif len(pin_nets) == 1:
                if len(pin_nets[0].pins) > 2:
                    print('more than one pin net')
                pins[pin]["diode"] = pin_nets[0].name
                if len(pin_nets[0]) > 2:
                    print("Warn: multiple switches connected to {diode_net}:".format(diode_net=pin_nets[0].name))
                    print("      {}".format(pin_nets))
                pins[pin]["row"] = row_from_diode_net(pin_nets[0]).name
                if switch.row != int(pins[pin]["row"][3:]):
                    print("ERR: {ref} nets do not match definition:".format(ref=ref))
                    print("     Expected R{}, found {}".format(switch.row, pins[pin]["row"]))
                    break
                else:
                    valid_col = True
            if valid_row == valid_col:  # aka XNOR, pin must be connected to a row or column, but not both
                switch_valid = False
        if not switch_valid:
            print("ERR: {ref} did not pass validation:".format(ref=ref))
            # print(pins)
            # print(switch)
        matrix_check[(switch.col, switch.row)].append(switch)
    # pprint(matrix_check)
    for location, switch_list in matrix_check.items():
        if len(switch_list) > 1:
            print("Warn: multiple switches found on C{col} R{row}:".format(col=location[0], row=location[1]))
            print("      {}".format(", ".join((sw.ref for sw in switch_list))))


def connect_switch_matrix():
    # Connect the diodes to their row
    for d in (v for (k, v) in parts.items() if k.startswith("D")):
        row = "Row{}".format(d.row)
        for pin in d["k"]:
            nets[row] += pin

    # Connect switches
    for sw in (v for (k, v) in parts.items() if k.startswith("S")):
        # Switch to column
        pins = ("MX1", "MX2")
        if getattr(sw, "reversed", False):
            pins = ("MX2", "MX1")
        if(hasattr(sw, "clone")):
            parent = parts[sw.clone]
            col = "Col{}".format(parent.col)
            d_ref = parent.d_ref
            d_pin = parent.d_pin
            parent["K"] += sw["K"]
            parent["A"] += sw["A"]
            setattr(sw, "row", parent.row)
            setattr(sw, "col", parent.col)
        else:
            col = "Col{}".format(sw.col)
            d_ref = sw.d_ref
            d_pin = sw.d_pin
        nets[col] += sw[pins[0]]
        # Switch to diode
        net_name = "Matrix-{switch_ref}-{diode_ref}-{diode_pin}".format(
            switch_ref=sw.ref, diode_ref=d_ref, diode_pin=d_pin)
        nets[net_name] += sw[pins[1]]
        nets[net_name] += parts[d_ref][d_pin]


def set_net_names():
    # Name all of the nets by their dict key, and create sublists as needed
    for (key, net) in nets.items():
        net.name = key
        if key.startswith("Col"):
            col_nets.append(net)
        if key.startswith("Row"):
            row_nets.append(net)
        if key.startswith("Matrix"):
            diode_nets.append(net)


def netnames_for_rgb(ref):
    rgb_matrix = [  # A, R, G, B
        (2, 1, 3, 4),
        (3, 1, 2, 4),
        (4, 1, 2, 3),
        (5, 1, 2, 3),
        (6, 1, 2, 3),
        (7, 1, 2, 3),
        (8, 1, 2, 3),
        (9, 1, 2, 3),
        (1, 9, 8, 7),
        (2, 9, 8, 7),
        (3, 9, 8, 7),
        (4, 9, 8, 7),
        (5, 9, 8, 7),
        (6, 9, 8, 7),
        (7, 9, 8, 6),
        (8, 9, 7, 6),
    ]
    matrix, i = divmod(ref - 1, 16)
    return (
        "L%d_%d" % (matrix, rgb_matrix[i][0]),
        "L%d_%d" % (matrix, rgb_matrix[i][1]),
        "L%d_%d" % (matrix, rgb_matrix[i][2]),
        "L%d_%d" % (matrix, rgb_matrix[i][3])
    )


def connect_switch_leds():
    for ref, sw in ((ref, switch) for (ref, switch) in parts.items() if ref.startswith("S")):
        if getattr(sw, "rgb") is not None:
            a, r, g, b = netnames_for_rgb(getattr(sw, "rgb"))
            nets[a] += sw["A"]
            nets[r] += sw["R"]
            nets[g] += sw["G"]
            nets[b] += sw["B"]


def label_controller(mcu):
    for pin in mcu.pins:
        port_name = pin.name[-3:].upper()
        if len(port_name) >= 3 and \
                port_name[0] == "P" and \
                port_name[1] in ("A", "B", "C", "D", "E", "F") and \
                port_name[2].isdigit() and \
                port_name not in matrix_to_mcu.values():
            nets[port_name] += pin


def label_unused_pins(mcu):
    for pin in mcu.pins:
        if not pin.nets:
            port_name = pin.name[-3:].upper()
            if len(port_name) >= 3 and \
                    port_name[0] == "P" and \
                    port_name[1] in ("A", "B", "C", "D", "E", "F") and \
                    port_name[2].isdigit() and \
                    port_name not in matrix_to_mcu.values():
                nets[port_name] += pin


def add_controller():
    nets["+5v"] = Net("+5v")
    nets["GND"] = Net("GND")
    parts["U1"] = Part(skidl_lib, 'AT90USB1286-AU', ref="U1", footprint='Keyboard:QFN_64')
    # label_controller(parts["U1"])
    parts["U2"] = Part(skidl_lib, 'IS31FL3731', ref="U2", footprint='Keyboard:QFN_28')
    for c in ("C4", "C10"):
        parts[c] = Part(skidl_lib, 'C', ref=c, value="1µF", footprint='Capacitors_SMD:C_0603')
    for c in ("C3", "C7", "C6", "C8", "C9", "C11", "C12"):
        parts[c] = Part(skidl_lib, 'C', ref=c, value="0.1µF", footprint='Capacitors_SMD:C_0603')
    for c in ("C1", "C2"):
        parts[c] = Part(skidl_lib, 'C', ref=c, value="18pF", footprint='Capacitors_SMD:C_0603')
    parts["C5"] = Part(skidl_lib, 'C', ref="C5", value="4.7µF", footprint='Capacitors_SMD:C_1206')
    for r in ("R1", "R6"):
        parts[r] = Part(skidl_lib, 'R', ref=r, value="10k", footprint='Resistors_SMD:R_0603')
    for r in ("R4", "R5"):
        parts[r] = Part(skidl_lib, 'R', ref=r, value="22", footprint='Resistors_SMD:R_0603')
    for r in ("R2", "R3"):
        parts[r] = Part(skidl_lib, 'R', ref=r, value="4.7k", footprint='Resistors_SMD:R_0603')
    for r in ("R7",):
        parts[r] = Part(skidl_lib, 'R', ref=r, value="30k", footprint='Resistors_SMD:R_0603')
    parts["F1"] = Part(skidl_lib, 'FP_Small', ref="F1", footprint='Capacitors_SMD:C_1206')
    parts["P1"] = Part(skidl_lib, 'USB_OTG', ref="P1", footprint='Capacitors_SMD:C_1206')
    parts["Y1"] = Part(skidl_lib, 'CRYSTAL_32x25', ref="Y1", footprint='Crystals:Crystal_SMD_3225-4pin_3.2x2.5mm')
    parts["RESET"] = Part(skidl_lib, 'SW_PUSH', ref="S1", footprint='Keyboard:PTS-820_SPST')
    parts["X1"] = Part(skidl_lib, 'Piezo', ref="X1", footprint='Keyboard:piezo-9x9')

    # Power
    nets["+5v"] += parts["U1"]["VCC,VBUS"]
    nets["+5v"] += parts["F1"][2]
    # nets["+5v"] += parts["RGB33"][1]
    nets["+5v"] += parts["R1"][1]
    nets["+5v"] += parts["U2"]["VCC"]
    nets["GND"] += parts["U1"]["GND"]
    nets["GND"] += parts["U1"]["PE2"]
    nets["GND"] += parts["U2"]["GND"]
    for ref in ("C5", "C6", "C7", "C8", "C9", "C10", "C11"):
        nets["+5v"] += parts[ref][1]
        nets["GND"] += parts[ref][2]
    nets["+5v"] += parts["R6"][1]

    # XTAL
    parts["U1"]["XTAL1"] += parts["Y1"][1]
    parts["U1"]["XTAL1"] += parts["C1"][2]
    parts["U1"]["XTAL2"] += parts["Y1"][3]
    parts["U1"]["XTAL2"] += parts["C2"][2]
    nets["GND"] += parts["Y1"][2]
    nets["GND"] += parts["Y1"][4]
    nets["GND"] += parts["C1"][1]
    nets["GND"] += parts["C2"][1]

    # USB
    nets["VBUS"] += parts["P1"]["VBUS"]
    nets["VBUS"] += parts["F1"][1]
    nets["USB-"] += parts["P1"]["D-"]
    nets["USB-"] += parts["R4"][2]
    nets["USB+"] += parts["P1"]["D\+"]
    nets["USB+"] += parts["R5"][2]
    nets["D-"] += parts["R4"][1]
    nets["D-"] += parts["U1"]["D-"]
    nets["D+"] += parts["R5"][1]
    nets["D+"] += parts["U1"]["D\+"]
    nets["GND"] += parts["P1"]["GND"]
    nets["GND"] += parts["P1"]["shield"]

    # MCU
    parts["U1"]["UCAP"] += parts["C3"][1]
    nets["GND"] += parts["C3"][2]
    parts["U1"]["AREF"] += parts["C4"][1]
    nets["GND"] += parts["C4"][2]
    nets["RESET"] += parts["U1"]["RESET"]
    nets["RESET"] += parts["RESET"][1]
    nets["RESET"] += parts["R1"][2]
    nets["GND"] += parts["RESET"][2]
    nets["GND"] += parts["RESET"]["case"]

    # Audio
    nets["AUDIO"] += parts["U1"]["B5"]
    nets["AUDIO"] += parts["X1"][1]
    nets["GND"] += parts["X1"][2]
    # nets["QMK_RGB"] += parts["U1"]["PF4"]

    # Connect Matrix to MCU
    for k, v in matrix_to_mcu.items():
        print(k, v)
        nets[k] += parts["U1"][v]

    # I2C
    nets["+5v"] += parts["R2"][1]
    nets["LED_SCL"] += parts["R2"][2]
    nets["LED_SCL"] += parts["U1"]["SCL/"]
    nets["LED_SCL"] += parts["U2"]["SCL"]
    nets["+5v"] += parts["R3"][1]
    nets["LED_SDA"] += parts["R3"][2]
    nets["LED_SDA"] += parts["U1"]["SDA/"]
    nets["LED_SDA"] += parts["U2"]["SDA"]

    # # USB Connector
    # parts["P2"] = Part('/Users/swilson/dev/kicad-library/library/conn.lib', 'CONN_01X05', ref="P2", footprint='Connectors_JST:JST_SH_SM05B-SRSS-TB_05x1.00mm_Angled')
    # nets["VBUS"] += parts["P2"][5]
    # nets["USB-"] += parts["P2"][4]
    # nets["USB+"] += parts["P2"][3]
    # nets["GND"] += parts["P2"][1]

    # ISP Connector
    parts["P3"] = Part('/Users/swilson/dev/kicad-library/library/conn.lib', 'CONN_02X03', ref="P3", footprint='Connectors_JST:JST_SH_SM06B-SRSS-TB_06x1.00mm_Angled')
    nets["+5v"] += parts["P3"][2]
    nets["GND"] += parts["P3"][6]
    nets["RESET"] += parts["P3"][5]
    parts["P3"][1] += parts["U1"]["MISO"]
    parts["P3"][3] += parts["U1"]["SCLK"]
    parts["P3"][4] += parts["U1"]["MOSI"]

    # # USB Connector
    # parts["P4"] = Part('/Users/swilson/dev/kicad-library/library/conn.lib', 'CONN_01X03', ref="P4", footprint='Connectors_JST:JST_SH_SM03B-SRSS-TB_03x1.00mm_Angled')
    # nets["+5v"] += parts["P4"][2]
    # nets["GND"] += parts["P4"][1]
    # parts["P4"][3] += parts["U1"]["PC6"]

    # ISSI
    parts["U2"]["SDB"] += parts["R6"][2]
    parts["U2"]["R_EXT"] += parts["R7"][2]
    nets["GND"] += parts["R7"][1]
    parts["U2"]["C_FILT"] += parts["C12"][2]
    nets["GND"] += parts["C12"][1]
    nets["GND"] += parts["U2"]["AD"]  # Sets I2C address to 0xEE (1110 111X)
    for i in range(1, 10):
        nets["L0_{}".format(i)] += parts["U2"]["CA{}".format(i)]
        nets["L1_{}".format(i)] += parts["U2"]["CB{}".format(i)]


add_controller()
connect_switch_leds()
connect_switch_matrix()
label_unused_pins(parts["U1"])
set_net_names()
validate_switches()
generate_netlist()
