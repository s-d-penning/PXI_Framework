from time import sleep

import pyvisa
from pyvisa import ResourceManager, VisaIOError
from pyvisa.resources.usb import USBInstrument
from pyvisa.constants import AccessModes


class PowerSupply:
    def __init__(self, usb: int = 0, manufacturer_id: str = '0x0483', model_code: str = '0x7540',
                 serial_number: str = 'SPD3ECAX1L1560', output_mode: int = 0):

        self.resource_name = f'USB{usb}::{manufacturer_id}::{model_code}::{serial_number}::INSTR'
        self.resource_manager: ResourceManager = pyvisa.highlevel.ResourceManager()
        self.access_mode = AccessModes.exclusive_lock
        self.delay = 0.025
        self.output_mode = '-1'
        self.voltage_multiplier = 1
        self.current_multiplier = 1
        self.status = bin(0x00)

        self.channel_1 = "CH1"
        self.channel_2 = "CH2"
        self.channel_3 = "CH3"

        self.ch1_mode = 'UNK'
        self.ch2_mode = 'UNK'
        self.ch3_mode = 'CV/CL'

        self.resource: USBInstrument = self.resource_manager.open_resource(resource_name=self.resource_name,
                                                                           access_mode=AccessModes.exclusive_lock)

        self.set_channel_power(self.channel_1, 'OFF')
        self.channel_1_state = 'OFF'
        self.set_channel_power(self.channel_2, 'OFF')
        self.channel_2_state = 'OFF'
        self.set_channel_power(self.channel_3, 'OFF')
        self.channel_3_state = 'OFF'

        if output_mode == 0:
            self.output_mode = 'Independent'
            self.voltage_multiplier = 1
            self.current_multiplier = 1
        elif output_mode == 1:
            self.output_mode = 'Series'
            self.voltage_multiplier = 2
            self.current_multiplier = 1
        elif output_mode == 2:
            self.output_mode = 'Parallel'
            self.voltage_multiplier = 1
            self.current_multiplier = 2
        else:
            raise ValueError("Channel config must be: 0,1 or 2")

        self.channel_config = output_mode
        rc = self.resource.write(f'OUTP:TRACK {self.channel_config}')
        sleep(self.delay)

    def __del__(self):
        self.resource_manager.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.resource.close()

    def refresh_status(self):
        status = None
        while status is None:
            try:
                rc = self.resource.write(f'SYST:STAT?')
                sleep(self.delay)
                # self.delay = self.delay * 0.95
                status = self.resource.read()
            except VisaIOError as e:
                self.delay = self.delay * 1.1
        self.status = bin(int(status, 16)).lstrip("0b").rjust(8, '0')

        if self.status[-1] == '0':
            self.ch1_mode = 'CV'
        elif self.status[-1] == '1':
            self.ch1_mode = 'CC'

        if self.status[-5] == '0':
            self.channel_1_state = 'OFF'
        elif self.status[-5] == '1':
            self.channel_1_state = 'ON'

        if self.status[-2] == '0':
            self.ch2_mode = 'CV'
        elif self.status[-2] == '1':
            self.ch2_mode = 'CC'

        if self.status[-6] == '0':
            self.channel_2_state = 'OFF'
        elif self.status[-6] == '1':
            self.channel_2_state = 'ON'

        if self.status[-4] == '0' and self.status[-3] == '1':
            self.output_mode = 'Independent'
        elif self.status[-4] == '1' and self.status[-3] == '0':
            self.output_mode = 'Parallel'
        elif self.status[-4] == '1' and self.status[-3] == '1':
            self.output_mode = 'Series'

        return self.status

    def set_channel_power(self, channel: str = "CH1", state: str = "OFF"):
        try:
            if channel != 'CH3':
                rc = self.resource.write(f'INST {channel}')
                sleep(self.delay)
            rc = self.resource.write(f'OUTP {channel},{state}')
            sleep(self.delay)
            # self.delay = self.delay * 0.95
        except VisaIOError:
            self.delay = self.delay * 1.1

        self.refresh_status()


