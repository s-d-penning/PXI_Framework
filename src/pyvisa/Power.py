import pyvisa
from pyvisa import ResourceManager

from time import sleep
import logging

logger = logging.getLogger('VoltagePowerSource')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class VoltagePowerSource:
    def __init__(self, resource_name: str,
                 channel: str = 'CH1',
                 channel_config: int = 1,
                 min_voltage: float = 0.0, max_voltage: float = 32.0):
        """
        Initialises one channel of the SPD3303C Power supply

        :param resource_name: VISA resource name
        :param channel: CH1 or CH2
        :param channel_config: {0[Independent] | 1[Series] | 2[Parallel]}
        :param min_voltage: 0 (Volts)
        :param max_voltage: 32.0 (Volts) for Independent mode, 64.0 (Volts) for Series mode
        """
        logger.debug(f'Initializing {resource_name}: {channel}, {channel_config}, {min_voltage}, {max_voltage}')

        self.status = bin(0x00)
        self.ch1_mode = 'Unknown'
        self.ch2_mode = 'Unknown'
        self.ch1_state = 'Unknown'
        self.ch2_state = 'Unknown'
        self.channel = 'Unknown'

        self.voltage_setting = 0.0
        self.current_setting = 0.0

        self.channel_config = channel_config
        self.min_voltage = min_voltage
        self.max_voltage = max_voltage
        self.resource_name = resource_name

        channel_upper = channel.upper()
        if channel_upper == 'CH1' or channel_upper == 'CH2':
            self.channel = channel_upper
            logger.debug(f'Using cSPD3303C channel: {self.channel}')
        else:
            raise ValueError("Channel must be either: 'CH1' or 'CH2'")
        logger.debug(f'Using channel: {self.channel}')

        if channel_config == '1':
            self.output_mode = 'Independent'
        elif channel_config == 2:
            self.output_mode = 'Parallel'
        elif channel_config == 3:
            self.output_mode = 'Series'
        else:
            raise ValueError("Channel config must be: 1,2 or 3")
        logger.debug(f'Set channel mode to {self.output_mode} mode')

        logger.debug('Acquiring PyVisa Resource Manager')
        self.resource_manager: ResourceManager = pyvisa.ResourceManager()

        logger.debug('Acquiring PyVisa Resource')
        self.resource: pyvisa.Resource = self.resource_manager.open_resource(resource_name)

        logger.debug('Shutting power off')
        self.set_power_off()

        self.refresh_status()

    def __del__(self):
        # Set the output voltage to zero so we know the output is 'off'
        logger.debug('Quitting')
        try:
            logger.debug('Shutting power off')
            self.set_power_off()

            logger.debug('Closing resource')
            self.resource.close()
        except Exception as e:
            logger.error(e)

    def set_output_mode(self, mode: int):
        """
        Sets the output mode of the power supply
        :param mode: {0[Independent] | 1[Series] | 2[Parallel]}
        :return:
        """
        logger.debug(f'Setting output mode to {mode}')
        if mode == '0':
            self.output_mode = 'Independent'
        elif mode == 1:
            self.output_mode = 'Series'
        elif mode == 2:
            self.output_mode = 'Parallel'
        else:
            raise ValueError("Channel config must be 0,1 or 2")
        logger.debug('Closing resource')

        self.channel_config = mode

        rc = self.resource.write('OUTP:TRACK {self.channel_config}')
        self.refresh_status()

    def refresh_status(self):
        """
        Refresh the status of the power supply
        :return:
        """
        logger.debug('Refreshing status')

        rc = self.resource.write(f'SYST:STAT?')
        sleep(0.1)
        status = self.resource.query(f'SYST:STAT?')

        self.status = bin(int(status, 16))
        logger.debug(f'Status is reported as : {status}')

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

    def set_power_on(self):
        """
        Turns on the power for the configured channel
        :return:
        """
        logger.debug(f'Set power on')
        rc = self.resource.write(f'OUTP {self.channel},ON')
        self.refresh_status()
        while (self.ch1_state == 'Off' and self.channel == 'CH1') or (
                self.ch2_state == 'Off' and self.channel == 'CH2'):
            rc = self.resource.write(f'OUTP {self.channel},ON')
            sleep(0.1)
            self.refresh_status()

    def set_power_off(self):
        """
        Turns off the power for the configured channel
        :return:
        """
        logger.debug(f'Set power off')
        rc = self.resource.write(f'OUTP {self.channel},OFF')
        self.refresh_status()
        while (self.ch1_state == 'On' and self.channel == 'CH1') or (self.ch2_state == 'On' and self.channel == 'CH2'):
            rc = self.resource.write(f'OUTP {self.channel},OFF')
            sleep(0.1)
            self.refresh_status()

    def get_output_voltage(self) -> float:
        """
        Reads the output voltage of the configured channel
        :return: output (Volts)
        """
        rc = self.resource.write(f'MEAS:VOLT? {self.channel}')
        sleep(0.1)
        result = self.resource.query(f'MEAS:VOLT? {self.channel}')
        # result = self.resource.read()
        self.voltage_setting = float(result)
        return self.voltage_setting

    def get_output_current(self) -> float:
        """
        Reads the output current of the configured channel
        :return: Output current (Amps)
        """
        self.resource.write(f'MEAS:CURR? {self.channel}')
        sleep(0.1)
        result = self.resource.query(f'MEAS:CURR? {self.channel}')
        # result = self.resource.read()
        self.current_setting = float(result)
        return self.current_setting

    def get_output_power(self) -> float:
        """
        Calculates the output power of the configured channel
        :return: Output power (Watts)
        """
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
        self.voltage_setting = voltage
        rc = self.resource.write(f'{self.channel}:VOLT {voltage}')
        self.voltage_setting = self.get_output_voltage()
        return self.voltage_setting

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
