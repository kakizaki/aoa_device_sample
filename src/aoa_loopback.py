import sys
import usb.core


# AOA通信の送受信
def communicate(
    device: usb.core.Device, 
    endpoint_in: usb.core.Endpoint,
    endpoint_out: usb.core.Endpoint,
    config_protocol: dict
    ): 

    while True:
        try:
            # timeout=None ... デフォルトのタイムアウトの値が使用される (1秒)
            recv = device.read(endpoint_in.bEndpointAddress, 16384, timeout=None)
            print("Received: ", recv)
            print("Received(ascii): ", bytes(recv).decode('ascii').encode('ascii'))

            len = device.write(endpoint_out.bEndpointAddress, recv)
            print("write len:", len)

        except usb.core.USBError as e:
            # read or write timeout
            if e.errno == 110: 
                # print("timeout")
                continue

            # print("error:", e)
            # if e.errno != 10060:
            raise

