import pandas as pd
import tabulate

debug_mode = 0
tablefmt_list = ["pipe", "simple", "grid", "fancy_grid", "orgtbl", "tsv"]
tablefmt = tablefmt_list[4]

def usi_to_txt(usi_list):
    header = ['hex', 'desc']
    df_usi = pd.DataFrame(usi_list, columns=header)
    usi_conts = df_usi.to_markdown(tablefmt=tablefmt, numalign='left', index=False)
    return usi_conts

def payload_to_txt(df_payload):

    pol_cmd_txt = df_payload.to_markdown(tablefmt=tablefmt, numalign='left', index=False)

    return pol_cmd_txt

def ursp_to_txt(ursp_sum, rsd_sum, rsd_conts, PTI, PLMN, UPSC):

    ursp_info = []
    ursp_info.append(format(int(PTI), '02X'))
    ursp_info.append(PLMN)
    ursp_info.append(format(int(UPSC), '02X'))

    header1 = ['pti', 'plmn', 'upsc']
    df_ursp_info = pd.DataFrame([ursp_info], columns=header1)
    ursp_info = df_ursp_info.to_markdown(tablefmt=tablefmt, numalign='left', index=False)

    ursp_list = []
    for i in range(len(ursp_sum)):
        for j in range(len(rsd_sum[i])):
            for k in range(len(rsd_conts[i][j])):
                ursp_item = ursp_sum[i] + rsd_sum[i][j] + rsd_conts[i][j][k]
                ursp_list.append(ursp_item)

    header2 = ['ursp_num', 'ursp_pv', 'td_type', 'td_val', 'rsd_num', 'rsd_pv', 'rsd_conts_num', 'rsd_conts_type', 'rsd_conts_val']
    df_ursp = pd.DataFrame(ursp_list, columns=header2)

    # for col in df_ursp.columns:
    #     mask = (df_ursp[col] == df_ursp[col].shift()) & (df_ursp[col] != '')
    #     df_ursp[col] = df_ursp[col].where(~mask, '')

    ursp_conts = df_ursp.to_markdown(tablefmt=tablefmt,numalign='left', index=False)

    return ursp_info, ursp_conts


# def ursp_to_text(ursp_sum, rsd_sum, rsd_conts, PTI, PLMN, UPSC):
#
#     ursp_list = []
#     for i in range(len(ursp_sum)):
#         for j in range(len(rsd_sum[i])):
#             for k in range(len(rsd_conts[i][j])):
#                 ursp_item = ursp_sum[i] + rsd_sum[i][j] + rsd_conts[i][j][k]
#                 ursp_list.append(ursp_item)
#
#     text = "URSP rules" + '\n'
#     text += "PTI 0x" + format(int(PTI), '02X') + ' / '
#     text += "UPSC 0x" + format(int(UPSC), '02X') + ' / '
#     text += "PLMN " + PLMN + '\n'
#
#     header = ["ursp_num", "ursp_pv", "td_type", "td_val", "rsd_num", "rsd_pv", "rsd_conts_num", "rsd_conts_type", "rsd_conts_val"]
#     column_lengths = [max(len(str(name)), max(len(str(item)) for item in column)) for name, column in
#                       zip(header, zip(*ursp_list))]
#
#     separator = ' ' * 3
#     text += "=" * (sum(column_lengths) + len(separator) * (len(column_lengths))) + '\n'
#     text += separator.join("%-*s" % (length, name) for name, length in zip(header, column_lengths)) + '\n'
#     text += "=" * (sum(column_lengths) + len(separator) * (len(column_lengths))) + '\n'
#     ursp_prev, rsd_prev = '', ''
#     for ursp in ursp_list:
#         if ursp[0] != ursp_prev:
#             if ursp[0] != "URSP_0":
#                 text += "-" * (sum(column_lengths) + len(separator) * (len(column_lengths))) + '\n'
#             text += separator.join("%-*s" % (length, str(ursp_comps)) for ursp_comps, length in zip(ursp, column_lengths)) + '\n'
#         else:
#             if ursp[4] != rsd_prev:
#                 text += separator.join(["%-*s" % (length, ' ') if i < 4 else "%-*s" % (length, str(ursp_comps))
#                                       for i, (ursp_comps, length) in enumerate(zip(ursp, column_lengths))]) + '\n'
#             else:
#                 text += separator.join(["%-*s" % (length, ' ') if i < 6 else "%-*s" % (length, str(ursp_comps))
#                                       for i, (ursp_comps, length) in enumerate(zip(ursp, column_lengths))])  + '\n'
#         ursp_prev = ursp[0]
#         rsd_prev = ursp[4]
#     text += "=" * (sum(column_lengths) + len(separator) * (len(column_lengths)))
#
#     print(text)
#     return text

# def hex_format(hex_stream, bytes_per_line=16):
#     hex_list = [hex_stream[i:i+2] for i in range(0, len(hex_stream), 2)]
#     result = []
#     for i in range(0, len(hex_list), bytes_per_line):
#         hex_line = hex_list[i:i + bytes_per_line]
#         hex_str = ' '.join(hex_line)
#         result.append(f"{i:04X}   {hex_str}")
#
#     print('\n'.join(result))
#     return '\n'.join(result)