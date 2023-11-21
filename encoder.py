import spec
import pandas as pd

debug_mode = 0

def ursp_encoder(ursp_sum, rsd_sum, rsd_conts, PTI, PLMN, UPSC):
    payload_pvtd_list = []
    payload_rsd_list = []

    if len(PLMN) == 5:
        PLMN += 'F'

    for ursp_cnt in range(len(ursp_sum)):
        ursp_list = ursp_sum[ursp_cnt]
        ursp_pv = int(ursp_list[1])
        td_type = ursp_list[2]
        td_val = ursp_list[3]

        payload_pvtd = []
        if td_type in spec.td_types_rev:
            td_type_hex = format(spec.td_types_rev[td_type], '02X')
            payload_pvtd.append(td_type_hex)
        else:
            print("*Unknown td_type")

        if td_type not in spec.td_zero:
            if td_type == 'DNN':
                td_val_byte = td_val.encode('ascii')

                apn_len = len(td_val_byte)
                dnn_len = apn_len + 1

                payload_pvtd.append(format(dnn_len, '02X'))
                payload_pvtd.append(format(apn_len, '02X'))

                for byte in td_val_byte:
                    payload_pvtd.append(format(byte, '02X'))

            elif td_type == "Connection capabilities":
                td_conn_capa = td_val.split(',')
                for item in td_conn_capa:
                    item = item.replace(' ','')
                    payload_pvtd.append(format(spec.td_conn_capa_rev[item], '02X'))

            elif td_type in ['OS App Id', 'OS Id + OS App Id']:
                os_id, app_id = td_val.split('/')
                app_id = app_id.replace(' ', '')

                os_id_bytes = []
                if os_id == 'Android':
                    os_id_byte = '97A498E3FC925C9489860333D06E4E47'
                    for i in range(0, len(os_id_byte), 2):
                        payload_pvtd.append(os_id_byte[i:i + 2])
                else:
                    print("*iOS TBD")

                app_id_byte = app_id.encode('ascii')
                app_id_len = len(app_id_byte)
                payload_pvtd.append(format(app_id_len, '02X'))
                for byte in app_id_byte:
                    payload_pvtd.append(format(byte, '02X'))
            else:
                print(td_val)

        td_len = len(payload_pvtd)
        td_len_hex = format(td_len, '04X')
        payload_pvtd.insert(0, td_len_hex[2:])
        payload_pvtd.insert(0, td_len_hex[:2])

        payload_pvtd.insert(0, format(int(ursp_pv), '02X'))
        payload_pvtd_list.append(payload_pvtd)


        for rsd_cnt in range(len(rsd_sum[ursp_cnt])):
            rsd_list = rsd_sum[ursp_cnt][rsd_cnt]
            rsd_pv = int(rsd_list[1])

            payload_rsd = []
            for rsd_conts_cnt in range(len(rsd_conts[ursp_cnt][rsd_cnt])):
                rsd_conts_list = rsd_conts[ursp_cnt][rsd_cnt][rsd_conts_cnt]
                rsd_conts_type = rsd_conts_list[1]
                rsd_conts_val = rsd_conts_list[2]

                if rsd_conts_type in spec.rsd_types_rev:
                    rsd_conts_type_hex = format(spec.rsd_types_rev[rsd_conts_type], '02X')
                else:
                    print("*Unknown rsd_conts_type")
                payload_rsd.append(rsd_conts_type_hex)

                if rsd_conts_type == 'S-NSSAI':
                    rsd_conts_len = '04'
                    payload_rsd.append(rsd_conts_len)

                    SST, SD = rsd_conts_val.split(' + ')

                    SST = format(int(SST.split(' ')[1]), '02X')
                    payload_rsd.append(SST)

                    SD = format(int(SD.split(' ')[1]), '06X')
                    for i in range(0, len(SD), 2):
                        payload_rsd.append(SD[i:i + 2])

                elif rsd_conts_type == 'DNN':
                    rsd_conts_val_byte = rsd_conts_val.encode('ascii')

                    apn_len = len(rsd_conts_val_byte)
                    dnn_len = apn_len + 1

                    payload_rsd.append(format(dnn_len, '02X'))
                    payload_rsd.append(format(apn_len, '02X'))

                    for byte in rsd_conts_val_byte:
                        payload_rsd.append(format(byte, '02X'))

                # shall not include value field
                elif rsd_conts_type in spec.rsd_zero:
                    continue

                # value field shall be encoded as a one octet
                elif rsd_conts_type in spec.rsd_one:
                    rsd_conts_val_hex = format(int(rsd_conts_val), '02X')
                    payload_rsd.append(rsd_conts_val_hex)

                # "Location criteria" or "Time window"
                else:
                    print("*Location criteria or Time window type TBD")
                    print()

            # tab * 3 location
            rsd_conts_len = len(payload_rsd)
            rsd_conts_len_hex = format(rsd_conts_len, '04X')
            payload_rsd.insert(0, rsd_conts_len_hex[2:])
            payload_rsd.insert(0, rsd_conts_len_hex[:2])
            payload_rsd.insert(0, format(int(rsd_pv), '02X'))

            rsd_len = len(payload_rsd)
            rsd_len_hex = format(rsd_len, '04X')
            payload_rsd.insert(0, rsd_len_hex[2:])
            payload_rsd.insert(0, rsd_len_hex[:2])

            if rsd_cnt != 0:
                payload_rsd = payload_rsd_list[-1] + payload_rsd
                del payload_rsd_list[-1]
            payload_rsd_list.append(payload_rsd)

    for payload_rsd in payload_rsd_list:
        rsd_list_len = len(payload_rsd)
        rsd_list_len_hex = format(rsd_list_len, '04X')
        payload_rsd.insert(0, rsd_list_len_hex[2:])
        payload_rsd.insert(0, rsd_list_len_hex[:2])

    if debug_mode:
        print("=" * 100)
        print("Route SelectionDescriptor List")
        print("=" * 100)
        for payload_rsd in payload_rsd_list:
            print(payload_rsd)
        print("=" * 100)
        print()

        print("=" * 100)
        print("Traffic Descriptor List")
        print("=" * 100)
        for payload_pvtd in payload_pvtd_list:
            print(payload_pvtd)
        print("=" * 100)
        print()

    if len(payload_pvtd_list) != len(payload_rsd_list):
        print("*** [ERROR] URSP rule malformed")
    else:
        payload_ursp_list = []
        for n in range(len(payload_pvtd_list)):
            payload_ursp = payload_pvtd_list[n]
            payload_ursp += payload_rsd_list[n]
            ursp_len = len(payload_ursp)
            ursp_len_hex = format(ursp_len, '04X')
            payload_ursp.insert(0, ursp_len_hex[2:])
            payload_ursp.insert(0, ursp_len_hex[:2])
            payload_ursp_list.append(payload_ursp)

    if debug_mode:
        print("=" * 100)
        print("URSP Rule List")
        print("=" * 100)
        for payload_ursp in payload_ursp_list:
            print(payload_ursp)
        print("=" * 100)
        print()

    payload_all = []
    for payload_ursp in payload_ursp_list:
        payload_all += payload_ursp

    #####################################
    # EF_URSP
    #####################################
    ef_ursp = format_EF(payload_all, PLMN)

    # UE policy part type
    payload_all.insert(0, '01')

    # UE policy part contents length
    pol_len = len(payload_all)
    pol_len_hex = format(pol_len, '04X')
    payload_all.insert(0, pol_len_hex[2:])
    payload_all.insert(0, pol_len_hex[:2])

    # UPSC
    upsc_byte = format(int(UPSC), '04X')
    payload_all.insert(0, upsc_byte[2:])
    payload_all.insert(0, upsc_byte[:2])

    # Instruction contents length
    ins_len = len(payload_all)
    ins_len_hex = format(ins_len, '04X')
    payload_all.insert(0, ins_len_hex[2:])
    payload_all.insert(0, ins_len_hex[:2])

    # PLMN
    payload_all.insert(0, PLMN[4]+PLMN[3])
    payload_all.insert(0, PLMN[5]+PLMN[2])
    payload_all.insert(0, PLMN[1]+PLMN[0])

    # Length of UE policy section management sublist
    upsm_len = len(payload_all)
    upsm_len_hex = format(upsm_len, '04X')
    payload_all.insert(0, upsm_len_hex[2:])
    payload_all.insert(0, upsm_len_hex[:2])

    # Length of UE policy section management list
    upsm_list_len = len(payload_all)
    upsm_list_len_hex = format(upsm_list_len, '04X')
    payload_all.insert(0, upsm_list_len_hex[2:])
    payload_all.insert(0, upsm_list_len_hex[:2])

    # UE policy delivery service message type: MANAGE UE POLICY COMMAND
    payload_all.insert(0, '01')

    # PTI
    PTI = format(int(PTI), '02X')
    payload_all.insert(0, PTI)

    # Length of payload
    payload_len = len(payload_all)
    payload_len_hex = format(payload_len, '04X')
    payload_all.insert(0, payload_len_hex[2:])
    payload_all.insert(0, payload_len_hex[:2])

    # Payload_type = UE policy container
    payload_all.insert(0,'05')

    # DL NAS trasport
    payload_all.insert(0,'68')
    dl_nas = ''.join(payload_all)

    df_dl_nas = pd.DataFrame({'hex': payload_all})
    df_dl_nas['dec'] = [int(x, 16) for x in df_dl_nas['hex']]
    df_dl_nas = df_dl_nas[['dec', 'hex']]
    df_dl_nas['desc'] = ''

    return df_dl_nas, ef_ursp, dl_nas

