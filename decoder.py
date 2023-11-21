import pandas as pd
import spec, display

debug_mode = 0

def ursp_decoder(df_dl_nas):
    df_dl_nas = df_dl_nas.copy()
    df_dl_nas['dec'] = [int(x, 16) for x in df_dl_nas['hex']]
    df_dl_nas = df_dl_nas[['dec', 'hex']]
    df_dl_nas['desc'] = ''

    payload_len = int(df_dl_nas.iloc[2:4]['hex'].str.cat(), 16)
    df_payload = df_dl_nas[0:4 + payload_len].reset_index(drop=True)
    df_payload.iloc[0, -1] = 'DL NAS Transport'
    df_payload.iloc[1, -1] = 'Payload container type: UE policy container'
    df_payload.iloc[2, -1] = 'Length of payload container contents[0]'
    df_payload.iloc[3, -1] = 'Length of payload container contents[1]'

    PTI = int(df_payload['hex'][4],16)
    df_payload.iloc[4, -1] = 'Procedure transaction identity(PTI)'

    type_int = int(df_payload['hex'][5], 16) & 0x0F
    if type_int in spec.pol_msg_types:
        pol_msg_type = spec.pol_msg_types[type_int]
    else:
        pol_msg_type = 'Reserved'

    # MANAGE UE POLICY COMMAND
    if type_int == 1:
        df_payload.iloc[5, -1] = 'UE policy delivery service message type: ' + pol_msg_type
    else:
        df_payload.iloc[5, -1] = 'UE policy delivery service message type: ' + pol_msg_type
        print(df_payload)
        return

    upsm_list_len = int(df_payload.iloc[6:8]['hex'].str.cat(), 16)
    df_payload.iloc[6, -1] = 'Length of UE policy section management list contents[0]'
    df_payload.iloc[7, -1] = 'Length of UE policy section management list contents[1]'

    if payload_len != (upsm_list_len+4):
        print('*** [ERROR] Length of payload container contents')
        print("payload_len", payload_len)
        print("upsm_list_len", upsm_list_len)
        print(df_payload)
        return

    df_UPSM_list = df_payload.iloc[8:8 + upsm_list_len].reset_index().rename(columns={'index': 'ind'})
    UPSM_list = []
    cnt = 0
    while cnt < len(df_UPSM_list):
        pos_row = df_UPSM_list['ind'][cnt]
        df_payload.iloc[pos_row, -1] = 'Length of UE policy section management sublist[0]'
        df_payload.iloc[pos_row + 1, -1] = 'Length of UE policy section management sublist[1]'

        upsm_len = int(df_UPSM_list.loc[cnt:cnt + 1, 'hex'].str.cat(), 16)
        cnt += 2
        UPSM_list.append(df_UPSM_list.iloc[cnt:cnt + upsm_len])
        cnt += upsm_len
        if debug_mode: print('upsm_len:', upsm_len)
    for subset in UPSM_list:
        df_UPSM = subset.reset_index(drop=True)
        df_payload.iloc[df_UPSM['ind'][0], -1] = 'MCC digit 2, MCC digit 1'
        df_payload.iloc[df_UPSM['ind'][1], -1] = 'MNC digit 3, MCC digit 3'
        df_payload.iloc[df_UPSM['ind'][2], -1] = 'MNC digit 2, MNC digit 1'

        PLMN = df_UPSM['hex'][0][1]
        PLMN += df_UPSM['hex'][0][0]
        PLMN += df_UPSM['hex'][1][1]
        PLMN += df_UPSM['hex'][2][1]
        PLMN += df_UPSM['hex'][2][0]
        PLMN += df_UPSM['hex'][1][0]

        df_INS_list = df_UPSM.iloc[3:].reset_index(drop=True)
        INS_list = []
        cnt = 0
        while cnt < len(df_INS_list):
            pos_row = df_INS_list['ind'][cnt]
            df_payload.iloc[pos_row, -1] = 'Instruction contents length[0]'
            df_payload.iloc[pos_row + 1, -1] = 'Instruction contents length[1]'

            ins_len = int(df_INS_list.loc[cnt:cnt + 1, 'hex'].str.cat(), 16)
            cnt += 2
            INS_list.append(df_INS_list.iloc[cnt:cnt + ins_len])
            cnt += ins_len
            if debug_mode: print('ins_len:', ins_len)
        if debug_mode: print('ins_num:', len(INS_list))

        for subset in INS_list:
            df_INS = subset.reset_index(drop=True)
            df_payload.iloc[df_INS['ind'][0], -1] = 'UPSC[0]'
            df_payload.iloc[df_INS['ind'][1], -1] = 'UPSC[1]'

            UPSC = int(df_INS['hex'][0:2].str.cat(),16)

            df_POL_list = df_INS.iloc[2:].reset_index(drop=True)
            POL_list = []
            cnt = 0
            while cnt < len(df_POL_list):
                pos_row = df_POL_list['ind'][cnt]
                df_payload.iloc[pos_row, -1] = 'UE policy part contents length[0]'
                df_payload.iloc[pos_row + 1, -1] = 'UE policy part contents length[1]'

                pol_len = int(df_POL_list.loc[cnt:cnt + 1, 'hex'].str.cat(), 16)
                cnt += 2
                POL_list.append(df_POL_list.iloc[cnt:cnt + pol_len])
                cnt += pol_len
                if debug_mode: print('pol_len:', pol_len)
            if debug_mode: print('pol_num', len(POL_list))

            for subset in POL_list:
                df_POL = subset.reset_index(drop=True)

                type_int = int(df_POL['hex'][0], 16) & 0x07
                if type_int in spec.pol_part_types:
                    pol_part_type = spec.pol_part_types[type_int]
                else:
                    pol_part_type = 'Reserved'
                df_payload.iloc[df_POL['ind'][0], -1] = 'UE policy part type: ' + pol_part_type

                # URSP_Analyzer rule
                if type_int == 1:
                    df_URSP_list = df_POL.iloc[1:].reset_index(drop=True)
                    URSP_list = []
                    cnt = 0
                    while cnt < len(df_URSP_list):
                        pos_row = df_URSP_list['ind'][cnt]
                        df_payload.iloc[pos_row, -1] = 'Length of URSP_Analyzer rule[0]'
                        df_payload.iloc[pos_row + 1, -1] = 'Length of URSP_Analyzer rule[1]'

                        ursp_len = int(df_URSP_list.loc[cnt:cnt + 1, 'hex'].str.cat(), 16)
                        cnt += 2
                        URSP_list.append(df_URSP_list.iloc[cnt:cnt + ursp_len])
                        cnt += ursp_len
                        if debug_mode: print('ursp_len:', ursp_len)

                    ursp_sum = []
                    rsd_sum = []
                    rsd_conts = []
                    ursp_num_cnt = 0
                    for subset in URSP_list:
                        ursp_sub1 = []
                        ursp_num = "URSP_" + str(ursp_num_cnt)
                        ursp_sub1.append(ursp_num)
                        ursp_num_cnt += 1

                        df_URSP = subset.reset_index(drop=True)

                        # PV
                        df_payload.iloc[df_URSP['ind'][0], -1] = 'Precedence value of URSP_Analyzer rule'
                        ursp_pv = int(df_URSP['hex'][0], 16)
                        ursp_sub1.append(ursp_pv)

                        # TD
                        df_payload.iloc[df_URSP['ind'][1], -1] = 'Length of traffic descriptor[0]'
                        df_payload.iloc[df_URSP['ind'][2], -1] = 'Length of traffic descriptor[1]'
                        td_len = int(df_URSP.loc[1:2, 'hex'].str.cat(), 16)

                        df_TD = df_URSP[3:3 + td_len].reset_index(drop=True)

                        type_int = int(df_TD['hex'][0], 16)
                        if type_int in spec.td_types:
                            td_type = spec.td_types[type_int]
                            df_payload.iloc[df_TD['ind'][0], -1] = 'Traffic descriptor type: ' + td_type
                        else:
                            td_type = 'Unknown'
                            df_payload.iloc[df_TD['ind'][0], -1] = ' *** [ERROR] Traffic descriptor type id NOT DEFINED'
                        ursp_sub1.append(td_type)

                        td_val = '-'
                        if td_type not in spec.td_zero:
                            if td_type == 'DNN':
                                dnn_len = int(df_TD['hex'][1], 16)
                                df_payload.iloc[df_TD['ind'][1], -1] = td_type + ' length field'

                                apn_len = int(df_TD['hex'][2], 16)
                                df_payload.iloc[df_TD['ind'][2], -1] = 'APN length as defined in 3GPP TS 23.003'

                                if apn_len + 1 != dnn_len:
                                    print(" *** [ERROR] DNN/APN length")
                                    df_payload.iloc[df_TD['ind'][1], -1] += '*ERROR*'
                                    df_payload.iloc[df_TD['ind'][2], -1] += '*ERROR*'
                                    break

                                apn_val_hex = ''
                                apn_cnt = 0
                                for byte in df_TD['hex'][3:3 + apn_len]:
                                    apn_val_hex += byte
                                    df_payload.iloc[df_TD['ind'][3 + apn_cnt], -1] = 'APN value field[%d]' % apn_cnt
                                    apn_cnt += 1
                                td_val = bytes.fromhex(apn_val_hex)
                                td_val = td_val.decode('ascii')

                            elif td_type == "Connection capabilities":
                                td_conn_capa = []
                                capa_cnt = 0
                                for octet in df_TD['hex'][1:]:
                                    td_conn_capa.append(spec.td_conn_capa[int(octet, 16)])
                                    df_payload.iloc[df_TD['ind'][1+capa_cnt], -1] = 'connection capability identifier: %s'%td_conn_capa[-1]
                                    capa_cnt += 1
                                td_val = ', '.join(td_conn_capa)

                            elif td_type in ['OS App Id', 'OS Id + OS App Id']:
                                os_id = df_TD['hex'][1:1 + 16].str.cat()
                                for os_id_cnt in range(16):
                                    df_payload.iloc[df_TD['ind'][1 + os_id_cnt], -1] = 'OS Id value field[%d]' % os_id_cnt
                                if os_id == '97A498E3FC925C9489860333D06E4E47':
                                    td_val = 'Android'
                                else:
                                    td_val = 'Unknown OS'

                                app_id_len = int(df_TD['hex'][17], 16)
                                df_payload.iloc[df_TD['ind'][17], -1] = 'OS App Id length field'

                                app_id = df_TD['hex'][18:18+app_id_len].str.cat()
                                for app_id_cnt in range(app_id_len):
                                    df_payload.iloc[df_TD['ind'][18 + app_id_cnt], -1] = 'OS App Id value field[%d]' % app_id_cnt
                                app_id_byte = bytes.fromhex(app_id)
                                app_id_val = app_id_byte.decode('ascii')
                                td_val += '/' + app_id_val

                            else:
                                etc_val_hex = '0x'
                                etc_cnt = 0
                                for byte in df_TD['hex'][1:]:
                                    etc_val_hex += byte
                                    df_payload.iloc[df_TD['ind'][1 + etc_cnt], -1] = td_type + ' value field[%d]' % etc_cnt
                                    etc_cnt += 1

                        ursp_sub1.append(td_val)

                        # RSD
                        df_remain = df_URSP[3 + td_len:].reset_index(drop=True)
                        df_payload.iloc[df_remain['ind'][0], -1] = 'Length of route selection descriptor list[0]'
                        df_payload.iloc[df_remain['ind'][1], -1] = 'Length of route selection descriptor list[1]'
                        rsd_list_len = int(df_remain.loc[0:1, 'hex'].str.cat(), 16)

                        df_RSD_list = df_remain.iloc[2:2 + rsd_list_len].reset_index(drop=True)

                        RSD_list = []
                        cnt = 0
                        while cnt < len(df_RSD_list):
                            pos_row = df_RSD_list['ind'][cnt]
                            df_payload.iloc[pos_row, -1] = 'Length of route selection descriptor[0]'
                            df_payload.iloc[pos_row + 1, -1] = 'Length of route selection descriptor[1]'

                            rsd_len = int(df_RSD_list.loc[cnt:cnt + 1, 'hex'].str.cat(), 16)
                            cnt += 2

                            RSD_list.append(df_RSD_list.iloc[cnt:cnt + rsd_len])
                            cnt += rsd_len
                            if debug_mode: print('rsd_len:', rsd_len)

                        rsd_sub1 = []
                        rsd_conts_sub1 = []
                        rsd_num_cnt = 0
                        for subset in RSD_list:
                            rsd_sub2 = []

                            rsd_num = "RSD_" + str(ursp_num_cnt-1) + '_' + str(rsd_num_cnt)
                            rsd_sub2.append(rsd_num)
                            rsd_num_cnt += 1

                            df_RSD = subset.reset_index(drop=True)

                            df_payload.iloc[df_RSD['ind'][0], -1] = 'Precedence value of route selection descriptor'
                            rsd_pv = int(df_RSD['hex'][0], 16)
                            rsd_sub2.append(rsd_pv)

                            rsd_conts_len = int(df_RSD.loc[1:2, 'hex'].str.cat(), 16)
                            df_payload.iloc[df_RSD['ind'][1], -1] = 'Length of route selection descriptor contents[0]'
                            df_payload.iloc[df_RSD['ind'][2], -1] = 'Length of route selection descriptor contents[1]'

                            df_RSD_conts_list = df_RSD.iloc[3:3 + rsd_conts_len].reset_index(drop=True)

                            exceed_len = len(df_RSD.iloc[3+rsd_conts_len:])
                            if exceed_len > 0:
                                for exceed_cnt in range(exceed_len):
                                    error_loc = df_RSD['ind'][3+rsd_conts_len+exceed_cnt]
                                    print(" *** [ERROR] pay_load_container[" + str(error_loc) + "]")
                                    df_payload.iloc[error_loc, -1] = '[ERROR] RSD contents length EXCEEDED'

                            rsd_conts_sub2 =[]
                            rsd_conts_num = 0
                            cnt = 0
                            while cnt < len(df_RSD_conts_list):
                                type_int = int(df_RSD_conts_list['hex'][cnt], 16)
                                if type_int in spec.rsd_types:
                                    rsd_conts_type = spec.rsd_types[type_int]
                                    df_payload.iloc[df_RSD_conts_list['ind'][cnt], -1] = 'route selection descriptor component type identifier: ' + rsd_conts_type
                                    cnt += 1
                                    if debug_mode: print(rsd_conts_type)
                                    rsd_conts_sub3 = [rsd_num + '_' +str(rsd_conts_num)]
                                    rsd_conts_sub3.append(rsd_conts_type)
                                    rsd_conts_num += 1
                                else:
                                    error_loc = df_RSD_conts_list['ind'][cnt]
                                    print(" *** [ERROR] pay_load_container["+str(error_loc)+"]")
                                    df_payload.iloc[error_loc, -1] = "[ERROR] RSD contents type id NOT MATCHED"
                                    break

                                if rsd_conts_type == 'S-NSSAI':
                                    rsd_conts_len = int(df_RSD_conts_list['hex'][cnt], 16)
                                    if rsd_conts_len != 4:
                                        print("[ERROR] S-NSSAI length error")
                                        break
                                    df_payload.iloc[df_RSD_conts_list['ind'][cnt], -1] = rsd_conts_type + ' length field'
                                    cnt += 1

                                    SST = int(df_RSD_conts_list['hex'][cnt], 16)
                                    df_payload.iloc[df_RSD_conts_list['ind'][cnt], -1] = 'SST'
                                    cnt += 1

                                    SD = int(df_RSD_conts_list.loc[cnt:cnt + 2, 'hex'].str.cat(), 16)
                                    df_payload.iloc[df_RSD_conts_list['ind'][cnt], -1] = 'SD[0]'
                                    df_payload.iloc[df_RSD_conts_list['ind'][cnt + 1], -1] = 'SD[1]'
                                    df_payload.iloc[df_RSD_conts_list['ind'][cnt + 2], -1] = 'SD[2]'
                                    cnt += 3

                                    rsd_conts_val = 'SST ' + str(SST) + ' + SD ' + str(SD)

                                elif rsd_conts_type == 'DNN':
                                    rsd_conts_len = int(df_RSD_conts_list['hex'][cnt], 16)
                                    df_payload.iloc[df_RSD_conts_list['ind'][cnt], -1] = 'DNN length field'
                                    cnt += 1

                                    apn_len = int(df_RSD_conts_list['hex'][cnt], 16)
                                    if apn_len + 1 != rsd_conts_len:
                                        print("[ERROR] DNN/APN length error")
                                        break
                                    df_payload.iloc[
                                        df_RSD_conts_list['ind'][cnt], -1] = 'APN length as defined in 3GPP TS 23.003'
                                    cnt += 1

                                    apn_val_hex = ''
                                    apn_cnt = 0
                                    for byte in df_RSD_conts_list['hex'][cnt:cnt + apn_len]:
                                        apn_val_hex += byte
                                        df_payload.iloc[df_RSD_conts_list['ind'][cnt], -1] = 'APN value field[%d]' % apn_cnt
                                        cnt += 1
                                        apn_cnt += 1
                                    rsd_conts_val = bytes.fromhex(apn_val_hex)
                                    rsd_conts_val = rsd_conts_val.decode('ascii')

                                # shall not include value field
                                elif rsd_conts_type in spec.rsd_zero:
                                    rsd_conts_val = ''

                                # value field shall be encoded as a one octet
                                elif rsd_conts_type in spec.rsd_one:
                                    rsd_conts_val = int(df_RSD_conts_list['hex'][cnt], 16)
                                    df_payload.iloc[df_RSD_conts_list['ind'][cnt], -1] = rsd_conts_type + ' value field'
                                    cnt += 1

                                # "Location criteria" or "Time window"
                                else:
                                    print(" *** [TBD] Location criteria or Time window type")
                                    break

                                rsd_conts_sub3.append(rsd_conts_val)
                                rsd_conts_sub2.append(rsd_conts_sub3)
                            rsd_sub1.append(rsd_sub2)
                            rsd_conts_sub1.append(rsd_conts_sub2)
                        ursp_sum.append(ursp_sub1)
                        rsd_sum.append(rsd_sub1)
                        rsd_conts.append(rsd_conts_sub1)

    if debug_mode:
        for i in range(len(ursp_sum)):
            print('URSP_'+str(i))
            print(ursp_sum[i])
            for j in range(len(rsd_sum[i])):
                print('RSD_'+str(j))
                print(rsd_sum[i][j])
                for k in range(len(rsd_conts[i][j])):
                    print('RSD_conts_'+str(k))
                    print(rsd_conts[i][j][k])

    df_payload = df_payload.reset_index().rename(columns={'index': 'ind'})

    return df_payload, ursp_sum, rsd_sum, rsd_conts, PTI, PLMN, UPSC

