import pickle as pkl
import socket
import struct

#from private_data import private_keys

class BaseWriter(object):
  def expand_data(self, data_points):
    all_data = []
    for key in data_points:
      for ts, value in data_points[key]:
        all_data.append((key, value, ts))
    return all_data

  def write_data(self, data_points):
    for key, data, ts in self.expand_data(data_points):
      print('Key {} - Value {} - Timestamp {}'.format(key, data, ts))


class CarbonWriter(BaseWriter):
  def __init__(self, carbon_server, carbon_port):
    self._CARBON_SERVER = carbon_server
    self._CARBON_PORT = carbon_port

  def write_data(self, data_points):
    for key, data, ts in self.expand_data(data_points):
      message = '%s %s %d\n' % (key, data, ts)
      print('Sending message: %s' % message)

      sock = socket.socket()
      sock.connect((self._CARBON_SERVER,
                    self._CARBON_PORT))
      sock.sendall(message.encode())
      sock.close()

class CarbonPickleWriter(CarbonWriter):
  def write_data(self, data_points):
    sub_data = []
    for key, data, ts in self.expand_data(data_points):
      sub_data.append((key, (ts, data)))
    payload = pkl.dumps(sub_data, protocol=2)
    header = struct.pack("!L", len(payload))
    message = header + payload

    print('Sending pickle: %s' % sub_data)
    sock = socket.socket()
    sock.connect((self._CARBON_SERVER,
                  self._CARBON_PORT))
    sock.sendall(message)
    sock.close()
  