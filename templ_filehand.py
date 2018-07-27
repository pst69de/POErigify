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
Template for file handling v1

This script/addon:
    - Template routines for file usage includng File dialogs
    - Extra: store some property in WindowManager

TO-DO:
    - ...

GitHub: https://github.com/pst69de/POErigify
Wiki: http://wiki69.pst69.homeip.net/index.php/POErigify
'''


import bpy
from bpy.props import StringProperty, CollectionProperty, BoolVectorProperty
import json

class porter():

    def export_pose(self, pose_bones, layers, to_file):

        # export pose to given to_file
        print('porter.export_pose: export to %s' % to_file)

        root_bone = None
        if pose_bones['ROOT']:
            root_bone = pose_bones['ROOT']
        if pose_bones['root']:
            root_bone = pose_bones['root']


        return
        # method export_pose over

    def import_pose(self, pose_bones, from_file):

        # import pose to given pose_bones

        return
        # method import_pose over
    # class over
porter = porter()

# GUI (Panel)
#
class ToolsPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_context = "posemode"
    bl_label = 'POErigify Pose Export/Import'

    # draw the gui
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        id_store = context.window_manager
        # ~ toolsettings = context.tool_settings
        # the extra layer for tweaks
        col = layout.column(align=True)
        row = col.row(align=True)
        bone_layers = bpy.context.active_pose_bone.bone.layers[:]
        for i in range(8):    # Layers 0-7
            icon = "NONE"
            if bone_layers[i]:
                icon = "LAYER_ACTIVE"
            row.prop(id_store, "pose_bones_export_set", index=i, toggle=True, text="", icon=icon)
        row = col.row(align=True)
        for i in range(16, 24):     # Layers 16-23
            icon = "NONE"
            if bone_layers[i]:
                icon = "LAYER_ACTIVE"
            row.prop(id_store, "pose_bones_export_set", index=i, toggle=True, text="", icon=icon)
        # 2nd row for the extra layer for tweaks
        col = layout.column(align=True)
        row = col.row(align=True)
        for i in range(8, 16):  # Layers 8-15
            icon = "NONE"
            if bone_layers[i]:
                icon = "LAYER_ACTIVE"
            row.prop(id_store, "pose_bones_export_set", index=i, toggle=True, text="", icon=icon)
        row = col.row(align=True)
        for i in range( 24, 32 ): # Layers 24-31
            icon = "NONE"
            if bone_layers[i]:
                icon = "LAYER_ACTIVE"
            row.prop(id_store, "pose_bones_export_set", index=i, toggle=True, text="", icon=icon)
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('rigify_expimp.export', icon='EXPORT')
        row = col.row(align=True)
        row.operator('rigify_expimp.import', icon='IMPORT')


class POSE_OT_expimp_export(bpy.types.Operator):
    bl_label = 'Export current pose'
    bl_idname = 'rigify_expimp.export'
    bl_description = 'Exports current Action to JSON'
    bl_options = {'REGISTER', 'UNDO'}

    # https://blender.stackexchange.com/questions/39854/how-can-i-open-a-file-select-dialog-via-python-to-add-an-image-sequence-into-vse
    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    #this can be look into the one of the export or import python file.
    #need to set a path so so we can get the file name and path
    filepath = StringProperty(name="File Path", description="Filepath used for exporting json files", maxlen= 256, default= "")
    files = CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
        )

    @classmethod
    def poll(self, context):
        return (context.object.type == 'ARMATURE' and context.mode == 'POSE' and context.active_object.data.get("rig_id"))

    # on mouse up:
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = bpy.context.active_object
        pose_bones = bpy.context.selected_pose_bones
        action = obj.animation_data.action
        id_store = context.window_manager

        #print("*************SELECTED FILES ***********")
        #print("FILEPATH: %s" % self.filepath) # display the file name and current path
        #for file in self.files:
        #    print("FILENAME: %s" % file.name)
        porter.export_pose(pose_bones, id_store.pose_bones_export_set, self.filepath)

        return {'FINISHED'}


class POSE_OT_expimp_import(bpy.types.Operator):
    bl_label = 'Import an pose'
    bl_idname = 'rigify_expimp.import'
    bl_description = 'Imports Action from JSON to selected'
    bl_options = {'REGISTER', 'UNDO'}

    # https://blender.stackexchange.com/questions/39854/how-can-i-open-a-file-select-dialog-via-python-to-add-an-image-sequence-into-vse
    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    #this can be look into the one of the export or import python file.
    #need to set a path so so we can get the file name and path
    filepath = StringProperty(name="File Path", description="Filepath used for importing json files", maxlen= 256, default= "")
    files = CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
        )

    @classmethod
    def poll(cls, context):
        return (context.object.type == 'ARMATURE' and context.mode == 'POSE' and context.active_object.data.get("rig_id"))

    # on mouse up:
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = bpy.context.active_object
        pose_bones = bpy.context.selected_pose_bones
        action = obj.animation_data.action
        id_store = context.window_manager

        porter.import_pose(pose_bones, self.filepath)

        return {'FINISHED'}


def register():
    IDStore = bpy.types.WindowManager
    IDStore.pose_bones_export_set = BoolVectorProperty(
        size        = 32,
        description = "Layers exporting pose bones",
        default     = tuple( [ i < 29 for i in range(0, 32) ] )
        )
    bpy.utils.register_class(ToolsPanel)
    bpy.utils.register_class(POSE_OT_expimp_export)
    bpy.utils.register_class(POSE_OT_expimp_import)

def unregister():
    IDStore = bpy.types.WindowManager
    bpy.utils.unregister_class(ToolsPanel)
    bpy.utils.unregister_class(POSE_OT_expimp_export)
    bpy.utils.unregister_class(POSE_OT_expimp_import)
    del IDStore.pose_bones_export_set

# bpy.utils.register_module(__name__)
