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
###############################
# Template rig class
# by Patrick O. Ehrmann
# based on simple_tentacle.py in the limbs rigs section
# documenting the steps of implementation a costum metarig bone system
# first version for the "super_stretcher" bone system
# feel free to reuse on your own project
#
# super_ring:
# of a radial bone make a deforming ring structure of
# configurable "wing"-lengths
# (a wing is half of the ring e.g. 3 in the wing makes 6 elements around)
#
# -> it is a good idea to keep your bone lists consistent
#    with the parenting order, then it is easier to parent the bones
#    by looping the bone lists
###############################
import bpy
import mathutils
import math
from ...utils import copy_bone, copy_bone_simple, put_bone
from ...utils import org, strip_org, mch, strip_mch, deformer, strip_def
from ...utils import connected_children_names
from ...utils import create_sphere_widget
from ...utils import create_widget, create_circle_widget
from ...utils import MetarigError
from rna_prop_ui import rna_idprop_ui_prop_get


class Rig:

    def __init__(self, obj, bone_name, params):
        # constructor for this class, in here the local parameters are defined
        self.obj = obj
        print('!!!WIP!!! super_ring on %s' % bone_name)
        # stretch_bone is the main element of this system
        self.radial_bone = bone_name
        # just in case we have a suffix
        # (L = Left, R = Right, F = Front, B = Back, U = to Up above, D = to Down below)
        self.suffix = ''
        if bone_name[-2].upper() in ['.L','.R','.F','.B','.U','.D']:
            self.suffix = bone_name[-2]
        # this list may be modified by head or tail params
        self.org_bones = [bone_name]
        # + bone_name.parent
        #print('super_ring params.guide_in_bone %s' % params.guide_in_bone)
        if params.sizing_bone:
            self.org_bones += [org(params.sizing_bone)]
            self.sizing_bone = org(params.sizing_bone)
        self.params = params
        # number of stretchy elements
        self.wing_elements = params.wing_elements
        # not yet: tweaks on extra layer
        #if params.tweak_extra_layers:
        #    self.tweak_layers = list(params.tweak_layers)
        #else:
        #    self.tweak_layers = None
        # construct must have 2 bones: radial_bone, sizing_bone
        # POE 2018-07-24: radial_bone carries this rig, sizing_bone may not be there
        if len(self.org_bones) > 2 or not self.obj.pose.bones[self.sizing_bone]:
            raise MetarigError(
                "RIGIFY ERROR: invalid rig structure on bone: %s (%d bones)" % (strip_org(bone_name),len(self.org_bones))
            )

    def make_mechanics(self):

        # construct mechanics of the bone system
        # i.e. for tweaking the stretch route
        print('super_ring.make_mechanics')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        mch_chain = []
        # no separate mechanics for this system
        # and out
        return mch_chain

    def make_controls(self):

        # Just a control for the guide_out,
        # but keep structure to build more complex control sets
        print('super_ring.make_controls')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        org_bones = self.org_bones
        ctrl_chain = []
        # just one control
        if self.sizing_bone:
            name = org_bones[1]
            ctrl_bone = copy_bone(self.obj,name,strip_org(name))
            ctrl_chain.append(ctrl_bone)
        # Make widgets
        bpy.ops.object.mode_set(mode ='OBJECT')
        for ctrl in ctrl_chain:
            create_circle_widget(self.obj, ctrl, radius=1, head_tail=0)
        return ctrl_chain

    def make_tweaks(self, mch_chain):

        # the tweaks itself are the shaped bones
        # controlling the mechanics in the bone system
        print('super_ring.make_tweaks')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        tweak_chain = []
        # not yet: tweaks for this system
        ## for over index because 1st is left out
        #for ix in range( len( mch_chain)):
        #    if ix > 0:
        #        tweak_name = strip_mch(mch_chain[ix])
        #        tweak_bone = copy_bone(self.obj,mch_chain[ix],tweak_name)
        #        tweak_chain.append(tweak_bone)
        #        eb[ tweak_bone ].length /= 4
        ## Make widgets
        #bpy.ops.object.mode_set(mode = 'OBJECT')
        #for tweak in tweak_chain:
        #    create_sphere_widget( self.obj, tweak )
        #    tweak_pb = self.obj.pose.bones[ tweak ]
        #    tweak_pb.lock_rotation = (True, False, True)
        #    tweak_pb.lock_scale    = (False, True, False)
        #    if self.tweak_layers:
        #        tweak_pb.bone.layers = self.tweak_layers
        # and out
        return tweak_chain

    def make_deform(self, mch_chain):

        # make the finally deforming skeleton meshes are rigged to
        print('super_ring.make_deform')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        def_chain = []
        org_bones = self.org_bones
        # from radial_bone make 2 wings
        ix = 1
        base_name = strip_org(self.radial_bone)
        prev_bone = self.radial_bone
        def_name = deformer('%s.%03d' % (base_name,ix))
        print('super_ring.make_deform make %s' % def_name)
        def_bone = copy_bone_simple( self.obj, prev_bone, def_name)
        put_bone(self.obj, def_bone,  eb[ prev_bone ].tail)
        #eb[def_bone].transform(mat_rot,scale=False, roll=False)
        #print('super_ring.make_deform head before ', eb[def_bone].head)
        #print('super_ring.make_deform tail before ', eb[def_bone].tail)
        # 1st right angle turn to the tangent of the circular system
        # POE 2018-07-24: rotation operation depends on orientation of radial_bone
        mat_rot = mathutils.Matrix.Rotation(math.radians(90.0), 4, eb[self.radial_bone].x_axis)
        eb[def_bone].tail = (mat_rot * eb[def_bone].vector) + eb[def_bone].head
        # 2nd half angle turn to set chord/secant
        mat_rot = mathutils.Matrix.Rotation(math.radians(90.0/self.wing_elements), 4, eb[self.radial_bone].x_axis)
        eb[def_bone].tail = (mat_rot * eb[def_bone].vector) + eb[def_bone].head
        #print('super_ring.make_deform tail after ', eb[def_bone].tail)
        def_chain += [def_bone]
        for i in range(1,self.wing_elements):
            prev_bone = def_bone
            ix += 1
            def_name = deformer('%s.%03d' % (base_name,ix))
            print('super_ring.make_deform make %s' % def_name)
            def_bone = copy_bone_simple( self.obj, prev_bone, def_name)
            put_bone(self.obj, def_bone,  eb[ prev_bone ].tail)
            # 3rd further elements go with full angle turn in the next chord/secant
            mat_rot = mathutils.Matrix.Rotation(math.radians(180.0/self.wing_elements), 4, eb[self.radial_bone].x_axis)
            eb[def_bone].tail = (mat_rot * eb[def_bone].vector) + eb[def_bone].head
            #print('super_ring.make_deform tail after ', eb[def_bone].tail)
            def_chain += [def_bone]
        # same procedure the other way around
        prev_bone = self.radial_bone
        ix += 1
        def_name = deformer('%s.%03d' % (base_name,ix))
        print('super_ring.make_deform make %s' % def_name)
        def_bone = copy_bone_simple( self.obj, prev_bone, def_name)
        put_bone(self.obj, def_bone,  eb[ prev_bone ].tail)
        # 1st right angle turn to the tangent of the circular system
        mat_rot = mathutils.Matrix.Rotation(math.radians(-90.0), 4, eb[self.radial_bone].x_axis)
        eb[def_bone].tail = (mat_rot * eb[def_bone].vector) + eb[def_bone].head
        # 2nd half angle turn to set chord/secant
        mat_rot = mathutils.Matrix.Rotation(math.radians(-90.0/self.wing_elements), 4, eb[self.radial_bone].x_axis)
        eb[def_bone].tail = (mat_rot * eb[def_bone].vector) + eb[def_bone].head
        #print('super_ring.make_deform tail after ', eb[def_bone].tail)
        def_chain += [def_bone]
        for i in range(1,self.wing_elements):
            prev_bone = def_bone
            ix += 1
            def_name = deformer('%s.%03d' % (base_name,ix))
            print('super_ring.make_deform make %s' % def_name)
            def_bone = copy_bone_simple( self.obj, prev_bone, def_name)
            put_bone(self.obj, def_bone,  eb[ prev_bone ].tail)
            # 3rd further elements go with full angle turn in the next chord/secant
            mat_rot = mathutils.Matrix.Rotation(math.radians(-180.0/self.wing_elements), 4, eb[self.radial_bone].x_axis)
            eb[def_bone].tail = (mat_rot * eb[def_bone].vector) + eb[def_bone].head
            #print('super_ring.make_deform tail after ', eb[def_bone].tail)
            def_chain += [def_bone]
        # and out
        return def_chain

    # helper for making constraints
    def make_constraint(self, bone, constraint):
        bpy.ops.object.mode_set(mode='OBJECT')
        pb = self.obj.pose.bones

        owner_pb = pb[bone]
        const = owner_pb.constraints.new(constraint['constraint'])
        const.target = self.obj
        # testing
        #for p in [k for k in constraint.keys()]:
        #    print('super_stretcher.make_constraint constraint.keys() %s' % p)
        # filter contraint props to those that actually exist in the current
        # type of constraint, then assign values to each
        for p in [k for k in constraint.keys() if k in dir(const)]:
            setattr(const, p, constraint[p])

    def make_constraints(self, all_bones):

        # make the needed constrainting modifiers to the bone system
        print('super_ring.make_constraints')
        # test if above works out
        #return
        bpy.ops.object.mode_set(mode ='OBJECT')
        org_bones = self.org_bones
        pb        = self.obj.pose.bones
        # Deform bones' constraints
        ctrls   = all_bones['control']
        tweaks  = all_bones['tweak'  ]
        deforms = all_bones['deform' ]
        # copy scale (xz) from self.sizing_bone
        # maybe COPY_TRANSFORMS
        print('super_ring.make_constraints %s copy_scale %s' % (self.radial_bone,self.sizing_bone))
        self.make_constraint( self.radial_bone, {
            'constraint': 'COPY_SCALE'
            , 'subtarget' : strip_org(self.sizing_bone)
            , 'use_y' : True
            } )
        # lock rotation, translation on control
        pbone = pb[strip_org(self.sizing_bone)]
        pbone.lock_location = (True, True, True)
        pbone.lock_rotation = (True, True, True)
        pbone.lock_rotation_w = True
        pbone.lock_scale = (False, False, False)
        # and out

    def parent_bones(self, all_bones):

        # give the parenting to the constructed bone system
        print('super_ring.parent_bones')
        # test if above works out
        #return
        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones
        eb        = self.obj.data.edit_bones

        # parent sizing_bone to radial_bone

        if self.sizing_bone:
            # guide_out control is 2nd
            print('super_ring.parent_bones parent %s to %s' % (self.sizing_bone,self.radial_bone))
            eb[self.sizing_bone].use_connect = False
            eb[self.sizing_bone].parent = eb[self.radial_bone]
            eb[self.sizing_bone].use_inherit_scale = False

        # Parent deform bones
        def_bones = all_bones['deform']
        prev_bone = self.radial_bone
        for def_bone in def_bones[:self.wing_elements]:
            print('super_ring.parent_bones parent %s to %s' % (def_bone,prev_bone))
            eb[def_bone].use_connect = True
            eb[def_bone].parent = eb[prev_bone]
            prev_bone = def_bone
        # and other way around
        prev_bone = self.radial_bone
        for def_bone in def_bones[self.wing_elements:]:
            print('super_ring.parent_bones parent %s to %s' % (def_bone,prev_bone))
            eb[def_bone].use_connect = True
            eb[def_bone].parent = eb[prev_bone]
            prev_bone = def_bone
        # and out

    def generate(self):

        # main generation method
        print('super_ring.generate')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        # Clear all initial parenting
        for bone in self.org_bones:
            eb[ bone ].parent      = None
            eb[ bone ].use_connect = False
        # will be "reparented" by self.parent_bones(), see below
        # Creating all bones
        mch_chain   = self.make_mechanics()
        ctrl_chain  = self.make_controls()
        tweak_chain = self.make_tweaks(mch_chain)
        def_chain   = self.make_deform(mch_chain)
        # join in dictionary
        all_bones = {
              'mch'     : mch_chain
            , 'control' : ctrl_chain
            , 'tweak'   : tweak_chain
            , 'deform'  : def_chain
        }
        # reorganize dependencies
        self.make_constraints(all_bones)
        self.parent_bones(all_bones)
        # if needed return a script addition for rig_ui.py
        # and out

