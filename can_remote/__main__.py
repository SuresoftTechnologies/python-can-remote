#!/usr/bin/env python
import logging
import argparse
try:
    import ssl
except ImportError:
    ssl = None
import can
from .server import RemoteServer
from . import DEFAULT_PORT

logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.DEBUG)
can.set_logging_level("DEBUG")


def main():
    parser = argparse.ArgumentParser(description="Remote CAN server")

    parser.add_argument('-v', action='count', dest="verbosity",
                        help='''How much information do you want to see at the command line?
                        You can add several of these e.g., -vv is DEBUG''', default=3)

    parser.add_argument('-c', '--channel', help='''Most backend interfaces require some sort of channel.
    For example with the serial interface the channel might be a rfcomm device: "/dev/rfcomm0"
    With the socketcan interfaces valid channel examples include: "can0", "vcan0".
    The server will only serve this channel. Start additional servers at different
    ports to share more channels.''')

    parser.add_argument('-i', '--interface',
                        help='''Specify the backend CAN interface to use. If left blank,
                        fall back to reading from configuration files.''',
                        choices=can.VALID_INTERFACES)

    parser.add_argument('-b', '--bitrate', type=int,
                        help='''Force to use a specific bitrate.
                        This will override any requested bitrate by the clients.''')

    parser.add_argument('-H', '--host',
                        help='''Host to listen to (default 0.0.0.0).''',
                        default='0.0.0.0')

    parser.add_argument('-p', '--port', type=int,
                        help='''TCP port to listen on (default %d).''' % DEFAULT_PORT,
                        default=DEFAULT_PORT)

    if ssl is not None:
        parser.add_argument('-C', '--cert',
                            help='SSL certificate in PEM format')

        parser.add_argument('-K', '--key',
                            help='''SSL private key in PEM format
                            (optional if provided in cert file)''')

    results = parser.parse_args()

    verbosity = results.verbosity
    logging_level_name = ['critical', 'error', 'warning', 'info', 'debug', 'subdebug'][min(5, verbosity)]
    can.set_logging_level(logging_level_name)

    config = {}
    if results.channel:
        config["channel"] = results.channel
    if results.interface:
        config["bustype"] = results.interface
    if results.bitrate:
        config["bitrate"] = results.bitrate

    if results.cert and ssl is not None:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=results.cert, keyfile=results.key)
    else:
        context = None

    server = RemoteServer(results.host, results.port,
                          ssl_context=context, **config)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    logging.info("Closing server")
    server.server_close()


if __name__ == "__main__":
    main()
