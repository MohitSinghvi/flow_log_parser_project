# protocol_utils.py

def protocolNumberToStr(proto_num):
    """
    I am converting a numeric protocol (e.g. '6', '17', '1') to a human-readable string.
    Unknown -> 'proto_<num>'
    """
    mapping = {
        6: "tcp",
        17: "udp",
        1: "icmp",
        2: "igmp"
    }
    return mapping.get(proto_num, f"proto_{proto_num}")
