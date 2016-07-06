"""
airPy is a flight controller based on pyboard and written in micropython.

The MIT License (MIT)
Copyright (c) 2016 Fabrizio Scimia, fabrizio.scimia@gmail.com
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from pyb import Pin, Timer
import util.airpy_logger as logger
import array


class EscController:

    def __init__(self, config_m, pwm_rate):

        # ESC parameters
        self.esc_pwm_min_cmd = config_m.get_param_set('esc', 'esc_pwm_min_cmd')
        self.esc_pwm_center = config_m.get_param_set('esc', 'esc_pwm_center')
        self.esc_pwm_min = config_m.get_param_set('esc', 'esc_pwm_min')
        self.esc_pwm_max = config_m.get_param_set('esc', 'esc_pwm_max')
        self.esc_low_range = self.esc_pwm_center - self.esc_pwm_min
        self.esc_high_range = self.esc_pwm_max - self.esc_pwm_center
        self.esc_full_range = self.esc_pwm_max - self.esc_pwm_min
        self.tmp_pwm = None

        # Threshold at 10% for the PID start working
        self.esc_pid_threshold = int(0.1*(self.esc_pwm_max - self.esc_pwm_min)) + self.esc_pwm_min

        # PWM initialization TODO: hexacopter handling
        self._num_motors = config_m.get_param('num_motors')
        self.pulse_widths = array.array('H', [0, 0, 0, 0])  # TODO: initialize based on # of motors

        # TODO: GENERALIZE
        # set PWM to 400Hz TODO: set freq according to settings
        self._timers = [Timer(config_m.get_param_set('esc', 'quadcopter')['timers'][index],
                              prescaler=83, period=2499) for index in range(0, self._num_motors)]

        self._escs = [self._timers[index].channel(config_m.get_param_set('esc',
                                                                         'quadcopter')['channels'][index],
                                                  Timer.PWM,
                                                  pin=Pin(config_m.get_param_set('esc',
                                                                                 'quadcopter')['pins'][index]
                                                          )
                                                  ) for index in range(0, self._num_motors)]

        logger.info("Esc Controller Started")

    def set_thrust_passthrough(self, pwm):

        for j in range(0, self._num_motors):
            self._escs[j].pulse_width(pwm)

    def set_zero_thrust(self):
        # set the thrust of all the motors to 0. Used for esc setup
        self.pulse_widths = [self.esc_pwm_min_cmd for i in range(0, self._num_motors)]  # used for aplink report
        for j in range(0, self._num_motors):
            self._escs[j].pulse_width(self.esc_pwm_min_cmd)

    def set_thrust(self, widths):

            self.pulse_widths = [min(max(self.esc_pwm_min, widths[0] - widths[1] - widths[2] - widths[3]), self.esc_pwm_max),
                                 min(max(self.esc_pwm_min, widths[0] + widths[1] + widths[2] - widths[3]), self.esc_pwm_max),
                                 min(max(self.esc_pwm_min, widths[0] - widths[1] + widths[2] + widths[3]), self.esc_pwm_max),
                                 min(max(self.esc_pwm_min, widths[0] + widths[1] - widths[2] + widths[3]), self.esc_pwm_max)]

            for k in range(0, self._num_motors):
                self._escs[k].pulse_width(self.pulse_widths[k])
