import pyvisa
from pyvisa import ResourceManager, VisaIOError
from pyvisa.resources import USBInstrument
from pyvisa.resources.usb import USBInstrument
from pyvisa.constants import AccessModes, EventType, ResourceAttribute, StatusCode

from time import sleep, time
import logging
import time

status_delay = 0.1
def get_status(inst: USBInstrument, wait=0.1) -> str:
    rc = inst.write(f'SYST:STAT?')
    sleep(wait)
    stat = inst.read()
    stat = bin(int(stat, 16)).lstrip("0b").rjust(8, '0')
    return stat


resource_manager: ResourceManager = pyvisa.highlevel.ResourceManager()
instrument: USBInstrument = resource_manager.open_resource(resource_name ='USB0::0x0483::0x7540::SPD3ECAX1L1560::INSTR',
                                                           access_mode = AccessModes.exclusive_lock)

with instrument:
    delay_step_size = 0.1
    min_delay = 0
    max_delay = 4
    delay_steps = int((max_delay - min_delay)/delay_step_size) + 1
    delays = [round(min_delay + delay_step*delay_step_size,2) for delay_step in range(delay_steps)]
    is_timeout = False
    delay_index = 0
    delay_spectrum = {}
    iteration = 0
    while delay_index <= delay_steps:
        stat='00000000'
        is_timeout = False
        try:
            if 0 <= delay_index <= delay_steps:
                delay = delays[delay_index]
            else:
                break

            # rc = instrument.write(f'SYST:STAT?')
            # rc = instrument.write(f'SYST:STAT?')
            # sleep(delay)
            # stat = instrument.read()
            # stat = bin(int(stat, 16)).lstrip("0b").rjust(8, '0')
            stat = get_status(instrument)

            if delay_index in delay_spectrum:
                delay_spectrum[delay_index] += 1
            else:
                delay_spectrum[delay_index] = 1

            # if delay_index > 0:
            #     delay_index -= 1
        except VisaIOError as e:
            is_timeout = True
            delay_index += 1
        print(f'delay={delay}, stat={stat}, iteration = {iteration}, index = {delay_index}, error={is_timeout}')
        iteration += 1


