# -*- coding: utf-8 -*-
# author:yangtao
# time: 2021/05/25


from . import ui
from . import core


class Response(ui.MainUI):
    def __init__(self):
        super(Response, self).__init__()
        self.name_space = None
        self.human_ikfk_switcher = None

        self.__setup_connect()

    def __setup_connect(self):
        self.get_name_space_btn.clicked.connect(self.get_name_space)

        self.right_arm_ikfk_btn.clicked.connect(self.switch_right_arm)
        self.left_arm_ikfk_btn.clicked.connect(self.switch_left_arm)
        self.right_leg_ikfk_btn.clicked.connect(self.switch_right_leg)
        self.left_leg_ikfk_btn.clicked.connect(self.switch_left_leg)

        self.ghost_re_checkbox.stateChanged.connect(self.__set_ghost_re)

    def instantiate_switcher(self):
        # 删除遗留的幽灵骨骼
        if self.human_ikfk_switcher and not self.ghost_re_status:
            self.human_ikfk_switcher.delete_all_ghost_object()

        self.human_ikfk_switcher = core.HumanIKFKSwitcher(self.name_space,
                                                          ghost_re=self.ghost_re_status)

    def __set_ghost_re(self, arg):
        if int(arg) == 0:
            self.ghost_re_status = False
        else:
            self.ghost_re_status = True
        self.instantiate_switcher()

    def get_name_space(self):
        """
        获取名称空间
        Returns:

        """
        self.name_space = core.get_namespace()
        if self.name_space == None:
            return
        self.name_space_lineedit.setText(self.name_space)
        self.instantiate_switcher()
        self.button_enabled(True)

    def switch_right_arm(self):
        status = self.human_ikfk_switcher.status("Arm", "R")
        if status == "IK":
            self.human_ikfk_switcher.arm_ik_to_fk("R")
        else:
            self.human_ikfk_switcher.arm_fk_to_ik("R")

    def switch_left_arm(self):
        status = self.human_ikfk_switcher.status("Arm", "L")
        if status == "IK":
            self.human_ikfk_switcher.arm_ik_to_fk("L")
        else:
            self.human_ikfk_switcher.arm_fk_to_ik("L")

    def switch_right_leg(self):
        status = self.human_ikfk_switcher.status("Leg", "R")
        if status == "IK":
            self.human_ikfk_switcher.leg_ik_to_fk("R")
        else:
            self.human_ikfk_switcher.leg_fk_to_ik("R")

    def switch_left_leg(self):
        status = self.human_ikfk_switcher.status("Leg", "L")
        if status == "IK":
            self.human_ikfk_switcher.leg_ik_to_fk("L")
        else:
            self.human_ikfk_switcher.leg_fk_to_ik("L")

    def closeEvent(self, event):
        if self.human_ikfk_switcher:
            self.human_ikfk_switcher.delete_all_ghost_object()
        self.save_setting()



@ui.handle_error_dialog
def load_ui():
    if not Response.instance:
        Response.instance = Response()
    Response.instance.show()
    Response.instance.raise_()
