
#!/usr/bin/env python3
# coding=utf-8
"""
Upload a QGIS plugin package to the official QGIS plugin repository.
"""

import sys
import getpass
import base64
import xmlrpc.client
from optparse import OptionParser

# Configuration
PROTOCOL = "https"
SERVER = "plugins.qgis.org"
PORT = "443"
ENDPOINT = "/plugins/RPC2/"
VERBOSE = False


class BasicAuthTransport(xmlrpc.client.Transport):
    """XML-RPC transport with HTTP Basic authentication."""

    def __init__(self, username, password):
        super().__init__()
        credentials = f"{username}:{password}".encode("utf-8")
        token = base64.b64encode(credentials).decode("ascii")
        self.authorization = f"Basic {token}"

    def send_headers(self, connection, headers):
        headers.append(("Authorization", self.authorization))
        super().send_headers(connection, headers)


class BasicAuthSafeTransport(xmlrpc.client.SafeTransport):
    """HTTPS XML-RPC transport with HTTP Basic authentication."""

    def __init__(self, username, password):
        super().__init__()
        credentials = f"{username}:{password}".encode("utf-8")
        token = base64.b64encode(credentials).decode("ascii")
        self.authorization = f"Basic {token}"

    def send_headers(self, connection, headers):
        headers.append(("Authorization", self.authorization))
        super().send_headers(connection, headers)


def main(parameters, arguments):
    """Upload the plugin package."""

    address = "{}://{}:{}{}".format(
        PROTOCOL,
        parameters.server,
        parameters.port,
        ENDPOINT
    )

    print("Connecting to: {}".format(address))

    if PROTOCOL == "https":
        transport = BasicAuthSafeTransport(
            parameters.username,
            parameters.password
        )
    else:
        transport = BasicAuthTransport(
            parameters.username,
            parameters.password
        )

    server = xmlrpc.client.ServerProxy(
        address,
        transport=transport,
        verbose=VERBOSE
    )

    try:
        with open(arguments[0], "rb") as plugin_file:
            plugin_data = xmlrpc.client.Binary(plugin_file.read())

        plugin_id, version_id = server.plugin.upload(plugin_data)

        print("Plugin ID: {}".format(plugin_id))
        print("Version ID: {}".format(version_id))

    except xmlrpc.client.ProtocolError as err:
        print("A protocol error occurred")
        print("URL: {}".format(err.url))
        print("HTTP/HTTPS headers: {}".format(err.headers))
        print("Error code: {}".format(err.errcode))
        print("Error message: {}".format(err.errmsg))

    except xmlrpc.client.Fault as err:
        print("A fault occurred")
        print("Fault code: {}".format(err.faultCode))
        print("Fault string: {}".format(err.faultString))

    except OSError as err:
        print("File error: {}".format(err))

    except xmlrpc.client.Error as err:
        print("XML-RPC error: {}".format(err))


if __name__ == "__main__":

    parser = OptionParser(
        usage="%prog [options] plugin.zip"
    )

    parser.add_option(
        "-w", "--password",
        dest="password",
        help="Password for plugin site",
        metavar="******"
    )

    parser.add_option(
        "-u", "--username",
        dest="username",
        help="Username of plugin site",
        metavar="user"
    )

    parser.add_option(
        "-p", "--port",
        dest="port",
        help="Server port to connect to",
        metavar="443"
    )

    parser.add_option(
        "-s", "--server",
        dest="server",
        help="Specify server name",
        metavar="plugins.qgis.org"
    )

    options, args = parser.parse_args()

    if len(args) != 1:
        print("Please specify zip file.\n")
        parser.print_help()
        sys.exit(1)

    if not options.server:
        options.server = SERVER

    if not options.port:
        options.port = PORT

    if not options.username:
        username = getpass.getuser()
        res = input("Please enter user name [{}] : ".format(username))
        options.username = res if res else username

    if not options.password:
        options.password = getpass.getpass("Password: ")

    main(options, args)