def usi_decoder(payload):
    usi_list = []
    usi_list.append([payload[0], 'Payload container type: UE policy container'])
    usi_list.append([payload[1], 'Payload container IEI'])
    usi_list.append([payload[2], 'Length of payload container contents[0]'])
    usi_list.append([payload[3], 'Length of payload container contents[1]'])
    payload_len = int(payload[2] + payload[3], 16)
    payload = payload[4:4+payload_len]

    usi_list.append([payload[0], 'Procedure transaction identity(PTI)'])
    usi_list.append([payload[1], 'UE policy delivery service message type: UE STATE INDICATION'])
    usi_list.append([payload[2], 'Length of UPSI list contents [0]'])
    usi_list.append([payload[3], 'Length of UPSI list contents [1]'])
    upsi_list_len = int(payload[2] + payload[3], 16)
    upsi_list_item = payload[4:4 + upsi_list_len]
    cnt = 0
    while cnt < len(upsi_list_item):
        usi_list.append([upsi_list_item[cnt], 'Length of UPSI sublist [0]'])
        usi_list.append([upsi_list_item[cnt+1], 'Length of UPSI sublist [1]'])
        upsi_sub_len = int(upsi_list_item[cnt] + upsi_list_item[cnt+1], 16)
        cnt += 2
        upsi_sub_item = upsi_list_item[cnt:cnt+upsi_sub_len]
        usi_list.append([upsi_sub_item[0], 'MCC digit 2 + MCC digit 1'])
        usi_list.append([upsi_sub_item[1], 'MNC digit 3 + MCC digit 3'])
        usi_list.append([upsi_sub_item[2], 'MNC digit 2 + MNC digit 1'])
        cnt += 3
        upsc_item = upsi_sub_item[3:]
        for i in range(len(upsc_item)):
            usi_list.append([upsc_item[i], 'UPSC ' + str(i // 2) + ' [' + str(i % 2) + ']'])
        cnt += len(upsc_item)
    payload_etc = payload[4 + upsi_list_len:]
    usi_list.append([payload_etc[0], 'UE policy classmark'])
    if payload_etc[1:]:
        for i in range(len(payload_etc[1:])):
            usi_list.append([payload_etc[1:][i], 'OS Id [' + str(i) + ']'])

    usi_rst = '=' * 213 + '\n'
    usi_rst += 'UE STATE INDICATION' + '\n'
    usi_rst += '=' * 213 + '\n'
    usi_conts = display.usi_to_txt(usi_list)
    usi_rst += usi_conts

    return usi_rst