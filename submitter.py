import pickle as pkl
import socket
import struct

from private_data import private_keys

def printer_submitter(data_point):
  metric, data, ts = data_point
  print(metric, data, ts)

def carbon_submitter(data_point):
  metric, data, ts = data_point
  message = '%s %s %d\n' % (metric, data, ts)

  print('Sending message: %s' % message)
  sock = socket.socket()
  sock.connect((private_keys.CARBON_SERVER,
                private_keys.CARBON_PORT))
  sock.sendall(message.encode())
  sock.close()

def carbon_pickle_submitter(data_points):
  sub_data = []
  for d in data_points:
    metric, data, ts = d
    sub_data.append((metric, (ts, data)))
  payload = pkl.dumps(sub_data, protocol=2)
  header = struct.pack("!L", len(payload))
  message = header + payload

  print('Sending pickle: %s' % sub_data)
  sock = socket.socket()
  sock.connect((private_keys.CARBON_SERVER,
                private_keys.CARBON_PICKLE_PORT))
  sock.sendall(message)
  sock.close()
  