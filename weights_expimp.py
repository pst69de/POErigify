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
Weights Export & Import v0.1

This script/addon:
    - Exports a set of Weights as JSON
    - Imports a Weights
    - frame taken from rot_mode.py in the same library

TO-DO:
    - Exporter
    - Importer
    - ...

GitHub: https://github.com/pst69de/POErigify
Wiki: http://wiki69.pst69.homeip.net/index.php/POErigify
'''


import bpy
from bpy.props import StringProperty, CollectionProperty
import json
import mathutils

class weightporter():

    def export_weights(self, to_file, from_mesh):

        # export weights to given to_file
        print('weightporter.export_weights: export to %s' % to_file)
        weights_dic = {}
        me = from_mesh
        vgs = from_mesh.vertex_groups
        # for vertex group in mesh groups:
        for vg in vgs:
            wdic = weights_dic[vg.name] = {}
            vgix = vg.index
            vs = [ v for v in me.data.vertices if vgix in [ vxg.group for vxg in v.groups if vxg.weight > 0.001] ]
            print('weightporter.export_weights: %s, %d vertices' % (vg.name, len(vs)))
            for vertex in vs:
                for vxg in vertex.groups:
                    if vxg.group == vgix:
                        wdic[vertex.index] = vxg.weight
                        #print('v: %d : %f' % (vertex.index, vxg.weight))
        output_file = open(to_file, 'w')
        json.dump(weights_dic, output_file, sort_keys=True, indent=4)
        output_file.close()
        return
        # method export_pose over

    def import_weights(self, from_file, to_mesh):

        # import weights to mesh
        print('weightporter.import_weights: import from %s' % from_file)
        me = to_mesh
        vgs = to_mesh.vertex_groups
        input_file = open(from_file, "r")
        weights_dic = None
        try:
            weights_dic = json.load(input_file)
        except:
            print('weightporter.import_weights: Errors in json file: {0}'.format(simple_path(input_file)))
            weights_dic = None
        input_file.close()
        if weights_dic:
            print('weightporter.import_weights: valid json dic')
            for vg in weights_dic:
                print('weightporter.import_weights: group: %s, %d vertices' % (vg, len(weights_dic[vg])))
                gr = weights_dic[vg]
                vgr = vgs.active
                if not vg in vgs:
                    vgr = vgs.new(vg)
                else:
                    vgr = vgs[vg]
                for vix in gr:
                    vidx = int(vix)
                    #print('vertex: %d, %f' % (vidx, gr[vix]))
                    vgr.add([vidx],gr[vix],'REPLACE')
        return
        # method import_pose over
    # class over
weightPorter = weightporter()

# GUI (Panel)
#
class ToolsPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_label = 'POErigify Weights Export/Import'

    @classmethod
    def poll(cls, context):
        return context.mode in ['PAINT_WEIGHT']

    # draw the gui
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        id_store = context.window_manager
        # ~ toolsettings = context.tool_settings
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('rigify_expimp.export_weights', icon='EXPORT')
        row = col.row(align=True)
        row.operator('rigify_expimp.import_weights', icon='IMPORT')


class WEIGHT_OT_expimp_export(bpy.types.Operator):
    bl_label = 'Export weights of mesh'
    bl_idname = 'rigify_expimp.export_weights'
    bl_description = 'Exports weights to JSON'
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
        return (context.active_object.type == 'MESH' and context.mode == 'PAINT_WEIGHT')

    # on mouse up:
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object

        #print("*************SELECTED FILES ***********")
        #print("FILEPATH: %s" % self.filepath) # display the file name and current path
        #for file in self.files:
        #    print("FILENAME: %s" % file.name)
        weightPorter.export_weights(self.filepath, mesh)

        return {'FINISHED'}


class WEIGHT_OT_expimp_import(bpy.types.Operator):
    bl_label = 'Import weights from JSON'
    bl_idname = 'rigify_expimp.import_weights'
    bl_description = 'Imports weights from JSON'
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
        return (context.active_object.type == 'MESH' and context.mode == 'PAINT_WEIGHT')

    # on mouse up:
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = bpy.context.active_object
        mesh = bpy.context.active_object

        weightPorter.import_weights(self.filepath, mesh)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ToolsPanel)
    bpy.utils.register_class(WEIGHT_OT_expimp_export)
    bpy.utils.register_class(WEIGHT_OT_expimp_import)

def unregister():
    bpy.utils.unregister_class(ToolsPanel)
    bpy.utils.unregister_class(WEIGHT_OT_expimp_export)
    bpy.utils.unregister_class(WEIGHT_OT_expimp_import)

# bpy.utils.register_module(__name__)
