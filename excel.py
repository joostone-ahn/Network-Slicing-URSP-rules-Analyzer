from datetime import datetime
import os
import pandas as pd
import win32com.client as win32

def to_excel(df_payload):
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime("%Y%m%d_%H%M%S")
    output_file = f'MANAGE_UE_POLICY_COMMAND_{timestamp}.xlsx'
    df_payload.to_excel(output_file, index=False)

    output_file_path = os.path.abspath(output_file)
    rst_msg = f" Saved at {output_file_path}"

    return rst_msg