def format_EF(payload_all, PLMN):
    ursp_rules = ''.join(payload_all)
    ursp_rules_len = coding_length(ursp_rules)
    ursp_rules = ursp_rules_len + ursp_rules
    ursp_rules = PLMN[1]+PLMN[0]+PLMN[5]+PLMN[2]+PLMN[4]+PLMN[3]+ursp_rules
    ursp_rules_len = coding_length(ursp_rules)
    ursp_rules = '80'+ursp_rules_len + ursp_rules
    return ursp_rules

# The length is coded according to ISO/IEC 8825-1 [35]
# Information technology – ASN.1 encoding rules : Specification of Basic Encoding Rules (BER), Canonical Encoding Rules (CER) and Distinguished Encoding Rules (DER)
def coding_length(data):
    data_length = len(data) // 2  # 데이터의 16진수 표현이므로 2로 나눠줌
    if data_length < 128:
        # Short Form
        length_field = format(data_length, '02X')  # 16진수로 변환하고 2자리로 표현
    else:
        # Long Form
        if data_length <= 255:
            length_field = '81' + format(data_length, '02X')  # 81은 128 이상임을 나타내는 플래그
        elif data_length <= 65535:
            length_field = '82' + format(data_length, '04X')  # 82는 두 바이트로 표현
        else:
            length_field = '83' + format(data_length, '06X')  # 83은 세 바이트로 표현
    return length_field