class PowerChannel(PowerSupply):
    """
    Knows about channel states without interpreting modes
    """

    def __init__(self, usb: int = 0, manufacturer_id: str = '0x0483', model_code: str = '0x7540',
                 serial_number: str = 'SPD3ECAX1L1560', output_mode: int = 0):
        super().__init__(usb, manufacturer_id, model_code, serial_number, output_mode)

        super().refresh_status()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Put the channels into a safe state
        self.set_channel_power_off(self.channel_1)
        self.set_channel_power_off(self.channel_2)
        self.set_channel_power_off(self.channel_3)

    def set_channel_power_on(self, channel: str = 'CH1') -> str:
        super().set_channel_power(channel, 'ON')

        if channel == 'CH1':
            return self.channel_1_state
        if channel == 'CH2':
            return self.channel_2_state
        else:
            self.channel_3_state = 'ON'
            return self.channel_3_state

    def set_channel_power_off(self, channel: str = 'CH1') -> str:
        super().set_channel_power(channel, 'OFF')

        if channel == 'CH1':
            return self.channel_1_state
        if channel == 'CH2':
            return self.channel_2_state
        else:
            self.channel_3_state = 'OFF'
            return self.channel_3_state

    def set_channel_voltage(self, channel: str = "CH1", value: float = 0.01):
        rc2 = None
        while rc2 is None:
            try:
                rc = self.resource.write(f'INST {channel}')
                sleep(self.delay)
                rc2 = self.resource.write(f'{channel}:VOLT {value}')
                sleep(self.delay)
            except VisaIOError as e:
                self.delay = self.delay * 1.1
        return value

    def get_channel_voltage(self, channel: str = "CH1") -> float:
        result = None
        while result is None:
            try:
                rc = self.resource.write(f'INST {channel}')
                sleep(self.delay)
                rc = self.resource.write(f'MEAS:VOLT? {channel}')
                sleep(self.delay)
                reading = self.resource.read()
                result = float(reading)
                # self.delay = self.delay * 0.95
            except VisaIOError as e:
                self.delay = self.delay * 1.1

        return result

    def set_channel_current(self, channel: str = "CH1", current: float = 3.2) -> float:
        result = None
        while result is None:
            try:
                rc = self.resource.write(f'INST {channel}')
                sleep(self.delay)
                rc = self.resource.write(f'{channel}:CURR {current}')
                sleep(self.delay)
                result = self.get_channel_current()
            except VisaIOError as e:
                self.delay = self.delay * 1.1
        return result

    def get_channel_current(self, channel: str = "CH1") -> float:
        result = None
        while result is None:
            try:
                rc = self.resource.write(f'INST {channel}')
                sleep(self.delay)
                rc = self.resource.write(f'MEAS:CURR? {channel}')
                sleep(self.delay)
                result = self.resource.read()
                result = float(result)
                # self.delay = self.delay * 0.95
            except VisaIOError as e:
                self.delay = self.delay * 1.1
        return result


