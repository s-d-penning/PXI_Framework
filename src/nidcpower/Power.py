from src import nidcpower

import numpy as np


class VoltagePowerSource:
    def __init__(self, resource_name: str, independent_channels: bool = True,
                 min_voltage: float = 0.0, max_voltage: float = 20.0):
        # Uninitiated state
        self.initiated = 0
        self.power_state = 0
        self.voltage_setting = 0.0
        self.current_setting = 0.0
        self.session = nidcpower.Session(resource_name=resource_name)
        self.min_voltage = min_voltage
        self.max_voltage = max_voltage
        self.resource_name = resource_name
        self.independent_channels = independent_channels
        self.session.measure_when = nidcpower.MeasureWhen.ON_DEMAND
        self.set_output_voltage(0.0)

    def __del__(self):
        # Set the output voltage to zero so we know the output is 'off'
        self.power_off()
        # Release the resource. This leaves the PSU at whatever state it was in!
        self.session.close()

    def power_on(self):
        if self.initiated == 0:
            self.session.initiate()
            self.initiated = 1
        self.power_state = 1
        self.set_output_voltage(self.voltage_setting)

    def power_off(self):
        self.session.voltage_level = 0
        self.session.commit()
        self.power_state = 0

    def output_voltage(self):
        if self.initiated == 1:
            self.voltage_setting = self.session.measure(nidcpower.MeasurementTypes.VOLTAGE)
        return self.voltage_setting

    def output_current(self):
        if self.initiated == 1:
            self.current_setting = self.session.measure(nidcpower.MeasurementTypes.CURRENT)
        return self.current_setting

    def output_power(self):
        output_voltage = self.output_voltage()
        output_current = self.output_current()
        output_power = output_voltage * output_current
        return output_power

    def set_output_voltage(self, voltage: float):
        self.voltage_setting = voltage
        if self.power_state == 1:
            self.session.voltage_level = self.voltage_setting
            self.session.commit()
            self.voltage_setting = self.output_voltage()

        return self.voltage_setting

    def change_voltage(self, pct: float = 0.0):
        output_voltage = self.output_voltage()
        dv = self.max_voltage * pct / 100.0
        new_output_voltage = output_voltage + dv
        if abs(new_output_voltage) <= abs(self.max_voltage):
            output_voltage = self.set_output_voltage(new_output_voltage)
        else:
            output_voltage = self.output_voltage()
        return output_voltage

    def set_min_voltage(self, sample_size: int = 1) -> np.floating:
        output_voltage = self.set_output_voltage(self.min_voltage)
        return output_voltage

    def set_max_voltage(self, sample_size: int = 1):
        output_voltage = self.set_output_voltage(self.max_voltage)
        return output_voltage


class CurrentPowerSource:
    def __init__(self, resource_name: str, independent_channels: bool = True,
                 min_current: float = 0.01, max_current: float = 1.0):
        # Uninitiated state
        self.initiated = 0
        self.power_state = 0
        self.voltage_setting = 0.0
        self.current_setting = min_current
        self.session = nidcpower.Session(resource_name=resource_name)
        self.min_current = min_current
        self.max_current = max_current
        self.resource_name = resource_name
        self.independent_channels = independent_channels
        self.session.measure_when = nidcpower.MeasureWhen.ON_DEMAND
        self.set_output_current(0.0)

    def __del__(self):
        # Set the output voltage to zero so we know the output is 'off'
        self.power_off()
        # Release the resource. This leaves the PSU at whatever state it was in!
        self.session.close()

    def power_on(self):
        if self.initiated == 0:
            self.session.initiate()
            self.initiated = 1
        self.power_state = 1
        self.set_output_current(self.current_setting)

    def power_off(self):
        self.session.current_level = self.min_current
        self.session.commit()
        self.power_state = 0

    def output_voltage(self):
        if self.initiated == 1:
            self.voltage_setting = self.session.measure(nidcpower.MeasurementTypes.VOLTAGE)
        return self.voltage_setting

    def output_current(self):
        if self.initiated == 1:
            self.current_setting = self.session.measure(nidcpower.MeasurementTypes.CURRENT)
        return self.current_setting

    def output_power(self):
        output_voltage = self.output_voltage()
        output_current = self.output_current()
        output_power = output_voltage * output_current
        return output_power

    def set_output_current(self, current: float):
        if self.power_state == 1:
            if current < self.min_current:
                self.current_setting = self.min_current
            elif self.min_current <= current <= self.max_current:
                self.current_setting = current
            else:
                self.current_setting = self.max_current

            self.session.current_level = self.current_setting
            self.session.commit()
            self.current_setting = self.output_current()

        return self.current_setting

    def change_current(self, pct: float = 0.0):
        output_current = self.output_current()
        di = self.max_current * pct / 100.0
        new_output_current = output_current + di
        if abs(new_output_current) <= abs(self.max_current):
            output_current = self.set_output_current(new_output_current)
        else:
            output_current = self.output_current()
        return output_current

    def set_min_current(self) -> np.floating:
        self.current_setting = self.set_output_current(self.min_current)
        return self.current_setting

    def set_max_current(self):
        self.current_setting = self.set_output_current(self.max_current)
        return self.current_setting
