"""

AirPy - MicroPython based autopilot v. 0.0.1

Created on Sun Dec 13 23:32:24 2015

@author: Fabrizio Scimia

Revision History:

20-Jan-2016 Initial Release

"""

import array


class ULScheduler:
    def __init__(self):
        # buffer to store msg in the queue
        self.msg_buffer = array.array('I', (0,)*1500)  # TODO: resize according with the link bit rate
        self.startIndex = 0
        self.endIndex = 0
        self.lostMsg = 0
        self.lock = False

    def add_msg(self, msg):
        self.lock = True
        if self.startIndex <= self.endIndex:
            if (self.endIndex + len(msg)) % len(self.msg_buffer) < self.startIndex:
                for i in range(0, len(msg)-1):
                    self.msg_buffer[(self.endIndex + i + 1) % len(self.msg_buffer)] = msg[i]
                self.endIndex = (self.endIndex + len(msg)) % len(self.msg_buffer)
            else:
                self.lostMsg += 1
        elif self.endIndex < self.startIndex:
            if (self.endIndex + len(msg)) < self.startIndex:
                for i in range(0, len(msg)-1):
                    self.msg_buffer[self.endIndex + i + 1] = msg[i]
                    self.endIndex += len(msg)
            else:
                self.lostMsg += 1
        self.lock = False

    def read_queue(self):
        if not self.lock:

            #TODO check start <> end

            single_byte = self.msg_buffer[self.startIndex]
            if self.startIndex + 1 > len(self.msg_buffer):
                self.startIndex = 0
            else:
                self.startIndex += 1
        else:
            single_byte = None
        return single_byte
