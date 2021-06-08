# -*- coding: utf-8 -*-
# author:yangtao
# time: 2021/05/26


import traceback
import sys

from PySide2 import QtWidgets
from PySide2 import QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


def handle_error_dialog(func):
    '''
    弹出窗户口显示 traceback.format_exc() 的报错
    '''

    def handle(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical,
                                  u"错误",
                                  traceback.format_exc()).exec_()
    return handle


def getMayaWindow():
    main_window_pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_pointer), QtWidgets.QWidget)


class MainUI(QtWidgets.QWidget):
    instance = None
    def __init__(self):
        super(MainUI, self).__init__()
        self.settings = QtCore.QSettings(u"hz_soft", u"ik_fk_switch")  # 保存设置类
        self.ghost_re_status = True

        self.__setup_ui()
        self.__retranslate_ui()

    def __setup_ui(self):
        self.setParent(getMayaWindow(), QtCore.Qt.Window)  # 设置maya为父级窗口
        self.main_window = QtWidgets.QVBoxLayout(self)

        # 命名空间获取部分
        self.name_space_layout = QtWidgets.QHBoxLayout()
        self.name_space_lineedit = QtWidgets.QLineEdit()
        self.get_name_space_btn = QtWidgets.QPushButton()
        self.name_space_layout.addWidget(self.name_space_lineedit)
        self.name_space_layout.addWidget(self.get_name_space_btn)

        # 胳膊IKIF切换
        self.arm_layout = QtWidgets.QHBoxLayout()
        self.left_arm_ikfk_btn = QtWidgets.QPushButton()
        self.right_arm_ikfk_btn = QtWidgets.QPushButton()
        self.arm_layout.addWidget(self.right_arm_ikfk_btn)
        self.arm_layout.addWidget(self.left_arm_ikfk_btn)

        # 腿IKFK切换
        self.leg_layout = QtWidgets.QHBoxLayout()
        self.left_leg_ikfk_btn = QtWidgets.QPushButton()
        self.right_leg_ikfk_btn = QtWidgets.QPushButton()
        self.leg_layout.addWidget(self.right_leg_ikfk_btn)
        self.leg_layout.addWidget(self.left_leg_ikfk_btn)

        # 踝关节
        self.set_layout = QtWidgets.QHBoxLayout()
        self.ghost_re_checkbox = QtWidgets.QCheckBox()
        self.set_layout.addStretch()
        self.set_layout.addWidget(self.ghost_re_checkbox)

        # 主窗口
        self.main_window.addLayout(self.name_space_layout)
        self.main_window.addLayout(self.arm_layout)
        self.main_window.addLayout(self.leg_layout)
        self.main_window.addLayout(self.set_layout)

    def __retranslate_ui(self):
        self.setWindowTitle("AdvancedSkeleton IK_IF 无缝切换")
        self.resize(360, 100)
        self.name_space_lineedit.setText(u"选中大纲内一个物体，点击获取空间名")
        self.get_name_space_btn.setText(u"获取名称空间")
        self.left_arm_ikfk_btn.setText(u"左胳膊")
        self.left_arm_ikfk_btn.setEnabled(False)
        self.right_arm_ikfk_btn.setText(u"右胳膊")
        self.right_arm_ikfk_btn.setEnabled(False)
        self.left_leg_ikfk_btn.setText(u"左腿")
        self.left_leg_ikfk_btn.setEnabled(False)
        self.right_leg_ikfk_btn.setText(u"右腿")
        self.right_leg_ikfk_btn.setEnabled(False)
        self.ghost_re_checkbox.setText(u"影子骨骼")
        if self.settings.value('ghost_re_status', u'true') == u'true':
            self.ghost_re_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
            self.ghost_re_status = True
        else:
            self.ghost_re_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.ghost_re_status = False

    def save_setting(self):
        if self.ghost_re_checkbox.checkState() == QtCore.Qt.CheckState.Checked:
            self.settings.setValue('ghost_re_status', u'true')
        else:
            self.settings.setValue('ghost_re_status', u'false')

    def button_enabled(self, status):
        self.right_arm_ikfk_btn.setEnabled(status)
        self.left_arm_ikfk_btn.setEnabled(status)
        self.right_leg_ikfk_btn.setEnabled(status)
        self.left_leg_ikfk_btn.setEnabled(status)


if __name__ == "__main__":
    if not MainUI.instance:
        MainUI.instance = MainUI()
    MainUI.instance.show()
    MainUI.instance.raise_()