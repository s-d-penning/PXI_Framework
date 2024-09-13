import pyvisa
from pyvisa import ResourceManager, VisaIOError
from pyvisa.resources.usb import USBInstrument
from pyvisa.constants import AccessModes

from time import sleep, time
import logging
import time

logger = logging.getLogger('VoltagePowerSource')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('Power.Py [%(asctime)s] %(lineno)d %(levelname)s - %(message)s','%m-%d %H:%M:%S')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class VoltagePowerSource:
    def __init__(self, resource_name: str,
                 channel: str = 'CH1',
                 channel_config: int = 0,
                 min_voltage: float = 0.0, max_voltage: float = 32.0,
                 max_current:float = 3.2,
                 mode = 'voltage',
                 delay=0.1):
        """
        Initialises one channel of the SPD3303C Power supply

        :param resource_name: VISA resource name
        :param channel: CH1 or CH2
        :param channel_config: {0[Independent] | 1[Series] | 2[Parallel]}
        :param min_voltage: 0 (Volts)
        :param max_voltage: 32.0 (Volts) for Independent mode, 64.0 (Volts) for Series mode
        :param max_current: 3.2 (Current) for Series and Independent modes, 6.4 for Parallel mode
        :param mode: voltage or current mode
        """
        logger.debug(f'Initializing {resource_name}: {channel}, {channel_config}, {min_voltage}, {max_voltage}')

        self.delay_step = 0.1
        self.delay = delay
        self.status = bin(0x00)
        self.ch1_mode = 'Unknown'
        self.ch2_mode = 'Unknown'
        self.ch1_state = 'Unknown'
        self.ch2_state = 'Unknown'
        self.channel = 'Unknown'

        self.voltage_setting = 30
        self.current_setting = 3

        self.channel_config = channel_config
        self.min_voltage = min_voltage
        self.max_voltage = max_voltage
        self.resource_name = resource_name

        self.current_multiplier = 1
        self.voltage_multiplier = 1
        self.output_mode = 'Unknown'

        channel_upper = channel.upper()
        if channel_upper == 'CH1' or channel_upper == 'CH2':
            self.channel = channel_upper
        else:
            raise ValueError("Channel must be either: 'CH1' or 'CH2'")
        logger.debug(f'Using SPD3303C channel: {self.channel}')

        logger.debug('Acquiring PyVisa Resource Manager')
        self.resource_manager: ResourceManager = pyvisa.highlevel.ResourceManager()
        # self.resource_manager.query_delay = 0.5

        inst = 'USB0::0x0483::0x7540::SPD3ECAX1L1560::INSTR'
        logger.debug(f'Acquiring PyVisa Instrument {inst}')
        self.resource: USBInstrument = self.resource_manager.open_resource(resource_name =inst,
                                                                           access_mode = AccessModes.exclusive_lock)

        self.resource.clear()

        self.set_output_mode(0)
        sleep(0.1)
        self.set_output_mode(channel_config)

        logger.debug('Shutting down active channels')
        self.set_power_off()

        self.set_output_voltage(30)
        self.set_output_current(3)

        # if mode == 'voltage':
        #     self.set_output_voltage(0.1)
        #     self.set_output_current(3)
        # else:
        #     self.set_output_current(0.1)
        #     self.set_output_voltage(30)

        self.refresh_status()

    def __enter__(self):
        return self.resource_manager

    def __close__(self):
        self.resource_manager.close()

    def __exit__(self, type, value, traceback):
        # Set the output voltage to zero so we know the output is 'off'
        logger.debug('Quitting')
        try:
            logger.debug('Shutting power off')
            self.set_power_off()

            logger.debug('Closing resource')
            self.resource.close()
        except Exception as e:
            logger.error(e)

    def set_output_mode(self, mode: int) -> str:
        """
        Sets the output mode of the power supply
        :param mode: {0[Independent] | 1[Series] | 2[Parallel]}
        :return: Output mode (Independent|Series|Parallel)
        """
        if mode == 0:
            self.output_mode = 'Independent'
            self.voltage_multiplier = 1
            self.current_multiplier = 1
        elif mode == 1:
            self.output_mode = 'Series'
            self.voltage_multiplier = 2
            self.current_multiplier = 1
        elif mode == 2:
            self.output_mode = 'Parallel'
            self.voltage_multiplier = 1
            self.current_multiplier = 2
        else:
            raise ValueError("Channel config must be: 0,1 or 2")
        logger.debug(f'Setting output mode to {self.output_mode}')
        self.channel_config = mode
        rc = self.resource.write(f'OUTP:TRACK {self.channel_config}')
        sleep(self.delay)
        return self.output_mode

    def refresh_status(self) -> str:
        """
        Refresh the status of the power supply
        :return: Status of the power supply (Binary encoded string)
        """
        logger.debug('Refreshing status')
        status = None
        while status is None:
            try:
                rc = self.resource.write(f'SYST:STAT?')
                sleep(self.delay)
                status = self.resource.read()
            except Exception as e:
                self.delay += 0.1
                logger.error(e)

        self.status = bin(int(status, 16)).lstrip("0b").rjust(8,'0')
        logger.debug(f'Status is reported as : {self.status}')

        if self.status[-1] == '0':
            self.ch1_mode = 'CV'
        elif self.status[-1] == '1':
            self.ch1_mode = 'CC'
        logger.debug(f'ch1_mode: {self.ch1_mode}')

        if self.status[-5] == '0':
            self.ch1_state = 'Off'
        elif self.status[-5] == '1':
            self.ch1_state = 'On'
        logger.debug(f'ch1_state: {self.ch1_state}')

        if self.status[-2] == '0':
            self.ch2_mode = 'CV'
        elif self.status[-2] == '1':
            self.ch2_mode = 'CC'
        logger.debug(f'ch2_mode: {self.ch2_mode}')

        if self.status[-6] == '0':
            self.ch2_state = 'Off'
        elif self.status[-6] == '1':
            self.ch2_state = 'On'
        logger.debug(f'ch2_state: {self.ch2_state}')

        if self.status[-4] == '0' and self.status[-3] == '1':
            self.output_mode = 'Independent'
        elif self.status[-4] == '1' and self.status[-3] == '0':
            self.output_mode = 'Parallel'
        elif self.status[-4] == '1' and self.status[-3] == '1':
            self.output_mode = 'Series'

        logger.debug(f'output_mode: {self.output_mode}')
        return self.status

    def set_power_on(self) -> str:
        """
        Turns on the power for the configured channel
        :return: State of the configured channel
        """
        logger.debug(f'Set power on')
        rc = self.resource.write(f'OUTP {self.channel},ON')
        sleep(self.delay)
        self.refresh_status()
        if self.channel == 'CH1':
            return self.ch1_state
        else:
            return self.ch2_state

    def set_power_off(self) -> str:
        """
        Turns off the power for the configured channel
        :return:
        """
        logger.debug(f'Sending power off command to channel {self.channel}')
        try:
            rc = self.resource.write(f'OUTP {self.channel},OFF')
            sleep(self.delay)
            self.refresh_status()
        except VisaIOError as e:
            self.delay += self.delay_step
        if self.channel == 'CH1':
            return self.ch1_state
        else:
            return self.ch2_state

    def get_output_voltage(self) -> float:
        """
        Reads the output voltage of the configured channel
        :return: output (Volts)
        """
        logger.debug(f'Get output voltage')

        result = None
        while result is None:
            logger.debug(f'Reading output voltage')
            try:
                rc = self.resource.write(f'MEAS:VOLT? {self.channel}') * self.voltage_multiplier
                sleep(self.delay)
                result = self.resource.read()
                self.voltage_setting = float(result) * self.voltage_multiplier
                logger.debug(f'Output voltage reads {self.voltage_setting} volts')
            except VisaIOError as e:
                logger.error(f'Increasing delay by {self.delay_step}')
                self.delay += self.delay_step
        return self.voltage_setting

    def get_output_current(self) -> float:
        """
        Reads the output current of the configured channel
        :return: Output current (Amps)
        """
        logger.debug(f'Get output current')

        result = None
        while result is None:
            logger.debug(f'Reading output current')
            try:
                rc = self.resource.write(f'MEAS:CURR? {self.channel}') * self.current_multiplier
                sleep(self.delay)
                result = self.resource.read()
                self.current_setting = float(result) * self.current_multiplier
                logger.debug(f'Output current reads {self.current_setting} amperes')
            except VisaIOError as e:
                logger.error(f'Increasing delay by {self.delay_step}')
                self.delay += self.delay_step
        return self.current_setting

    def get_output_power(self) -> float:
        """
        Calculates the output power of the configured channel
        :return: Output power (Watts)
        """
        logger.debug(f'Get output power')

        output_voltage = self.get_output_voltage()
        output_current = self.get_output_current()
        output_power = output_voltage * output_current
        return output_power

    def set_output_voltage(self, voltage: float) -> float:
        """
        Sets the output voltage for the configured channel
        :param voltage: Desired output voltage (Volts)
        :return: measured output voltage (Volts)
        """
        result = None
        while result is None:
            logger.debug(f'Set output voltage to {voltage}')
            try:
                setting = voltage / self.voltage_multiplier
                rc = self.resource.write(f'{self.channel}:VOLT {setting}')
                sleep(self.delay)
                result = self.get_output_voltage()
            except VisaIOError as e:
                logger.error(f'Increasing delay by {self.delay_step}')
                self.delay += self.delay_step
        return result

    def set_output_current(self, current: float) -> float:
        """
        Sets the output current for the configured channel
        :param current: Desired output current limit (Amps)
        :return: measured output current (Amps)
        """
        result = None
        while result is None:
            logger.debug(f'Set output current limit to {current}')
            try:
                current_setting = current / self.current_multiplier
                rc = self.resource.write(f'{self.channel}:CURR {current_setting}')
                sleep(self.delay)
                result = self.get_output_current()
            except VisaIOError as e:
                logger.error(f'Increasing delay by {self.delay_step}')
                self.delay += self.delay_step
        return result

    def change_voltage(self, pct: float = 0.0) -> float:
        """
        Changes the output voltage  by the specified pct until the voltage reaches the configured or hard positive or negative limit
        :param pct: percentage change (positive or negative)
        :return: Measured output voltage (Volts)
        """
        output_voltage = self.get_output_voltage()
        dv = self.max_voltage * pct / 100.0
        new_output_voltage = output_voltage + dv
        if abs(new_output_voltage) <= abs(self.max_voltage):
            output_voltage = self.set_output_voltage(new_output_voltage)
        else:
            output_voltage = self.get_output_voltage()
        return output_voltage

    def set_min_voltage(self, sample_size: int = 1) -> float:
        """
        Sets the output voltage of the configured channel to the minimum voltage configured for the channel
        :param sample_size: Number of samples to use for the measurement
        :return: Measured output voltage (Volts)
        """
        output_voltage = self.set_output_voltage(self.min_voltage)
        return output_voltage

    def set_max_voltage(self, sample_size: int = 1) -> float:
        """
        Sets the output voltage of the configured channel to the maximum voltage configured for the channel
        :param sample_size: Number of samples to use for the measurement
        :return: Measured output voltage (Volts)
        """
        output_voltage = self.set_output_voltage(self.max_voltage)
        return output_voltage