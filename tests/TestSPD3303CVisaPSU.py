from src.pyvisa.Power import VoltagePowerSource
import pyvisa
import logging

logger = logging.getLogger('__main__')
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

if __name__ == '__main__':
    logger.debug('Starting test program')
    logger.debug('Create VoltagePowerSource')
    spd3030c_channel_0 = VoltagePowerSource(resource_name='USB0::0x0483::0x7540::SPD3ECAX1L1560::INSTR', channel='CH1',channel_config=2)

    logger.debug('Power on the voltage source')
    channel_state = spd3030c_channel_0.set_power_on()
    logger.debug(f'channel_state: {channel_state}')
    logger.debug('Measure the output voltage')
    v_out = spd3030c_channel_0.get_output_voltage()
    logger.debug(f'v_out: {v_out}')
    logger.debug('Measure the output current')
    i_out = spd3030c_channel_0.get_output_current()
    logger.debug(f'i_out: {i_out}')
    logger.debug('Measure the output power')
    p_out = spd3030c_channel_0.get_output_power()
    logger.debug(f'p_out: {p_out}')
    logger.debug('Power off the voltage source')
    channel_state = spd3030c_channel_0.set_power_off()
    logger.debug(f'channel_state: {channel_state}')

    v_out = 1.0
    logger.debug(f'Set the voltage to {v_out}')
    v_out = spd3030c_channel_0.set_output_voltage(v_out)
    logger.debug(f'v_out: {v_out}')

    i_out = 3.2
    logger.debug(f'Set the current limit to {i_out}')
    v_out = spd3030c_channel_0.set_current_limit(i_out)
    logger.debug(f'i_out: {i_out}')

    logger.debug('Power on the voltage source')
    channel_state = spd3030c_channel_0.set_power_on()
    logger.debug(f'channel_state: {channel_state}')
    logger.debug('Measure the output voltage')
    v_out = spd3030c_channel_0.get_output_voltage()
    logger.debug(f'v_out: {v_out}')
    logger.debug('Measure the output current')
    i_out = spd3030c_channel_0.get_output_current()
    logger.debug(f'i_out: {i_out}')
    logger.debug('Measure the output power')
    p_out = spd3030c_channel_0.get_output_power()
    logger.debug(f'p_out: {p_out}')
    logger.debug('Power off the voltage source')
    channel_state = spd3030c_channel_0.set_power_off()
    logger.debug(f'channel_state: {channel_state}')

    v_out = 2.0
    logger.debug(f'Set the voltage to {v_out}')
    v_out = spd3030c_channel_0.set_output_voltage(v_out)
    logger.debug(f'v_out: {v_out}')

    i_out = 3.2
    logger.debug(f'Set the current limit to {i_out}')
    v_out = spd3030c_channel_0.set_current_limit(i_out)
    logger.debug(f'i_out: {i_out}')

    logger.debug('Power on the voltage source')
    channel_state = spd3030c_channel_0.set_power_on()
    logger.debug(f'channel_state: {channel_state}')
    logger.debug('Measure the output voltage')
    v_out = spd3030c_channel_0.get_output_voltage()
    logger.debug(f'v_out: {v_out}')
    logger.debug('Measure the output current')
    i_out = spd3030c_channel_0.get_output_current()
    logger.debug(f'i_out: {i_out}')
    logger.debug('Measure the output power')
    p_out = spd3030c_channel_0.get_output_power()
    logger.debug(f'p_out: {p_out}')
    logger.debug('Power off the voltage source')
    channel_state = spd3030c_channel_0.set_power_off()
    logger.debug(f'channel_state: {channel_state}')