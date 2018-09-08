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

class POEtoolbox():

    def make_offset_bone(self, selected_bone):

        # export pose to given to_file
        print('POEtoolbox.make_offset_bone: WIP !')

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
        poetoolbox.make_offset_bone(pose_bones)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(ToolBoxPanel)
    bpy.utils.register_class(POSE_OT_toolbox_offset_bone)

def unregister():
    bpy.utils.unregister_class(ToolBoxPanel)
    bpy.utils.unregister_class(POSE_OT_toolbox_offset_bone)

# bpy.utils.register_module(__name__)
