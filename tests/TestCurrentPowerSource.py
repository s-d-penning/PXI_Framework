from src.nidcpower.Power import CurrentPowerSource


if __name__ == '__main__':
    pxi_4110_channel_0 = CurrentPowerSource(resource_name='PXI_4110_1/1',
                                            min_current=0.01,
                                            max_current=1.00)
    
    v_out = pxi_4110_channel_0.output_voltage()
    i_out = pxi_4110_channel_0.output_current()
    p_out = pxi_4110_channel_0.output_power()
    print(f'{v_out:+#.5e} volts, {i_out:+#.5e} amps, {p_out:+#.5e} Watts')

    pxi_4110_channel_0.power_on()
    v_out = pxi_4110_channel_0.output_voltage()
    i_out = pxi_4110_channel_0.output_current()
    p_out = pxi_4110_channel_0.output_power()
    print(f'{v_out:+#.5e} volts, {i_out:+#.5e} amps, {p_out:+#.5e} Watts')
    pxi_4110_channel_0.power_off()

    pxi_4110_channel_0.set_output_current(0.01)
    pxi_4110_channel_0.power_on()
    v_out = pxi_4110_channel_0.output_voltage()
    i_out = pxi_4110_channel_0.output_current()
    p_out = pxi_4110_channel_0.output_power()
    print(f'{v_out:+#.5e} volts, {i_out:+#.5e} amps, {p_out:+#.5e} Watts')
    pxi_4110_channel_0.power_off()

    pxi_4110_channel_0.set_output_current(0.02)
    pxi_4110_channel_0.power_on()
    v_out = pxi_4110_channel_0.output_voltage()
    i_out = pxi_4110_channel_0.output_current()
    p_out = pxi_4110_channel_0.output_power()
    print(f'{v_out:+#.5e} volts, {i_out:+#.5e} amps, {p_out:+#.5e} Watts')
    pxi_4110_channel_0.power_off()

    pxi_4110_channel_0.set_output_current(0.03)
    pxi_4110_channel_0.set_output_current(0.04)
    pxi_4110_channel_0.power_on()
    v_out = pxi_4110_channel_0.output_voltage()
    i_out = pxi_4110_channel_0.output_current()
    p_out = pxi_4110_channel_0.output_power()
    print(f'{v_out:+#.5e} volts, {i_out:+#.5e} amps, {p_out:+#.5e} Watts')
    pxi_4110_channel_0.power_off()

    pxi_4110_channel_0.power_on()
    v_out = pxi_4110_channel_0.output_voltage()
    i_out = pxi_4110_channel_0.output_current()
    p_out = pxi_4110_channel_0.output_power()
    print(f'{v_out:+#.5e} volts, {i_out:+#.5e} amps, {p_out:+#.5e} Watts')

    pxi_4110_channel_0.set_output_current(0.05)
    v_out = pxi_4110_channel_0.output_voltage()
    i_out = pxi_4110_channel_0.output_current()
    p_out = pxi_4110_channel_0.output_power()
    print(f'{v_out:+#.5e} volts, {i_out:+#.5e} amps, {p_out:+#.5e} Watts')

    pxi_4110_channel_0.set_output_current(0.06)
    v_out = pxi_4110_channel_0.output_voltage()
    i_out = pxi_4110_channel_0.output_current()
    p_out = pxi_4110_channel_0.output_power()
    print(f'{v_out:+#.5e} volts, {i_out:+#.5e} amps, {p_out:+#.5e} Watts')
    pass