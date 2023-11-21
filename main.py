import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget, QPushButton, \
    QComboBox, QLineEdit, QFrame, QWidget, QSpinBox, QTextEdit, QToolTip, QTableWidget
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QCoreApplication
import pandas as pd
import re
import tabulate
import encoder, decoder, spec, display, excel

debug_mode = 0

nar_width = 120
wide_width = 180

font_bold = QFont()
font_bold.setPointSize(9)
font_bold.setBold(True)

font_log = QFont("Consolas", 11)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):

        self.tabs = QTabWidget()

        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "Encoder")
        self.init_tab1()
        self.tab1.setLayout(self.tab1_vbox)

        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, "Decoder")
        self.init_tab2()
        self.tab2.setLayout(self.tab2_vbox)

        self.tab3 = QWidget()
        self.tabs.addTab(self.tab3, "Result")
        self.init_tab3()
        self.tab3.setLayout(self.tab3_vbox)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        self.setWindowTitle('URSP analyzer v1.0')
        self.setGeometry(100, 100, 1700, 900)
        self.show()

        copyright_label = QLabel('Copyright © 2023 JUSEOK AHN<ajs3013@lguplus.co.kr> All rights reserved.')
        copyright_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(copyright_label)

    def init_tab1(self):

        self.tab1_vbox = QVBoxLayout()

        # ursp_cnt
        self.ursp_cnt = QSpinBox()
        self.ursp_cnt.setFixedWidth(nar_width)
        self.ursp_cnt.setMinimum(1)
        self.ursp_cnt.setMaximum(5)
        self.ursp_cnt.setValue(1)
        self.ursp_cnt.setAlignment(Qt.AlignLeft)
        self.ursp_cnt.valueChanged.connect(self.ursp_cnt_changed)

        ursp_num, rsd_num, rsd_conts_num = 0, 0, 0

        self.ursp_sum = []
        ursp_sub1 = self.create_ursp_sum_item(ursp_num)
        self.ursp_sum.append(ursp_sub1)
        if debug_mode: print("ursp_sum", self.ursp_sum)

        self.rsd_sum = []
        rsd_sub1 = []
        rsd_sub2 = self.create_rsd_sum_item(ursp_num, rsd_num)
        rsd_sub1.append(rsd_sub2)
        self.rsd_sum.append(rsd_sub1)
        if debug_mode: print("rsd_sum", self.rsd_sum)

        self.rsd_conts = []
        rsd_conts_sub1 = []
        rsd_conts_sub2 = []
        rsd_conts_sub3 = self.create_rsd_conts_item(ursp_num, rsd_num, rsd_conts_num)
        rsd_conts_sub2.append(rsd_conts_sub3)
        rsd_conts_sub1.append(rsd_conts_sub2)
        self.rsd_conts.append(rsd_conts_sub1)
        if debug_mode:
            print("rsd_conts", self.rsd_conts)
            print()

        info_list = ['pti', 'plmn', 'upsc']
        info_header_hbox =QHBoxLayout()
        for i in range(len(info_list)):
            info_header = QLabel(f'info{i}')
            info_header.setFixedWidth(nar_width)
            info_header.setText(info_list[i])
            info_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            info_header.setFont(font_bold)
            info_header_hbox.addWidget(info_header)
        info_header_hbox.addStretch()
        self.tab1_vbox.addLayout(info_header_hbox)

        info_line = QFrame()
        info_line.setFrameShape(QFrame.HLine)
        info_line.setFrameShadow(QFrame.Sunken)
        info_line.setFixedWidth(nar_width*3+12)
        self.tab1_vbox.addWidget(info_line)

        info_hbox = QHBoxLayout()
        for i in range(len(info_list)):
            info = QLineEdit()
            info.setFixedWidth(nar_width)
            info.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            setattr(self, f'{info_list[i]}', info)
            if info_list[i] == 'pti':
                info.setText('151')
            elif info_list[i] == 'plmn':
                info.setText('45006F')
            elif info_list[i] == 'upsc':
                info.setText('2')
            info_hbox.addWidget(info)
        info_hbox.addStretch()
        self.tab1_vbox.addLayout(info_hbox)
        self.tab1_vbox.addWidget(QLabel())

        self.ursp_grid = QGridLayout()
        row, col = 0, 0
        header_list = ['ursp_cnt', 'ursp_num', 'ursp_pv', 'td_type', 'td_val', 'rsd_cnt', 'rsd_num', 'rsd_pv',
                       'rsd_conts_cnt', 'rsd_conts_num', 'rsd_conts_type', 'rsd_conts_val']
        for i in range(len(header_list)):
            header = QLabel(f'header{i}')
            if i in [3,4,10,11]:
                header.setFixedWidth(wide_width)
            else:
                header.setFixedWidth(nar_width)
            header.setText(header_list[i])
            header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header.setFont(font_bold)
            self.ursp_grid.addWidget(header, row, col)
            col += 1
        row += 1

        header_line = QFrame()
        header_line.setFrameShape(QFrame.HLine)
        header_line.setFrameShadow(QFrame.Sunken)
        self.ursp_grid.addWidget(header_line, row, 0, 1, col)
        row += 1

        self.create_layout()
        self.tab1_vbox.addLayout(self.ursp_grid)
        self.tab1_vbox.addStretch()

        EN_btn_hbox = QHBoxLayout()
        EN_btn = QPushButton()
        EN_btn.setText("Encoding")
        EN_btn.setFixedWidth(nar_width)
        EN_btn.clicked.connect(self.EN_btn_clicked)
        EN_btn_hbox.addWidget(EN_btn)
        self.EN_label = QLabel()
        EN_btn_hbox.addWidget(self.EN_label)
        EN_btn_hbox.addStretch()
        self.tab1_vbox.addLayout(EN_btn_hbox)

        return self.tab1_vbox

    def init_tab2(self):

        self.tab2_vbox = QVBoxLayout()
        self.log_text = QTextEdit()
        style_sheet = "background-color: black; color: white;"
        self.log_text.setStyleSheet(style_sheet)
        self.log_text.setFont(font_log)
        self.tab2_vbox.addWidget(self.log_text)
        DE_btn_hbox = QHBoxLayout()
        DE_btn = QPushButton()
        DE_btn.setText("Decoding")
        DE_btn.setFixedWidth(nar_width)
        DE_btn.clicked.connect(self.DE_btn_clicked)
        DE_btn_hbox.addWidget(DE_btn)
        self.DE_label = QLabel()
        self.DE_label.setFont(font_log)
        DE_btn_hbox.addWidget(self.DE_label)
        DE_btn_hbox.addStretch()
        self.tab2_vbox.addLayout(DE_btn_hbox)

        self.log_text.setText("""Please paste hex values of NAS message containing 'UE policy container'.

Sample
    0000   98 7a 10 a4 6f 51 00 15 17 ab b1 87 08 00 45 02
    0010   00 bc 00 00 40 00 3d 84 7a 4e c0 a8 14 18 c0 a8
    0020   2d 05 96 0c 96 0c 03 79 20 0c ef de 05 2c 00 03
    0030   00 9c c6 14 7c 52 00 00 00 ad 00 00 00 3c 00 04
    0040   40 80 87 00 00 04 00 0a 00 06 80 c8 00 00 00 20
    0050   00 55 00 03 40 70 21 00 26 00 61 60 7e 02 c4 e5
    0060   ff de 04 7e 00 68 05 00 53 01 01 00 4f 00 4d 02
    0070   f8 23 00 48 00 03 00 44 01 00 1f 01 00 0b 88 09
    0080   08 62 75 73 69 6e 65 73 73 00 0f 00 0d ff 00 0a
    0090   02 04 01 e2 e1 11 08 01 10 01 00 20 02 00 01 01
    00a0   00 1a 00 18 ff 00 15 02 04 01 de f2 22 04 09 08
    00b0   69 6e 74 65 72 6e 65 74 08 01 10 01 00 6e 40 0a
    00c0   0c 3b 9a ca 00 30 3b 9a ca 00
            """)

    def init_tab3(self):

        self.tab3_vbox = QVBoxLayout()
        self.rst_text = QTextEdit()
        style_sheet = "background-color: black; color: white;"
        self.rst_text.setStyleSheet(style_sheet)
        self.rst_text.setFont(font_log)
        self.tab3_vbox.addWidget(self.rst_text)

        save_btn_hbox = QHBoxLayout()
        self.save_btn = QPushButton()
        self.save_btn.setText("Save")
        self.save_btn.setFixedWidth(nar_width)
        self.save_btn.clicked.connect(self.save_btn_clicked)
        save_btn_hbox.addWidget(self.save_btn)
        self.save_label = QLabel()
        save_btn_hbox.addWidget(self.save_label)
        save_btn_hbox.addStretch()
        self.tab3_vbox.addLayout(save_btn_hbox)

    def create_ursp_sum_item(self, ursp_num):
        ursp_sub1 = []

        # ursp_num
        line = QLineEdit()
        line.setText(f'URSP_{ursp_num}')
        line.setEnabled(False)
        line.setFixedWidth(nar_width)
        line.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        setattr(self, f'ursp_num_{ursp_num}', line)
        ursp_sub1.append(line)

        # ursp_pv
        line = QLineEdit()
        line.setFixedWidth(nar_width)
        line.setAlignment(Qt.AlignLeft)
        setattr(self, f'ursp_pv_{ursp_num}', line)
        ursp_sub1.append(line)

        # td_type
        comb = QComboBox()
        comb.setFixedWidth(wide_width)

        # Spec Partially support (spec.TD_types)
        td_types = ['Match-all', 'OS Id + OS App Id', 'DNN', 'Connection capabilities']
        for td_type in td_types:
            comb.addItem(td_type)
        comb.currentIndexChanged.connect(lambda: self.td_type_changed(ursp_num))
        setattr(self, f'td_type_{ursp_num}', comb)
        ursp_sub1.append(comb)

        # td_val
        line = QLineEdit()
        line.setFixedWidth(wide_width)
        line.setAlignment(Qt.AlignLeft)
        line.setText('-')
        line.setEnabled(False)
        setattr(self, f'td_val_{ursp_num}', line)
        ursp_sub1.append(line)

        # rsd_cnt
        spin = QSpinBox()
        spin.setFixedWidth(nar_width)
        spin.setMinimum(1)
        spin.setMaximum(5)
        spin.setValue(1)
        spin.setAlignment(Qt.AlignLeft)
        spin.valueChanged.connect(self.rsd_cnt_changed)
        # spin.setEnabled(False)
        setattr(self, f'rsd_cnt_{ursp_num}', spin)
        ursp_sub1.append(spin)

        return ursp_sub1

    def create_rsd_sum_item(self, ursp_num, rsd_num):
        rsd_sub2 = []

        # rsd_num
        line = QLineEdit()
        line.setText(f'RSD_{ursp_num}_{rsd_num}')
        line.setFixedWidth(nar_width)
        line.setEnabled(False)
        line.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        setattr(self, f'rsd_num_{ursp_num}_{rsd_num}', line)
        rsd_sub2.append(line)

        # rsd_pv
        line = QLineEdit()
        line.setFixedWidth(nar_width)
        line.setAlignment(Qt.AlignLeft)
        setattr(self, f'rsd_pv_{ursp_num}_{rsd_num}', line)
        rsd_sub2.append(line)

        # rsd_conts_cnt
        spin = QSpinBox()
        spin.setFixedWidth(nar_width)
        spin.setMinimum(1)
        spin.setMaximum(5)
        spin.setValue(1)
        spin.setAlignment(Qt.AlignLeft)
        spin.valueChanged.connect(self.rsd_conts_cnt_changed)
        setattr(self, f'rsd_conts_cnt_{ursp_num}_{rsd_num}', spin)
        rsd_sub2.append(spin)

        return rsd_sub2

    def create_rsd_conts_item(self, ursp_num, rsd_num, rsd_conts_num):
        rsd_conts_sub3 = []

        # rsd_conts_num
        line = QLineEdit()
        line.setText(f'RSD_{ursp_num}_{rsd_num}_{rsd_conts_num}')
        line.setFixedWidth(nar_width)
        line.setEnabled(False)
        line.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        setattr(self, f'rsd_conts_num_{ursp_num}_{rsd_num}_{rsd_conts_num}', line)
        rsd_conts_sub3.append(line)

        # rsd_conts_type
        comb = QComboBox()
        comb.setFixedWidth(wide_width)
        for rsd_type in spec.rsd_types.values():
            if rsd_type not in ['Location criteria','Time window']: # spec full support TBD
                comb.addItem(rsd_type)
        comb.currentIndexChanged.connect(lambda: self.rsd_type_changed(ursp_num, rsd_num, rsd_conts_num))
        setattr(self, f'rsd_conts_type_{ursp_num}_{rsd_num}_{rsd_conts_num}', comb)
        rsd_conts_sub3.append(comb)

        # rsd_pv
        line = QLineEdit()
        line.setFixedWidth(wide_width)
        line.setAlignment(Qt.AlignLeft)
        setattr(self, f'rsd_conts_val_{ursp_num}_{rsd_num}_{rsd_conts_num}', line)
        rsd_conts_sub3.append(line)

        return rsd_conts_sub3

    def ursp_cnt_changed(self, ursp_cnt):
        ursp_num = ursp_cnt - 1
        rsd_num, rsd_conts_num = 0, 0
        if ursp_cnt > len(self.ursp_sum):
            ursp_sub1 = self.create_ursp_sum_item(ursp_num)
            self.ursp_sum.append(ursp_sub1)
            rsd_sub1 =[]
            rsd_sub2 = self.create_rsd_sum_item(ursp_num, rsd_num)
            rsd_sub1.append(rsd_sub2)
            self.rsd_sum.append(rsd_sub1)
            rsd_conts_sub1 = []
            rsd_conts_sub2 = []
            rsd_conts_sub3 = self.create_rsd_conts_item(ursp_num, rsd_num, rsd_conts_num)
            rsd_conts_sub2.append(rsd_conts_sub3)
            rsd_conts_sub1.append(rsd_conts_sub2)
            self.rsd_conts.append(rsd_conts_sub1)
        else:
            if debug_mode: print("ursp_cnt decreased")
            del self.ursp_sum[-1]
            del self.rsd_sum[-1]
            del self.rsd_conts[-1]
        if debug_mode:
            print("ursp_sum", self.ursp_sum)
            print("rsd_sum", self.rsd_sum)
            print("rsd_conts", self.rsd_conts)
            print()
        self.create_layout()

    def rsd_cnt_changed(self, rsd_cnt):
        rsd_cnt_sender = self.sender()
        rsd_num = rsd_cnt - 1
        rsd_conts_num = 0

        for ursp_num in range(len(self.ursp_sum)):

            if rsd_cnt_sender in self.ursp_sum[ursp_num]:
                if rsd_cnt > len(self.rsd_sum[ursp_num]):
                    if debug_mode:
                        print("rsd_cnt_sender", rsd_cnt_sender)
                        print("ursp_num", ursp_num, "changed")
                    rsd_sub2 = self.create_rsd_sum_item(ursp_num, rsd_num)
                    self.rsd_sum[ursp_num].append(rsd_sub2)
                    rsd_conts_sub3 = self.create_rsd_conts_item(ursp_num, rsd_num, rsd_conts_num)
                    rsd_conts_sub2 = [rsd_conts_sub3]
                    self.rsd_conts[ursp_num].append(rsd_conts_sub2)
                else:
                    if debug_mode: print("rsd_cnt decreased")
                    del self.rsd_sum[ursp_num][-1]
                    del self.rsd_conts[ursp_num][-1]
        if debug_mode:
            print("ursp_sum", self.ursp_sum)
            print("rsd_sum", self.rsd_sum)
            print("rsd_conts", self.rsd_conts)
            print()
        self.create_layout()

    def rsd_conts_cnt_changed(self, rsd_conts_cnt):
        rsd_conts_cnt_sender = self.sender()
        rsd_conts_num = rsd_conts_cnt - 1
        for ursp_num in range(len(self.ursp_sum)):
            for rsd_num in range(len(self.rsd_sum[ursp_num])):
                if rsd_conts_cnt_sender in self.rsd_sum[ursp_num][rsd_num]:
                    if rsd_conts_cnt > len(self.rsd_conts[ursp_num][rsd_num]):
                        if debug_mode:
                            print("rsd_conts_cnt_sender", rsd_conts_cnt_sender)
                            print("ursp_num", ursp_num, "rsd_num", rsd_num, "changed")
                        rsd_conts_sub3 = self.create_rsd_conts_item(ursp_num, rsd_num, rsd_conts_num)
                        self.rsd_conts[ursp_num][rsd_num].append(rsd_conts_sub3)
                    else:
                        if debug_mode: print("rsd_conts_cnt decreased")
                        del self.rsd_conts[ursp_num][rsd_num][-1]
        if debug_mode:
            print("ursp_sum", self.ursp_sum)
            print("rsd_sum", self.rsd_sum)
            print("rsd_conts", self.rsd_conts)
            print()
        self.create_layout()

    def td_type_changed(self, ursp_num):
        if self.ursp_sum[ursp_num][2].currentText() != 'Match-all':
            self.ursp_sum[ursp_num][3].setEnabled(True)
            self.ursp_sum[ursp_num][3].clear()
            if self.ursp_sum[ursp_num][2].currentText() == 'OS Id + OS App Id':
                self.ursp_sum[ursp_num][3].setText('Android/OS_APP_Id')
            elif self.ursp_sum[ursp_num][2].currentText() == 'Connection capabilities':
                self.ursp_sum[ursp_num][3].setText('IMS, MMS, SUPL, Internet')
        else:
            self.ursp_sum[ursp_num][3].setEnabled(False)
            self.ursp_sum[ursp_num][3].setText('-')

    def rsd_type_changed(self, ursp_num, rsd_num, rsd_conts_num):
        if self.rsd_conts[ursp_num][rsd_num][rsd_conts_num][1].currentText() in spec.rsd_zero:
            self.rsd_conts[ursp_num][rsd_num][rsd_conts_num][2].setText('-')
            self.rsd_conts[ursp_num][rsd_num][rsd_conts_num][2].setEnabled(False)
        else:
            self.rsd_conts[ursp_num][rsd_num][rsd_conts_num][2].clear()
            self.rsd_conts[ursp_num][rsd_num][rsd_conts_num][2].setEnabled(True)
            if self.rsd_conts[ursp_num][rsd_num][rsd_conts_num][1].currentText() == 'S-NSSAI':
                self.rsd_conts[ursp_num][rsd_num][rsd_conts_num][2].setText('SST 1 + SD 1')

    def create_layout(self):
        row_under_header = 3
        for row in range(row_under_header, self.ursp_grid.rowCount()):
            for col in range(self.ursp_grid.columnCount()):
                item = self.ursp_grid.itemAtPosition(row, col)
                if item is not None:
                    self.ursp_grid.removeItem(item)
                    widget = item.widget()
                    if widget is not None:
                        widget.setParent(None)

        row, col = row_under_header, 0
        for ursp_num in range(len(self.ursp_sum)):
            for rsd_num in range(len(self.rsd_sum[ursp_num])):
                for rsd_conts_num in range(len(self.rsd_conts[ursp_num][rsd_num])):
                    if debug_mode:
                        print("ursp_num", ursp_num, "rsd_num", rsd_num, "rsd_conts_num", rsd_conts_num)
                        print("row", row, "col", col)

                    if ursp_num == 0 and rsd_num == 0 and rsd_conts_num == 0:
                        self.ursp_grid.addWidget(self.ursp_cnt, row, col)
                        col += 1
                    else:
                        self.ursp_grid.addWidget(QLabel(), row, col)
                        col += 1

                    for ursp_item in self.ursp_sum[ursp_num]:
                        if rsd_num == 0 and rsd_conts_num == 0:
                            self.ursp_grid.addWidget(ursp_item, row, col)
                            col += 1
                            # if isinstance(ursp_item, QLineEdit):
                            #     print(ursp_item.text())
                        else:
                            self.ursp_grid.addWidget(QLabel(), row, col)
                            col += 1
                    for rsd_item in self.rsd_sum[ursp_num][rsd_num]:
                        if rsd_conts_num == 0:
                            self.ursp_grid.addWidget(rsd_item, row, col)
                            col += 1
                        else:
                            self.ursp_grid.addWidget(QLabel(), row, col)
                            col += 1
                    for rsd_conts_item in self.rsd_conts[ursp_num][rsd_num][rsd_conts_num]:
                        self.ursp_grid.addWidget(rsd_conts_item, row, col)
                        col += 1
                        # if isinstance(rsd_conts_item, QLineEdit):
                        #     print(rsd_conts_item.text())
                    col = 0
                    row += 1

    def EN_btn_clicked(self):

        self.clear_red_borders()
        missing_values = self.check_missing_values()

        if missing_values:
            self.EN_label.setText(' * Please fill out the red boxes and press the "Encoding" button again.')
            self.EN_label.setStyleSheet("color: red")
            self.EN_label.setFont(font_log)
            self.highlight_missing_values()
            return

        ursp_sum = []
        for ursp_sum_item in self.ursp_sum:
            ursp_sub1 = []
            for ursp_sub1_item in ursp_sum_item:
                if isinstance(ursp_sub1_item, QLineEdit):
                    ursp_sub1.append(ursp_sub1_item.text())
                elif isinstance(ursp_sub1_item, QComboBox):
                    ursp_sub1.append(ursp_sub1_item.currentText())
            ursp_sum.append(ursp_sub1)
        if debug_mode: print("ursp_sum", ursp_sum)

        rsd_sum = []
        for rsd_sum_item in self.rsd_sum:
            rsd_sub1 = []
            for rsd_sub1_item in rsd_sum_item:
                rsd_sub2 = []
                for rsd_sub2_item in rsd_sub1_item:
                    if isinstance(rsd_sub2_item, QLineEdit):
                        rsd_sub2.append(rsd_sub2_item.text())
                rsd_sub1.append(rsd_sub2)
            rsd_sum.append(rsd_sub1)
        if debug_mode: print("rsd_sum", rsd_sum)

        rsd_conts = []
        for rsd_conts_item in self.rsd_conts:
            rsd_conts_sub1 = []
            for rsd_conts_sub1_item in rsd_conts_item:
                rsd_conts_sub2 = []
                for rsd_conts_sub2_item in rsd_conts_sub1_item:
                    rsd_conts_sub3 = []
                    for rsd_conts_sub3_item in rsd_conts_sub2_item:
                        if isinstance(rsd_conts_sub3_item, QLineEdit):
                            rsd_conts_sub3.append(rsd_conts_sub3_item.text())
                        elif isinstance(rsd_conts_sub3_item, QComboBox):
                            rsd_conts_sub3.append(rsd_conts_sub3_item.currentText())
                    rsd_conts_sub2.append(rsd_conts_sub3)
                rsd_conts_sub1.append(rsd_conts_sub2)
            rsd_conts.append(rsd_conts_sub1)
        if debug_mode: print("rsd_conts", rsd_conts)

        PTI = self.pti.text()
        PLMN = self.plmn.text()
        UPSC = self.upsc.text()

        df_dl_nas, ef_ursp, dl_nas = encoder.ursp_encoder(ursp_sum, rsd_sum, rsd_conts, PTI, PLMN, UPSC)
        df_payload, ursp_sum, rsd_sum, rsd_conts, PTI, PLMN, UPSC = decoder.ursp_decoder(df_dl_nas)
        self.pol_cmd_excel = df_payload

        ursp_info, ursp_conts = display.ursp_to_txt(ursp_sum, rsd_sum, rsd_conts, PTI, PLMN, UPSC)
        pol_cmd_txt = display.payload_to_txt(df_payload)
        self.rst_show(ef_ursp, dl_nas, ursp_info, ursp_conts, pol_cmd_txt)

        self.clear_red_borders()


    def check_missing_values(self):
        missing_values = []

        # Check for missing values in PTI
        if not self.pti.text():
            missing_values.append("PTI")

        # Check for missing values in UPSC
        if not self.upsc.text():
            missing_values.append("UPSC")

        # Check for missing values in ursp_sum
        for ursp_num, ursp_sum_item in enumerate(self.ursp_sum, start=1):
            for index, ursp_sub1_item in enumerate(ursp_sum_item, start=1):
                if isinstance(ursp_sub1_item, QLineEdit) and not ursp_sub1_item.text():
                    missing_values.append(f"URSP_{ursp_num} - Item {index}")

        # Check for missing values in rsd_sum
        for ursp_num, rsd_sum_item in enumerate(self.rsd_sum, start=1):
            for rsd_num, rsd_sub1_item in enumerate(rsd_sum_item, start=1):
                for index, rsd_sub2_item in enumerate(rsd_sub1_item, start=1):
                    if isinstance(rsd_sub2_item, QLineEdit) and not rsd_sub2_item.text():
                        missing_values.append(f"RSD_{ursp_num}_{rsd_num} - Item {index}")

        # Check for missing values in rsd_conts
        for ursp_num, rsd_conts_item in enumerate(self.rsd_conts, start=1):
            for rsd_num, rsd_conts_sub1_item in enumerate(rsd_conts_item, start=1):
                for rsd_conts_num, rsd_conts_sub2_item in enumerate(rsd_conts_sub1_item, start=1):
                    for index, rsd_conts_sub3_item in enumerate(rsd_conts_sub2_item, start=1):
                        if isinstance(rsd_conts_sub3_item, QLineEdit) and not rsd_conts_sub3_item.text():
                            missing_values.append(f"RSD_{ursp_num}_{rsd_num}_{rsd_conts_num} - Item {index}")

        return missing_values

    def highlight_missing_values(self):
        for widget in [self.pti, self.upsc]:
            if not widget.text():
                widget.setStyleSheet("border: 1px solid red;")

        for ursp_num, ursp_sum_item in enumerate(self.ursp_sum, start=1):
            for index, ursp_sub1_item in enumerate(ursp_sum_item, start=1):
                if isinstance(ursp_sub1_item, QLineEdit) and not ursp_sub1_item.text():
                    ursp_sub1_item.setStyleSheet("border: 1px solid red;")

        for ursp_num, rsd_sum_item in enumerate(self.rsd_sum, start=1):
            for rsd_num, rsd_sub1_item in enumerate(rsd_sum_item, start=1):
                for index, rsd_sub2_item in enumerate(rsd_sub1_item, start=1):
                    if isinstance(rsd_sub2_item, QLineEdit) and not rsd_sub2_item.text():
                        rsd_sub2_item.setStyleSheet("border: 1px solid red;")

        for ursp_num, rsd_conts_item in enumerate(self.rsd_conts, start=1):
            for rsd_num, rsd_conts_sub1_item in enumerate(rsd_conts_item, start=1):
                for rsd_conts_num, rsd_conts_sub2_item in enumerate(rsd_conts_sub1_item, start=1):
                    for index, rsd_conts_sub3_item in enumerate(rsd_conts_sub2_item, start=1):
                        if isinstance(rsd_conts_sub3_item, QLineEdit) and not rsd_conts_sub3_item.text():
                            rsd_conts_sub3_item.setStyleSheet("border: 1px solid red;")

    def clear_red_borders(self):

        # Clear label
        self.EN_label.clear()

        # Clear red borders
        for widget in [self.pti, self.upsc]:
            widget.setStyleSheet("")

        for ursp_num, ursp_sum_item in enumerate(self.ursp_sum, start=1):
            for index, ursp_sub1_item in enumerate(ursp_sum_item, start=1):
                if isinstance(ursp_sub1_item, QLineEdit):
                    ursp_sub1_item.setStyleSheet("")

        for ursp_num, rsd_sum_item in enumerate(self.rsd_sum, start=1):
            for rsd_num, rsd_sub1_item in enumerate(rsd_sum_item, start=1):
                for index, rsd_sub2_item in enumerate(rsd_sub1_item, start=1):
                    if isinstance(rsd_sub2_item, QLineEdit):
                        rsd_sub2_item.setStyleSheet("")

        for ursp_num, rsd_conts_item in enumerate(self.rsd_conts, start=1):
            for rsd_num, rsd_conts_sub1_item in enumerate(rsd_conts_item, start=1):
                for rsd_conts_num, rsd_conts_sub2_item in enumerate(rsd_conts_sub1_item, start=1):
                    for index, rsd_conts_sub3_item in enumerate(rsd_conts_sub2_item, start=1):
                        if isinstance(rsd_conts_sub3_item, QLineEdit):
                            rsd_conts_sub3_item.setStyleSheet("")

    def DE_btn_clicked(self):

        log_paste = self.log_text.toPlainText()
        hex_values = re.findall(r'\b[0-9A-Fa-f]{2}\b', log_paste)
        hex_int = [int(x, 16) for x in hex_values]
        hex_str = [f'{x:02X}' for x in hex_int]

        # DL NAS Transport
        if '68' in hex_str:
            start = hex_str.index('68')
            payload_type = hex_str[start+1]
            # Payload container type: UE policy container
            if payload_type == '05':
                # UE policy deliver service type: MANAGE UE POLICY COMMAND or UE POLICY PROVISIONING REQUEST
                df_dl_nas = pd.DataFrame({'hex': hex_str[start:]})
                df_payload, ursp_sum, rsd_sum, rsd_conts, PTI, PLMN, UPSC = decoder.ursp_decoder(df_dl_nas)
                self.pol_cmd_excel = df_payload
                df_dl_nas, ef_ursp, dl_nas = encoder.ursp_encoder(ursp_sum, rsd_sum, rsd_conts, PTI, PLMN, UPSC)

                ursp_info, ursp_conts = display.ursp_to_txt(ursp_sum, rsd_sum, rsd_conts, PTI, PLMN, UPSC)
                pol_cmd_txt = display.payload_to_txt(df_payload)
                self.rst_show(ef_ursp, dl_nas, ursp_info, ursp_conts, pol_cmd_txt)

            else:
                self.DE_label.setText(" [DL NAS Transport] No UE policy container")
                self.DE_label.setStyleSheet("color: red")

        # UL NAS Transport
        elif '67' in hex_str:
            start = hex_str.index('67')
            payload_type = hex_str[start+1]
            # Payload container type: UE policy container
            if payload_type == '05':
                type_int = int(hex_str[start+5], 16) & 0x0F
                if type_int in spec.pol_msg_types:
                    pol_msg_type = spec.pol_msg_types[type_int]
                    self.DE_label.setText(" [UL NAS Transport] UE policy container type: " + pol_msg_type)
                    if 'REJECT' in pol_msg_type:
                        self.DE_label.setStyleSheet("color: red")
                    else:
                        self.DE_label.setStyleSheet("color: blue")
            else:
                self.DE_label.setText(" [UL NAS Transport] No UE policy container")
                self.DE_label.setStyleSheet("color: red")

        # Registration request
        elif '41' in hex_str:
            # Payload container type: UE policy container
            if '85' in hex_str:
                payload = hex_str[hex_str.index('85'):]
                usi_rst = decoder.usi_decoder(payload)
                self.rst_text.setText(usi_rst)
                self.tabs.setCurrentIndex(2)
                self.save_btn.setEnabled(True)
                self.save_label.clear()
            else:
                self.DE_label.setText(" [Registration request] No UE policy container")
                self.DE_label.setStyleSheet("color: red")
        else:
            self.DE_label.setText(" No UE policy container in these hex values.")
            self.DE_label.setStyleSheet("color: red")

    def rst_show(self, ef_ursp, dl_nas, ursp_info, ursp_conts, pol_cmd_txt):
        enter = '\n'
        line_length = 214
        line = '-'*line_length

        rst = ''
        rst += '[SIM EF_URSP]' + enter
        rst += ef_ursp + enter*2
        rst += '[DL NAS TRANSPORT]' + enter
        rst += dl_nas + enter*2
        rst += display.hex_format(dl_nas) + enter*2
        rst += line + enter*2

        rst += '[URSP RULE]' + enter*2
        rst += ursp_info + enter*2
        rst += ursp_conts + enter*2
        rst += line + enter*2

        rst += '[MANAGE UE POLICY COMMAND]' + enter*2
        rst += pol_cmd_txt

        self.rst_text.setText(rst)
        self.tabs.setCurrentIndex(2)
        self.save_btn.setEnabled(True)
        self.save_label.clear()

    def save_btn_clicked(self):
        self.save_btn.setEnabled(False)
        self.save_label.setText(" Saving...")
        rst_msg = excel.to_excel(self.pol_cmd_excel)
        self.save_label.setText(rst_msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    sys.exit(app.exec_())
