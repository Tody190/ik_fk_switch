# coding=utf-8


import pymel.core as pm
import re
import pprint


def get_namespace():
    '''
    get select control namespace...
    '''
    sel_ctl = pm.ls(sl=True)
    if not sel_ctl:
        return None
    namespace = re.match('(\w+:)+', sel_ctl[0].name())
    if not namespace:
        return ''

    return namespace.group()


class HumanIKFKSwitcher():
    def __init__(self, namespace='', ghost_re=True):
        # 命名空间
        self.namespace = namespace
        self.ghost_re_status = ghost_re

        # 保存所有创建过的参考，方便退出时批量删除
        self.__ghost_object = []

    def status(self, part, side, set=False):
        # ikfk 控制器属性名
        attr_name = self.namespace
        attr_name += 'FKIK%s_%s'%(part, side)
        attr_name += '.FKIKBlend'

        # 手动设置控制器状态
        if set == 'FK':
            pm.setAttr(attr_name, 0)
            return 'FK'
        if set == 'IK':
            pm.setAttr(attr_name, 10)
            return 'IK'

        # 自动设置控制器状态
        if pm.getAttr(attr_name) < 5:
            # 控制器切换
            pm.setAttr(attr_name, 0)
            return 'FK'
        else:
            # 控制器切换
            pm.setAttr(attr_name, 10)
            return 'IK'

    def attr_clear(self, attr):
        # 将属性清零
        try:
            attr_value = pm.getAttr(attr)
        except:
            return

        try:
            # 一个值的时候
            if isinstance(attr_value, list):
                pm.setAttr(attr, 0, 0, 0)
            else:
                pm.setAttr(attr, 0)
        except Exception as e:
            print('Attribute clear failed: %s' % attr)
            print(e)

    def world_space_xform(self, src_node, dst_node, *args):
        '''
        将骨骼的空间值 ro， t 等值传给控制器
        Args:
            jnt:
            ctl:
            *args:

        Returns:

        '''
        try:
            for value_type in args:
                # 获取骨骼的旋转值
                value = eval('pm.xform(src_node, q=True, ws=True, %s=True)'%value_type)
                # 传递旋转值
                eval('pm.xform(dst_node, ws=True, %s=%s)'%(value_type, value))
        except Exception as e:
            print('Data transfer error: %s -> %s' % (src_node, dst_node))
            print(e)

    def delete_ghost_joint(self, joint_name):
        ghost_jiont_name = ('ghost_%s' % joint_name).replace(':', '_')
        ghost_jiont_layer = ('ghost_%s_layer' % joint_name).replace(':', '_')
        try:
            pm.delete(ghost_jiont_name)
        except:
            pass
        try:
            pm.delete(ghost_jiont_layer)
        except:
            pass

        return ghost_jiont_name, ghost_jiont_layer

    def create_ghost_joint(self, joint_name):
        ghost_jiont_name, ghost_jiont_layer_name = self.delete_ghost_joint(joint_name)
        for name in (ghost_jiont_name, ghost_jiont_layer_name):
            if name not in self.__ghost_object:
                self.__ghost_object.append(name)

        duplicate_ikx_ro_jnt = pm.duplicate(joint_name, rc=True, name=ghost_jiont_name)[0]
        pm.parent(duplicate_ikx_ro_jnt, world=True)
        pm.select(duplicate_ikx_ro_jnt)
        ghost_jnt_layer = pm.createDisplayLayer(name=ghost_jiont_layer_name)
        pm.setAttr('%s.color' % str(ghost_jnt_layer), 22)
        #pm.mel.eval('layerEditorLayerButtonTypeChange %s;'%ghost_jiont_layer_name)

    def arm_ik_to_fk(self, side):
        # 获取骨骼名
        shoulder_jnt = '%sShoulder_%s' % (self.namespace, side)
        elobow_jnt = '%sElbow_%s' % (self.namespace, side)
        wrist_jnt = '%sWrist_%s' % (self.namespace, side)
        scapula_jnt = '%sScapula_%s' % (self.namespace, side)

        # 获取控制器名
        fk_shoulder_ctl = '%sFKShoulder_%s' % (self.namespace, side)
        fk_elobow_ctl = '%sFKElbow_%s' % (self.namespace, side)
        fk_wrist_ctl = '%sFKWrist_%s' % (self.namespace, side)

        if self.ghost_re_status:
            # 复制一条腿部骨骼作为位置参考
            self.create_ghost_joint(scapula_jnt)

        # fk 位移坐标清零
        for attr in ('%s.tx'%fk_shoulder_ctl,
                     '%s.ty'%fk_shoulder_ctl,
                     '%s.tz'%fk_shoulder_ctl,
                     '%s.tx' % fk_elobow_ctl,
                     '%s.ty' % fk_elobow_ctl,
                     '%s.tz' % fk_elobow_ctl,
                     '%s.tx' % fk_wrist_ctl,
                     '%s.ty' % fk_wrist_ctl,
                     '%s.tz' % fk_wrist_ctl
                     ):
            self.attr_clear(attr)

        for jnt, ctl in (
                (
                        (shoulder_jnt, fk_shoulder_ctl),
                        (elobow_jnt, fk_elobow_ctl),
                        (wrist_jnt, fk_wrist_ctl)
                )
        ):
            # 依次传递旋转值
            self.world_space_xform(jnt, ctl, 'ro')

        # 状态改为FK
        self.status(part='Arm', side=side, set='FK')

    def leg_ik_to_fk(self, side):
        # 获取骨骼名
        hip_jnt = '%sHip_%s' % (self.namespace, side)
        knee_jnt = '%sKnee_%s' % (self.namespace, side)
        ankle_jnt = '%sAnkle_%s' % (self.namespace, side)
        toes_jnt = '%sToes_%s' % (self.namespace, side)
        # 获取控制器名
        fk_hip_ctl = '%sFKHip_%s' % (self.namespace, side)
        fk_knee_ctl = '%sFKKnee_%s' % (self.namespace, side)
        fk_ankle_ctl = '%sFKAnkle_%s' % (self.namespace, side)
        fk_toes_ctl = '%sFKToes_%s' % (self.namespace, side)

        if self.ghost_re_status:
            # 复制一条腿部骨骼作为位置参考
            self.create_ghost_joint(hip_jnt)

        # fk 位移坐标清零
        for attr in ('%s.tx'%fk_hip_ctl,
                     '%s.ty'%fk_hip_ctl,
                     '%s.tz'%fk_hip_ctl,
                     '%s.tx' % fk_knee_ctl,
                     '%s.ty' % fk_knee_ctl,
                     '%s.tz' % fk_knee_ctl,
                     '%s.tx' % fk_ankle_ctl,
                     '%s.ty' % fk_ankle_ctl,
                     '%s.tz' % fk_ankle_ctl,
                     '%s.tx' % fk_toes_ctl,
                     '%s.ty' % fk_toes_ctl,
                     '%s.tz' % fk_toes_ctl
                     ):
            self.attr_clear(attr)

        # 依次将骨骼位置信息传送给控制器
        for jnt, ctl in (
                (
                        (hip_jnt, fk_hip_ctl),
                        (knee_jnt, fk_knee_ctl),
                        (ankle_jnt, fk_ankle_ctl),
                        (toes_jnt, fk_toes_ctl)
                )
        ):
            # 依次传递旋转值
            self.world_space_xform(jnt, ctl, 'ro')

        # 状态改为FK
        self.status(part='Leg', side=side, set='FK')

    def arm_fk_to_ik(self, side):
        wrist_ik_jnt = '%sIKXWrist_%s' % (self.namespace, side)

        wrist_jnt = '%sWrist_%s' % (self.namespace, side)
        elobow_jnt = '%sElbow_%s' % (self.namespace, side)
        scapula_jnt = '%sScapula_%s' % (self.namespace, side)

        ik_arm_ctl = '%sIKArm_%s' % (self.namespace, side)
        pole_leg_ctl = '%sPoleArm_%s' % (self.namespace, side)

        if self.ghost_re_status:
            # 复制一条腿部骨骼作为位置参考
            self.create_ghost_joint(scapula_jnt)

        # 复制ikx骨骼
        duplicate_ikx_ro_jnt = pm.duplicate(wrist_ik_jnt, po=True)[0]
        # 复制ik控制
        duplicate_ik_ctl = pm.duplicate(ik_arm_ctl, po=True)[0]

        # # 将复制的控制器 P 给ikx骨骼
        pm.parentConstraint(duplicate_ikx_ro_jnt, duplicate_ik_ctl, mo=True)
        # # 将ikx骨骼 p 给旋转部分的骨骼
        pm.parentConstraint(wrist_jnt, duplicate_ikx_ro_jnt)
        # 将骨骼的空间坐标位置传递给IK控制器
        for jnt, ctl in ((wrist_jnt, ik_arm_ctl),
                         (elobow_jnt, pole_leg_ctl)):
            self.world_space_xform(jnt, ctl, 't')

        # 将复制的控制器
        rx, ry, rz = pm.getAttr('%s.rotate' % (duplicate_ik_ctl))
        pm.setAttr('%s.rotate' % (ik_arm_ctl), rx, ry, rz)

        # 删除临时骨骼和控制器
        pm.delete(duplicate_ikx_ro_jnt, duplicate_ik_ctl)

        self.status(part='Arm', side=side, set='IK')

    def leg_fk_to_ik(self, side):
        if self.ghost_re_status:
            # 复制一条腿部骨骼作为位置参考
            hip_jnt = '%sHip_%s' % (self.namespace, side)
            self.create_ghost_joint(hip_jnt)

        # 给踝关节创建一个 locator
        ikxankle = '%sIKXAnkle_%s' % (self.namespace, side)
        ikxankle_locator = pm.spaceLocator(n='%s_locator' % ikxankle).name()
        self.world_space_xform(ikxankle, ikxankle_locator, 't')

        # 踝关节 locator 约束 ik 腿部控制器
        ik_leg_ctl = '%sIKLeg_%s' % (self.namespace, side)
        ik_leg_ctl_parentconstraint = pm.parentConstraint(ikxankle_locator, ik_leg_ctl, mo=True).name()

        # 将踝关节 locator 移动到现在 FK 踝关节位置，
        fkxankle_jnt = '%sFKXAnkle_%s' % (self.namespace, side)
        self.world_space_xform(fkxankle_jnt, ikxankle_locator, 't')

        # 删除腿部控制器的约束和 ikxankle_locator
        pm.delete(ik_leg_ctl_parentconstraint)

        # 调整膝盖位置
        knee_jnt = '%sKnee_%s' % (self.namespace, side)
        pole_leg_ctl = '%sPoleLeg_%s' % (self.namespace, side)
        self.world_space_xform(knee_jnt, pole_leg_ctl, 't')

        # 将 ikxankle_locator 旋转约束到腿部IK控制器
        ik_leg_ctl_orientconstraint = pm.orientConstraint(ikxankle_locator, ik_leg_ctl, mo=True)

        # 给 IKXToes 创建一个 locator
        ikxtoes = '%sIKXToes_%s' % (self.namespace, side)
        ikxtoes_locator = pm.spaceLocator(n='%s_locator' % ikxtoes).name()
        self.world_space_xform(ikxtoes, ikxtoes_locator, 't')

        # IKXToes_locator 目标约束 ikxankle_locator
        ikxankle_locator_aimconstraint = pm.aimConstraint(ikxtoes_locator, ikxankle_locator, mo=True)

        # 将 IKXToes_locator 移动到 FK的骨骼上
        fkxtoes = '%sFKXToes_%s' % (self.namespace, side)
        self.world_space_xform(fkxtoes, ikxtoes_locator, 't')

        # 将两个约束删除
        pm.delete(ik_leg_ctl_orientconstraint, ikxankle_locator_aimconstraint)

        # 将踝关节 locator 重新移动到 ik 的踝关节
        self.world_space_xform(ikxankle, ikxankle_locator, 't')

        # 踝关节 locator 重新约束到 ik 腿部控制器
        ik_leg_ctl_parentconstraint = pm.parentConstraint(ikxankle_locator, ik_leg_ctl, mo=True).name()

        # 踝关节 locator 重新移动到现在 FK 踝关节位置，
        self.world_space_xform(fkxankle_jnt, ikxankle_locator, 't')

        # 删除腿部控制器的约束和 ikxankle_locator
        pm.delete(ik_leg_ctl_parentconstraint)
        # 删除所有 locator
        pm.delete(ikxankle_locator, ikxtoes_locator)

        # 重新调整膝盖位置
        self.world_space_xform(knee_jnt, pole_leg_ctl, 't')

        # 切换到 IK 控制器显示
        self.status(part='Leg', side=side, set='IK')

    def delete_all_ghost_object(self):
        for ghost_object in self.__ghost_object:
            try:
                pm.delete(ghost_object)
            except:
                pass