class VoltageSource(PowerChannel):
    """
    Knows about voltage states, using modes to interpret the multipliers
    """

    def __init__(self, usb: int = 0, manufacturer_id: str = '0x0483', model_code: str = '0x7540',
                 serial_number: str = 'SPD3ECAX1L1560', channel_3_voltage: float = 5.0, output_mode: int = 0):
        if output_mode == 0:
            channel = ("CH1", "CH2", "CH3")
        else:
            channel = ("CH1", "CH3")

        super().__init__(usb=usb, manufacturer_id=manufacturer_id, model_code=model_code, serial_number=serial_number
                         , output_mode=output_mode)

        # Set the channels to Voltage mode by setting the max output current to the physical maximum
        if self.output_mode == 'Independent':
            self.current_setting_ch1 = 3.2
            self.current_setting_ch2 = 3.2
            super().set_channel_current(self.channel_1, self.current_setting_ch1)
            super().set_channel_current(self.channel_2, self.current_setting_ch2)
        if self.output_mode == 'Parallel':
            self.current_setting_ch1 = 6.4
            self.current_setting_ch2 = 0
            super().set_channel_current(self.channel_1, self.current_setting_ch1)
        if self.output_mode == 'Series':
            self.current_setting_ch1 = 3.2
            self.current_setting_ch2 = 3.2
            super().set_channel_current(self.channel_1, self.current_setting_ch1)

        self.voltage_max_ch3 = channel_3_voltage

        # Set channels into safe mode
        # All channels start as 'OFF' = 0v
        self.voltage_setting_ch1 = 0
        self.voltage_setting_ch2 = 0

        super().set_channel_voltage(self.channel_1, self.voltage_setting_ch1)
        super().set_channel_voltage(self.channel_2, self.voltage_setting_ch2)
        self.voltage_setting_ch3 = 0  # Channel 3 is OFF so 0v

    def set_channel_voltage(self, channel: str = "CH1", value: float = 0.0, power_on: bool = True):
        if channel == "CH3":
            result = self.voltage_max_ch3
        else:
            if self.output_mode == 'Series':
                setting = value / 2.0
            else:
                setting = value
            super().set_channel_voltage(channel=channel, value=setting)

        if channel == 'CH1':
            self.voltage_setting_ch1 = value
        elif channel == 'CH2':
            self.voltage_setting_ch2 = value
        else:
            self.voltage_setting_ch3 = value

        # result = self.get_output_voltage(channel=channel)
        return value

    def get_output_voltage(self, channel: str = "CH1") -> float:
        voltage_reading = None
        if channel == 'CH3' and self.channel_3_state == 'ON':
            voltage_reading = self.voltage_max_ch3
        elif channel == 'CH3' and self.channel_3_state == 'OFF':
            voltage_reading = 0
        else:
            if self.output_mode == 'Independent' and (channel == 'CH1' or channel == "CH2"):
                voltage = super().get_channel_voltage(channel=self.channel_1)
                self.voltage_setting_ch1 = voltage
                voltage = super().get_channel_voltage(channel=self.channel_2)
                self.voltage_setting_ch2 = voltage
            elif self.output_mode == 'Parallel' and (channel == 'CH1' or channel == "CH2"):
                voltage = super().get_channel_voltage(channel=self.channel_1)
                self.voltage_setting_ch1 = voltage
                self.voltage_setting_ch1 = voltage
            elif self.output_mode == 'Series' and (channel == 'CH1' or channel == "CH2"):
                voltage = super().get_channel_voltage(channel=self.channel_1)
                voltage_reading = voltage * self.voltage_multiplier
                self.voltage_setting_ch1 = voltage
                self.voltage_setting_ch2 = 0

        return voltage_reading


