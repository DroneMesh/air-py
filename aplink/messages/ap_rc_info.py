"""

AirPy - MicroPython based autopilot v. 0.0.1

Created on Sun Dec 13 23:32:24 2015

@author: Fabrizio Scimia

Revision History:

28-Jan-2016 Initial Release

"""


class RcInfo:
    def __init__(self, h_builder, attitude):

        self.attitude_controller = attitude
        self.header_builder = h_builder
        self.QCI = 0
        self.MESSAGE_TYPE_ID = 20
        # self.PAYLOAD = b'\xFF'
        self.PAYLOAD = (self.attitude_controller.get_rc_controller()).get_channels()
        self.PAYLOAD_LENGTH = len(self.PAYLOAD)
        self.EOF = self.PAYLOAD[0]
        self.header = bytearray(h_builder.get_header(self))
        self.message = self.header + bytearray(self.PAYLOAD)

    def get_bytes(self):
        return self.message