def add_parameters(params):
    """ Add the parameters of this rig type to the
        RigifyParameters PropertyGroup
    """
    # not needed in this construct
    #params.copy_rotation_axes = bpy.props.BoolVectorProperty(
    #    size=3,
    #    description="Automation axes",
    #    default=tuple([i == 0 for i in range(0, 3)])
    #    )
    # param guide_in bone, defaulted to parent of shaft
    # shaft is carrying the Rig property
    params.sizing_bone = bpy.props.StringProperty(
        name = 'sizing_bone',
        default = 'ring_sizer',
        description = "placement for size control"
        )
    # number of stretchy elements
    params.wing_elements = bpy.props.IntProperty(
        name        = 'wing_elements',
        default     = 3,
        min         = 1,
        description = 'Number of elements on 1 side of ring'
    )
    # no tweak bone set yet, maybe in future
    ## Setting up extra tweak layers
    ## do extra layer for tweaks
    #params.tweak_extra_layers = bpy.props.BoolProperty(
    #    name        = "tweak_extra_layers",
    #    default     = True,
    #    description = ""
    #    )
    ## the extra layer for tweaks
    #params.tweak_layers = bpy.props.BoolVectorProperty(
    #    size        = 32,
    #    description = "Layers for the tweak controls to be on",
    #    default     = tuple( [ i == 1 for i in range(0, 32) ] )
    #    )


