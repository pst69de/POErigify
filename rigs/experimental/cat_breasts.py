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
# based on less_template.py
# sample container for a futanari crotch
# feel free to reuse on your own project
#
###############################
import bpy
from ...utils import copy_bone, copy_bone_simple, put_bone
from ...utils import org, strip_org, mch, strip_mch
from ...utils import make_deformer_name, connected_children_names
from ...utils import make_mechanism_name, create_sphere_widget
from ...utils import create_widget, create_circle_widget
from ...utils import MetarigError
from rna_prop_ui import rna_idprop_ui_prop_get


class Rig:

    def __init__(self, obj, bone_name, params):
        # constructor for this class, in here the local parameters are defined
        self.obj = obj
        print('!!!WIP!!! cat_breasts on %s' % bone_name)
        # stretch_bone is the main element of this system
        self.bone_name = bone_name
        # just in case we have a suffix
        # (L = Left, R = Right, F = Front, B = Back, U = to Up above, D = to Down below)
        self.suffix = ''
        if bone_name[-2].upper() in ['.L','.R','.F','.B','.U','.D']:
            self.suffix = bone_name[-2]
        # this list may be modified by head or tail params
        self.org_bones = [bone_name]
        self.params = params
        # construct must have 1 bone
        if len(self.org_bones) != 1:
            raise MetarigError(
                "RIGIFY ERROR: invalid rig structure on bone: %s (%d bones)" % (strip_org(bone_name),len(self.org_bones))
            )

    def make_mechanics(self):

        # construct mechanics of the bone system
        # i.e. for tweaking the stretch route
        print('cat_breasts.make_mechanics -> no mechanis')
        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones
        eb = self.obj.data.edit_bones
        mechs = []
        # and out
        return mechs

    def make_controls(self):

        # Just a control for ...
        print('cat_breasts.make_controls -> no controls')
        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones
        eb = self.obj.data.edit_bones
        ctrls = []
        # and out
        return ctrls

    def make_tweaks(self):

        # the tweaks itself are the shaped bones
        # controlling the deforms in the bone system
        # and usually are controlled by mechs
        print('cat_breasts.make_tweaks -> no tweaks')
        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones
        eb = self.obj.data.edit_bones
        tweaks = []
        # and out
        return tweaks

    def make_deform(self):

        # make the finally deforming skeleton meshes are rigged to
        print('cat_breasts.make_deform -> no deform')
        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones
        eb = self.obj.data.edit_bones
        deforms = []
        # and out
        return deforms

    # helper for making constraints
    def make_constraint(self, bone, constraint):
        bpy.ops.object.mode_set(mode='OBJECT')
        pb = self.obj.pose.bones

        owner_pb = pb[bone]
        const = owner_pb.constraints.new(constraint['constraint'])
        constraint['target'] = self.obj

        # filter contraint props to those that actually exist in the current
        # type of constraint, then assign values to each
        for p in [k for k in constraint.keys() if k in dir(const)]:
            setattr(const, p, constraint[p])

    def make_constraints(self, all_bones):

        # make the needed constrainting modifiers to the bone system
        print('cat_breasts.make_constraints -> no constraints')
        # test if above works out
        #return
        bpy.ops.object.mode_set(mode ='OBJECT')
        org_bones = self.org_bones
        pb        = self.obj.pose.bones
        # Deform bones' constraints
        ctrls   = all_bones['control']
        tweaks  = all_bones['tweak'  ]
        deforms = all_bones['deform' ]
        # this routine solely is acting in Pose space
        # and out


    def parent_bones(self, all_bones):

        # give the parenting to the constructed bone system
        print('cat_breasts.parent_bones -> no parenting')
        # test if above works out
        #return
        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones
        eb        = self.obj.data.edit_bones
        # and out

    def generate(self):

        # main generation method
        print('cat_breasts.generate')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        # if needed clear all initial parenting
        #for bone in self.org_bones:
        #    eb[ bone ].parent      = None
        #    eb[ bone ].use_connect = False
        # will be "reparented" by self.parent_bones(), see below
        # Creating all bones
        mechs   = self.make_mechanics()
        ctrls   = self.make_controls()
        tweaks  = self.make_tweaks(mch_chain)
        deforms = self.make_deform(mch_chain)
        # join in dictionary
        all_bones = {
              'mch'     : mechs
            , 'control' : ctrls
            , 'tweak'   : tweaks
            , 'deform'  : deforms
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
    # param boolean
    params.boolean_prop = bpy.props.BoolProperty(
        name        = "boolean_prop",
        default     = True,
        description = "Boolean"
        )
    # param bone
    params.bone_prop = bpy.props.StringProperty(
        name = 'bone_prop',
        default = '',
        description = "Bone String"
        )
    # and out


def parameters_ui(layout, params):
    """ Create the ui for the rig parameters.
    """

    pb = bpy.context.object.pose
    # param boolean
    r = layout.row()
    r.prop(params, "boolean_prop", text="Boolean")
    # param bone
    r = layout.row()
    r.prop_search(params, 'bone_prop', pb, "bones", text="Bone String")
    # and out


def create_sample(obj):
    # to be ...
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('breast.L')
    bone.head[:] = 0.0740, -0.1431, 1.2355
    bone.tail[:] = 0.1083, -0.2387, 1.2106
    bone.roll = 1.2718
    bone.use_connect = False
    bones['breast.L'] = bone.name
    bone = arm.edit_bones.new('breast.R')
    bone.head[:] = -0.0740, -0.1431, 1.2355
    bone.tail[:] = -0.1083, -0.2387, 1.2106
    bone.roll = -1.2718
    bone.use_connect = False
    bones['breast.R'] = bone.name
    bone = arm.edit_bones.new('breast.001.L')
    bone.head[:] = 0.0568, -0.1500, 1.1774
    bone.tail[:] = 0.0787, -0.1935, 1.1319
    bone.roll = 1.9218
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['breast.L']]
    bones['breast.001.L'] = bone.name
    bone = arm.edit_bones.new('nipple.L')
    bone.head[:] = 0.1083, -0.2387, 1.2106
    bone.tail[:] = 0.1175, -0.2625, 1.2199
    bone.roll = -1.5136
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['breast.L']]
    bones['nipple.L'] = bone.name
    bone = arm.edit_bones.new('breast.002.L')
    bone.head[:] = 0.1271, -0.1040, 1.2243
    bone.tail[:] = 0.1554, -0.1627, 1.1710
    bone.roll = 1.6893
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['breast.L']]
    bones['breast.002.L'] = bone.name
    bone = arm.edit_bones.new('breast.003.L')
    bone.head[:] = 0.0766, -0.1067, 1.3461
    bone.tail[:] = 0.0830, -0.1669, 1.2936
    bone.roll = 2.0224
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['breast.L']]
    bones['breast.003.L'] = bone.name
    bone = arm.edit_bones.new('breast.004.L')
    bone.head[:] = 0.0054, -0.1746, 1.2329
    bone.tail[:] = 0.0364, -0.2173, 1.1596
    bone.roll = 2.0224
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['breast.L']]
    bones['breast.004.L'] = bone.name
    bone = arm.edit_bones.new('nipple.R')
    bone.head[:] = -0.1083, -0.2387, 1.2106
    bone.tail[:] = -0.1175, -0.2625, 1.2199
    bone.roll = 1.5136
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['breast.R']]
    bones['nipple.R'] = bone.name
    bone = arm.edit_bones.new('breast.001.R')
    bone.head[:] = -0.0568, -0.1500, 1.1774
    bone.tail[:] = -0.0787, -0.1935, 1.1319
    bone.roll = -1.9218
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['breast.R']]
    bones['breast.001.R'] = bone.name
    bone = arm.edit_bones.new('breast.002.R')
    bone.head[:] = -0.1271, -0.1040, 1.2243
    bone.tail[:] = -0.1554, -0.1627, 1.1710
    bone.roll = -1.6893
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['breast.R']]
    bones['breast.002.R'] = bone.name
    bone = arm.edit_bones.new('breast.003.R')
    bone.head[:] = -0.0766, -0.1067, 1.3461
    bone.tail[:] = -0.0830, -0.1669, 1.2936
    bone.roll = -2.0224
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['breast.R']]
    bones['breast.003.R'] = bone.name
    bone = arm.edit_bones.new('breast.004.R')
    bone.head[:] = -0.0054, -0.1746, 1.2329
    bone.tail[:] = -0.0364, -0.2173, 1.1596
    bone.roll = -2.0224
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['breast.R']]
    bones['breast.004.R'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['breast.L']]
    pbone.rigify_type = 'experimental.super_dome'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    try:
        pbone.rigify_parameters.tweak_layers = [False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.base_bone = "spine.003"
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['breast.R']]
    pbone.rigify_type = 'experimental.super_dome'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    try:
        pbone.rigify_parameters.tweak_layers = [False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.base_bone = "spine.003"
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['breast.001.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['nipple.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['breast.002.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['breast.003.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['breast.004.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['nipple.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['breast.001.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['breast.002.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['breast.003.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['breast.004.R']]
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
