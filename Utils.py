from icmplib import ICMPv4Socket, ICMPRequest, PID, TimeoutExceeded, \
                    DestinationUnreachable, TimeExceeded, ICMPLibError


def check_connection(address, timeout=2, request_id=PID):
    sock = ICMPv4Socket()
    request = ICMPRequest(destination=address, id=request_id, sequence=1)

    try:
        sock.send(request)
        reply = sock.receive(request, timeout)
        reply.raise_for_status()

    except TimeoutExceeded as err:
        print(err)

    except DestinationUnreachable as err:
        print(err)

    except TimeExceeded as err:
        print(err)

    except ICMPLibError as err:
        print(err)