class CurrentSource(PowerChannel):
    """
    Knows about current states, using modes to interpret the multipliers
    """

    def __init__(self, usb: int = 0, manufacturer_id: str = '0x0483', model_code: str = '0x7540',
                 serial_number: str = 'SPD3ECAX1L1560', output_mode: int = 0):

        super().__init__(usb=usb, manufacturer_id=manufacturer_id, model_code=model_code, serial_number=serial_number
                         , output_mode=output_mode)

        # Set the channels to Voltage mode by setting the max output current to the physical maximum
        if self.output_mode == 'Independent':
            self.voltage_setting_ch1 = 32
            self.voltage_setting_ch2 = 32
            super().set_channel_voltage(self.channel_1, self.voltage_setting_ch1)
            super().set_channel_voltage(self.channel_2, self.voltage_setting_ch2)
        if self.output_mode == 'Parallel':
            self.voltage_setting_ch1 = 32
            self.voltage_setting_ch2 = 0
            super().set_channel_voltage(self.channel_1, self.voltage_setting_ch1)
        if self.output_mode == 'Series':
            self.voltage_setting_ch1 = 64
            self.voltage_setting_ch2 = 0
            super().set_channel_voltage(self.channel_1, self.voltage_setting_ch1)

        self.current_max_ch3 = 3.2

        # Set channels into safe mode
        # All channels start as 'OFF' = 0v
        self.current_setting_ch1 = 0
        self.current_setting_ch2 = 0

        super().set_channel_current(self.channel_1, self.current_setting_ch1)
        super().set_channel_current(self.channel_2, self.current_setting_ch2)
        self.current_setting_ch3 = 0  # Channel 3 is OFF so 0v

    def set_channel_current(self, channel: str = "CH1", value: float = 0.0, power_on: bool = True):
        if self.output_mode == 'Parallel':
            setting = value / 2.0
        else:
            setting = value
        super().set_channel_current(channel=channel, current=setting)

        if channel == 'CH1':
            self.current_setting_ch1 = value
        elif channel == 'CH2':
            self.current_setting_ch2 = value

        return value

    def get_output_current(self, channel: str = "CH1") -> float:
        current_reading = None
        if channel == 'CH3' and self.channel_3_state == 'ON':
            current_reading = self.current_max_ch3
        elif channel == 'CH3' and self.channel_3_state == 'OFF':
            current_reading = 0
        else:
            if self.output_mode == 'Independent':
                current = super().get_channel_current(channel=channel)
                if channel == "CH1":
                    self.current_setting_ch1 = current
                elif channel == "CH2":
                    self.current_setting_ch2 = current
                else:
                    self.current_setting_ch3 = current

            elif self.output_mode == 'Parallel' and (channel == 'CH1' or channel == "CH2"):
                voltage = super().get_channel_voltage(channel=self.channel_1)
                self.voltage_setting_ch1 = voltage
                self.voltage_setting_ch1 = voltage
            elif self.output_mode == 'Series' and (channel == 'CH1' or channel == "CH2"):
                current = super().get_channel_current(channel=self.channel_1)
                current_reading = current * self.voltage_multiplier
                self.current_setting_ch1 = current
                self.current_setting_ch2 = 0

        return current_reading


# class IndependentVoltageSource:
#     def __init__(self, usb: int = 0, manufacturer_id: str = '0x0483', model_code: str = '0x7540',
#                  serial_number: str = 'SPD3ECAX1L1560'):
#         self.voltage_source = VoltageSource(usb = 0, manufacturer_id = '0x0483', model_code  = '0x7540',
#                  serial_number = 'SPD3ECAX1L1560', output_mode=0)
#
#     def set_output_1(self, value:float = 0.0):
#         super().set_channel_voltage(channel = self.channel, value= 0.0)
#
# class ParallelVoltageSource(VoltageSource):
#     pass
#
# class SeriesVoltageSource(VoltageSource):
#     pass

if __name__ == '__main__':

    with PowerChannel() as p:
        p.set_channel_power_on("CH1")
        p.set_channel_power_off("CH1")
        p.set_channel_power_on("CH2")
        p.set_channel_power_off("CH2")
        p.set_channel_power_on("CH3")
        p.set_channel_power_off("CH3")

    p = None

    with PowerChannel() as p:
        p.set_channel_power_on("CH1")
        p.set_channel_power_on("CH2")
        p.set_channel_power_on("CH3")

    p = None

    output_voltages = [1.0, 0.5, 0.0, 0.5, 1.0]
    with VoltageSource() as p:
        p.set_channel_power_on("CH1")
        for output_voltage in output_voltages:
            p.set_channel_voltage("CH1", output_voltage)
        p.set_channel_power_off("CH1")

        p.set_channel_power_on("CH2")
        for output_voltage in output_voltages:
            p.set_channel_voltage("CH2", output_voltage)
        p.set_channel_power_off("CH2")

    p = None

    # output_voltages = [round((v/100)*6.4,2) for v in range(101)]
    output_voltages = [0,1] * 100
    with VoltageSource() as p:
        while True:
            p.set_channel_power_on("CH1")
            for output_voltage in output_voltages:
                # print(output_voltage)
                p.set_channel_voltage("CH1", output_voltage)
            print(p.delay)

    # output_voltages = [round((v/100)*6.4,2) for v in range(101)]
    output_currents = [round((v / 100) * 3.1, 2) for v in range(101)]
    with CurrentSource() as p:
        while True:
            p.set_channel_power_on("CH1")
            for output_current in output_currents:
                print(output_current)
                p.set_channel_current("CH1", output_current)
            print(p.delay)