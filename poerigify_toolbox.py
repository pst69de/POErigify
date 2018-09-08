#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================
'''
POErigify Toolbox routines v1

This script/addon:
    - provides a tool to make offset bones in the finished rig
      like in https://lollypopman.com/2018/09/06/pro-tip-double-controls/ described
    - ...

TO-DO:
    - ...

GitHub: https://github.com/pst69de/POErigify
Wiki: http://wiki69.pst69.homeip.net/index.php/POErigify
'''


import bpy
from bpy.props import StringProperty, CollectionProperty, BoolVectorProperty
import json
from .utils import copy_bone_simple

def onlySuffix(bone_name):
    # if there is a defined suffix, cut that for result
    # maybe in future even if there is an instance number
    suffix = ''
    #print('POEtoolbox.onlySuffix: %s' % bone_name[-2:].upper())
    if bone_name[-2:].upper() in ['.L','.R','.F','.B','.U','.D']:
        suffix = bone_name[-2:]
    return suffix
    # def onlySuffix() over

def woSuffix(bone_name):
    # if a suffix is return without
    suffix = 0
    suffix = len(onlySuffix(bone_name))
    #print('POEtoolbox.woSuffix: suffix: ',suffix,bone_name[0:-suffix])
    if suffix > 0:
        return bone_name[0:-suffix]
    else:
        return bone_name
    # def woSuffix() over

class POEtoolbox():

    def make_offset_bone(self, active_object, selected_bones):

        # export pose to given to_file
        print('WIP ! POEtoolbox.make_offset_bone: on %s' % active_object.name)
        # only one to be selected (exit elsewise)
        if len(selected_bones) != 1:
            raise ValueError("Select only ONE bone !")
        org_bone = selected_bones[0].name
        # maybe _n generationwise in future
        copi_bone = woSuffix(org_bone) + '_ofs' + onlySuffix(org_bone)
        print('POEtoolbox.make_offset_bone: org: %s copy: %s' %(org_bone,copi_bone))
        # set pose to rest-position
        active_object.data.pose_position = 'REST'
        # swith to edit-mode
        bpy.ops.object.mode_set(mode='EDIT')
        eb = active_object.data.edit_bones
        # copy org_bone to copy_bone
        copied_bone = copi_bone
        copied_bone = copy_bone_simple(active_object,org_bone,copi_bone)
        # scan children of org_bone and reparent to copied_bone
        children = [aChilds.name for aChilds in eb[org_bone].children]
        for child in children:
            print('POEtoolbox.make_offset_bone: reparent: ',child)
            eb[child].parent = eb[copied_bone]
        # reparent copied_bone to org_bone
        print('POEtoolbox.make_offset_bone: reparent: ',child)
        eb[copied_bone].parent = eb[org_bone]
        # switch to pose-mode
        bpy.ops.object.mode_set(mode='POSE')
        pb = active_object.pose.bones
        # scan all bones for constraints tageting org_bone
        #   and redirect to copy_bone
        for pbone in pb:
            if len(pbone.constraints) > 0:
                for aConstraint in pbone.constraints:
                    if hasattr(aConstraint,'target') and hasattr(aConstraint,'subtarget'):
                        if aConstraint.subtarget == org_bone:
                            print('POEtoolbox.make_offset_bone: retarget: %s.%s from %s to %s'
                                % ( pbone.name
                                    , aConstraint.name
                                    , aConstraint.subtarget
                                    , copied_bone
                                    )
                                )
                            aConstraint.subtarget = copied_bone
        # copy and resize widget of copied_bone
        print('POEtoolbox.make_offset_bone: rescale: ', pb[copied_bone].custom_shape_scale)
        pb[copied_bone].bone_group = pb[org_bone].bone_group
        pb[copied_bone].custom_shape = pb[org_bone].custom_shape
        pb[copied_bone].custom_shape_scale = pb[org_bone].custom_shape_scale - 0.1
        # unset rest-position
        active_object.data.pose_position = 'POSE'
        return
        # method make_offset_bone over

    # class over
poetoolbox = POEtoolbox()

# GUI (Panel)
#
class ToolBoxPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_context = "posemode"
    bl_label = 'POErigify Toolbox'

    # draw the gui
    def draw(self, context):
        layout = self.layout
        # ~ toolsettings = context.tool_settings
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('rigify_toolbox.offset_bone', icon='GROUP_BONE')


class POSE_OT_toolbox_offset_bone(bpy.types.Operator):
    bl_label = 'Create offset bone WIP'
    bl_idname = 'rigify_toolbox.offset_bone'
    bl_description = 'Create offset bone of one selected'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return (context.object.type == 'ARMATURE' and context.mode == 'POSE' and context.active_object.data.get("rig_id"))

    def execute(self, context):
        obj = bpy.context.active_object
        pose_bones = bpy.context.selected_pose_bones

        #print("*************SELECTED FILES ***********")
        #print("FILEPATH: %s" % self.filepath) # display the file name and current path
        #for file in self.files:
        #    print("FILENAME: %s" % file.name)
        poetoolbox.make_offset_bone(obj, pose_bones)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(ToolBoxPanel)
    bpy.utils.register_class(POSE_OT_toolbox_offset_bone)

def unregister():
    bpy.utils.unregister_class(ToolBoxPanel)
    bpy.utils.unregister_class(POSE_OT_toolbox_offset_bone)

# bpy.utils.register_module(__name__)
