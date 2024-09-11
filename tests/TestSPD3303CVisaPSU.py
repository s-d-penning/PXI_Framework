import logging
import math

from src.pyvisa.Power import VoltagePowerSource

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


def test_current_mode():
    logger.debug('Test independent mode, channel 1')
    logger.debug('Create VoltagePowerSource')
    spd3030c_channel_0_independent = VoltagePowerSource(resource_name='USB0::0x0483::0x7540::SPD3ECAX1L1560::INSTR',
                                                        channel='CH1',
                                                        channel_config=0,
                                                        mode='current')

    with spd3030c_channel_0_independent:
        logger.debug('Power on the voltage source')
        channel_state = spd3030c_channel_0_independent.set_power_on()
        logger.debug(f'Channel state: {channel_state}')

        p_max = 10
        r = 1
        i_max = round(math.sqrt(p_max / r), 2)

        v_max = round(i_max * 2, 2)

        i_step = 0.1
        # i_max = 2.0
        i_steps = int(i_max / i_step) + 1
        i_range = [round(i * i_step, 4) for i in range(i_steps)]
        for i_out in i_range:
            spd3030c_channel_0_independent.set_output_current(i_out)
            v_out_result = spd3030c_channel_0_independent.get_output_voltage()
            i_out_result = spd3030c_channel_0_independent.get_output_current()
            p_out_result = spd3030c_channel_0_independent.get_output_power()
            logger.debug(f'{i_out},{i_out_result},{v_out_result},{p_out_result}')

    logger.debug('Test parallel mode, channel 1')
    spd3030c_channel_0_parallel = VoltagePowerSource(resource_name='USB0::0x0483::0x7540::SPD3ECAX1L1560::INSTR',
                                                     channel='CH1',
                                                     channel_config=1)
    with spd3030c_channel_0_parallel:
        logger.debug('Power on the voltage source')
        channel_state = spd3030c_channel_0_parallel.set_power_on()
        logger.debug(f'Channel state: {channel_state}')

        p_max = 10
        r = 1
        i_max = round(math.sqrt(p_max / r), 2)

        v_max = round(i_max * 2, 2)

        i_step = 0.1
        # i_max = 2.0
        i_steps = int(i_max / i_step) + 1
        i_range = [round(i * i_step, 4) for i in range(i_steps)]
        for i_out in i_range:
            spd3030c_channel_0_parallel.set_output_current(i_out)
            v_out_result = spd3030c_channel_0_parallel.get_output_voltage()
            i_out_result = spd3030c_channel_0_parallel.get_output_current()
            p_out_result = spd3030c_channel_0_parallel.get_output_power()
            logger.debug(f'{i_out},{i_out_result},{v_out_result},{p_out_result}')


def test_voltage_mode():
    logger.debug('Test independent mode, channel 1')
    logger.debug('Create VoltagePowerSource')
    spd3030c_channel_0_independent = VoltagePowerSource(resource_name='USB0::0x0483::0x7540::SPD3ECAX1L1560::INSTR',
                                                        channel='CH1',
                                                        channel_config=0,
                                                        mode='voltage')
    with spd3030c_channel_0_independent:
        logger.debug('Power on the voltage source')
        channel_state = spd3030c_channel_0_independent.set_power_on()
        logger.debug(f'Channel state: {channel_state}')

        p_max = 10
        r = 1
        i_max = round(math.sqrt(p_max / r), 2)

        v_max = round(i_max * 2, 2)

        v_step = 0.1
        # v_max = 12.0
        v_steps = int(v_max / v_step) + 1

        v_range = [round(v * v_step, 4) for v in range(v_steps)]
        for v_out in v_range:
            spd3030c_channel_0_independent.set_output_voltage(v_out)
            v_out_result = spd3030c_channel_0_independent.get_output_voltage()
            i_out_result = spd3030c_channel_0_independent.get_output_current()
            p_out_result = spd3030c_channel_0_independent.get_output_power()
            logger.debug(f'{v_out},{v_out_result},{i_out_result},{p_out_result}')

    logger.debug('Test series mode, channel 1/2')
    logger.debug('Create VoltagePowerSource')
    spd3030c_channel_0_series = VoltagePowerSource(resource_name='USB0::0x0483::0x7540::SPD3ECAX1L1560::INSTR',
                                                   channel='CH1',
                                                   channel_config=1)
    with spd3030c_channel_0_series:
        logger.debug('Power on the voltage source')
        channel_state = spd3030c_channel_0_series.set_power_on()
        logger.debug(f'Channel state: {channel_state}')

        p_max = 10
        r = 1
        i_max = round(math.sqrt(p_max / r), 2)

        v_max = round(i_max * 2, 2)

        v_step = 0.1
        # v_max = 12.0
        v_steps = int(v_max / v_step) + 1
        v_range = [round(v * v_step, 4) for v in range(v_steps)]
        for v_out in v_range:
            spd3030c_channel_0_series.set_output_voltage(v_out)
            v_out_result = spd3030c_channel_0_series.get_output_voltage()
            i_out_result = spd3030c_channel_0_series.get_output_current()
            p_out_result = spd3030c_channel_0_series.get_output_power()
            logger.debug(f'{v_out},{v_out_result},{i_out_result},{p_out_result}')

    logger.debug('Test parallel mode, channel 1/2')
    logger.debug('Create VoltagePowerSource')
    spd3030c_channel_0_parallel = VoltagePowerSource(resource_name='USB0::0x0483::0x7540::SPD3ECAX1L1560::INSTR',
                                                     channel='CH1',
                                                     channel_config=2)
    with spd3030c_channel_0_parallel:
        logger.debug('Power on the voltage source')
        channel_state = spd3030c_channel_0_parallel.set_power_on()
        logger.debug(f'Channel state: {channel_state}')

        p_max = 10
        r = 1
        i_max = round(math.sqrt(p_max / r), 2)
        v_max = round(i_max * 2, 2)

        v_step = 0.1
        # v_max = 12.0
        v_steps = int(v_max / v_step) + 1
        v_range = [round(v * v_step, 4) for v in range(v_steps)]
        for v_out in v_range:
            spd3030c_channel_0_parallel.set_output_voltage(v_out)
            v_out_result = spd3030c_channel_0_parallel.get_output_voltage()
            i_out_result = spd3030c_channel_0_parallel.get_output_current()
            p_out_result = spd3030c_channel_0_parallel.get_output_power()
            logger.debug(f'{v_out},{v_out_result},{i_out_result},{p_out_result}')


if __name__ == '__main__':
    logger.debug('Starting test program')
    # test_current_mode()
    test_voltage_mode()
