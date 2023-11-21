pol_msg_types = {
    0x01: "MANAGE UE POLICY COMMAND",
    0x02: "MANAGE UE POLICY COMPLETE",
    0x03: "MANAGE UE POLICY COMMAND REJECT",
    0x04: "UE STATE INDICATION",
    0x05: "UE POLICY PROVISIONING REQUEST",
    0x06: "UE POLICY PROVISIONING REJECT"
}

pol_part_types = {
    0x01: "URSP",
    0x02: "ANDSP",
    0x03: "V2XP",
    0x04: "ProSeP"
}

td_types = {
    0b00000001: "Match-all",
    0b00001000: "OS Id + OS App Id",
    0b00010000: "IPv4 remote address",
    0b00100001: "IPv6 remote address/prefix length",
    0b00110000: "Protocol identifier/next header",
    0b01010000: "Single remote port",
    0b01010001: "Remote port range",
    0b01010010: "IP 3 tuple",
    0b01100000: "Security parameter index",
    0b01110000: "Type of service/traffic class",
    0b10000000: "Flow label",
    0b10000001: "Destination MAC address",
    0b10000011: "802.1Q C-TAG VID",
    0b10000100: "802.1Q S-TAG VID",
    0b10000101: "802.1Q C-TAG PCP/DEI",
    0b10000110: "802.1Q S-TAG PCP/DEI",
    0b10000111: "Ethertype",
    0b10001000: "DNN",
    0b10010000: "Connection capabilities",
    0b10010001: "Destination FQDN",
    0b10010010: "Regular expression",
    0b10100000: "OS App Id",
    0b10100001: "Destination MAC address range"
}

td_conn_capa = {
    0b00000001: "IMS",
    0b00000010: "MMS",
    0b00000100: "SUPL",
    0b00001000: "Internet"
}

td_zero = ["Match-all"]

rsd_types = {
    0b00000001: "SSC mode",
    0b00000010: "S-NSSAI",
    0b00000100: "DNN",
    0b00001000: "PDU session type",
    0b00010000: "Preferred access type",
    0b00010001: "Multi-access preference",
    0b00100000: "Non-seamless non-3GPP offload indication",
    0b01000000: "Location criteria",
    0b10000000: "Time window",
    0b10000001: "5G ProSe layer-3 UE-to-network relay offload indication",
    0b10000010: "PDU session pair ID",
    0b10000011: "RSN"
}
rsd_zero = ["Multi-access preference", "Non-seamless non-3GPP offload indication",
            "5G ProSe layer-3 UE-to-network relay offload indication"]
rsd_one = ['SSC mode', "PDU session type", "Preferred access type", "PDU session pair ID", "RSN"]

td_types_rev = {v: k for k, v in td_types.items()}
td_conn_capa_rev = {v: k for k, v in td_conn_capa.items()}
rsd_types_rev = {v: k for k, v in rsd_types.items()}