def parameters_ui(layout, params):
    """ Create the ui for the rig parameters.
    """

    pb = bpy.context.object.pose
    # not needed in this construct
    #r = layout.row()
    #col = r.column(align=True)
    #row = col.row(align=True)
    #for i, axis in enumerate(['x', 'y', 'z']):
    #    row.prop(params, "copy_rotation_axes", index=i, toggle=True, text=axis)
    # param guide_in bone
    r = layout.row()
    r.prop_search(params, 'sizing_bone', pb, "bones", text="Size control")
    # param boolean deform guide_in
    # number of stretchy elements
    r = layout.row()
    r.prop(params, "wing_elements", text="Number elements in ring half")
    # no tweak bone set yet, maybe in future
    ## do extra layer for tweaks
    #r = layout.row()
    #r.prop(params, "tweak_extra_layers", text="Tweak extra")
    #r.active = params.tweak_extra_layers
    ## the extra layer for tweaks
    #col = r.column(align=True)
    #row = col.row(align=True)
    #bone_layers = bpy.context.active_pose_bone.bone.layers[:]
    #for i in range(8):    # Layers 0-7
    #    icon = "NONE"
    #    if bone_layers[i]:
    #        icon = "LAYER_ACTIVE"
    #    row.prop(params, "tweak_layers", index=i, toggle=True, text="", icon=icon)
    #row = col.row(align=True)
    #for i in range(16, 24):     # Layers 16-23
    #    icon = "NONE"
    #    if bone_layers[i]:
    #        icon = "LAYER_ACTIVE"
    #    row.prop(params, "tweak_layers", index=i, toggle=True, text="", icon=icon)
    ## 2nd row for the extra layer for tweaks
    #col = r.column(align=True)
    #row = col.row(align=True)
    #for i in range(8, 16):  # Layers 8-15
    #    icon = "NONE"
    #    if bone_layers[i]:
    #        icon = "LAYER_ACTIVE"
    #    row.prop(params, "tweak_layers", index=i, toggle=True, text="", icon=icon)
    #row = col.row(align=True)
    #for i in range( 24, 32 ): # Layers 24-31
    #    icon = "NONE"
    #    if bone_layers[i]:
    #        icon = "LAYER_ACTIVE"
    #    row.prop(params, "tweak_layers", index=i, toggle=True, text="", icon=icon)


def create_sample(obj):
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('ring_radius')
    bone.head[:] = 0.0000, 0.0000, 1.0000
    bone.tail[:] = 1.0000, 0.0000, 1.0000
    bone.roll = 1.5708
    bone.use_connect = False
    bones['ring_radius'] = bone.name
    bone = arm.edit_bones.new('ring_sizer')
    bone.head[:] = 0.0000, 0.0000, 1.0000
    bone.tail[:] = 0.0000, 0.0000, 2.0000
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['ring_radius']]
    bones['ring_sizer'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['ring_radius']]
    pbone.rigify_type = 'experimental.super_ring'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    try:
        pbone.rigify_parameters.sizing_bone = "ring_sizer"
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['ring_sizer']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'

    bpy.ops.object.mode_set(mode='EDIT')
    for bone in arm.edit_bones:
        bone.select = False
        bone.select_head = False
        bone.select_tail = False
    for b in bones:
        bone = arm.edit_bones[bones[b]]
        bone.select = True
        bone.select_head = True
        bone.select_tail = True
        arm.edit_bones.active = bone
