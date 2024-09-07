from src.pyvisa.Power import VoltagePowerSource
import pyvisa
import logging
import math

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

    p_max = 10
    r = 1
    i_max = round(math.sqrt(p_max/r),2)

    v_max = round(i_max * 2,2)
    spd3030c_channel_0.set_output_voltage(v_max)

    i_step = 0.1
    # i_max = 2.0
    i_steps = int(i_max/i_step) + 1
    i_range = [round(i*i_step,4) for i in range(i_steps)]
    for i_out in i_range:
        spd3030c_channel_0.set_current_limit(i_out)
        v_out_result = spd3030c_channel_0.get_output_voltage()
        i_out_result = spd3030c_channel_0.get_output_current()
        p_out_result = spd3030c_channel_0.get_output_power()
        logger.debug(f'{i_out},{i_out_result},{v_out_result},{p_out_result}')


