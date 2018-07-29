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
# super_stretcher:
# A guide_in bone being the parent of a shaft bone, itself being parent to the
# guide_out bone. These will result in the ORG-bones copied by rigify.
# -> ORG-guide_out will be reparented to ORG-guide_in without connect
# -> ORG-shaft will have a Stretch To-modifier to guide_out
# -> dependencies description:
# -+ guide_in (root of construct, ctrl, excluded, if not needed as ctrl)
#  +-+ ORG-guide_in (ORG, in case guide_in not needed, root)
#    +-+ guide_out
#    | +-+ ORG-guide_out
#    |   +-- DEF-guide_out
#    |
#    +-+ ORG-shaft (Stretch to guide_out)
#    | |
#    | +-+ shaft_tweak.001
#    | | +-- DEF-shaft.002 (Stretch to shaft_tweak.002)
#    | |
#    | +-+ shaft_tweak.002
#    |   +-- DEF-shaft.003 (Stretch to guide_out)
#    |
#    +-- DEF-shaft.001 (Stretch to shaft_tweak.001)
#
# -> ORG_bones already made by rigify
# -> generate guide_out
# -> generate guide_in (if needed)
# -> generate tweaks
# -> generate deform
# -> refine constraints
# -> provide locks
# -> parent up the tree
#
# -> it is a good idea to keep your bone lists consistent
#    with the parenting order, then it is easier to parent the bones
#    by looping the bone lists
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
        print('!!!WIP!!! super_template on %s' % bone_name)
        # stretch_bone is the main element of this system
        self.stretch_bone = bone_name
        # just in case we have a suffix
        # (L = Left, R = Right, F = Front, B = Back, U = to Up above, D = to Down below)
        self.suffix = ''
        if bone_name[-2].upper() in ['.L','.R','.F','.B','.U','.D']:
            self.suffix = bone_name[-2]
        # this list may be modified by head or tail params
        self.org_bones = []
        # + bone_name.parent
        #print('super_template params.guide_in_bone %s' % params.guide_in_bone)
        if params.guide_in_bone:
            self.org_bones += [org(params.guide_in_bone)]
        self.org_bones += [bone_name] + connected_children_names(obj, bone_name)
        self.params = params
        # in principle do a copy of the add_parameters method
        # and assign params properties to "self"-properties
        # not in this context
        #self.copy_rotation_axes = params.copy_rotation_axes
        # param guide_in bone, defaulted to parent of shaft
        # shaft is carrying the Rig property
        self.guide_in_bone = params.guide_in_bone
        # param boolean deform guide_in
        self.guide_in_deform = params.guide_in_deform
        # param boolean control guide_in
        self.guide_in_control = params.guide_in_control
        # param guide_out bone, defaulted to first child of shaft
        self.guide_out_bone = params.guide_out_bone
        # param boolean deform guide_out
        self.guide_out_deform = params.guide_out_deform
        # number of stretchy elements
        self.bbone_elements = params.bbone_elements
        # number of segments in the stretch elements
        self.bbone_segments = params.bbone_segments
        # tweaks on extra layer ?
        if params.tweak_extra_layers:
            self.tweak_layers = list(params.tweak_layers)
        else:
            self.tweak_layers = None
        # construct must have 3 bones: guide_in, shaft, guide_out
        if len(self.org_bones) != 3:
            raise MetarigError(
                "RIGIFY ERROR: invalid rig structure on bone: %s (%d bones)" % (strip_org(bone_name),len(self.org_bones))
            )

    def make_mechanics(self):

        # construct mechanics of the bone system
        # i.e. for tweaking the stretch route
        print('super_template.make_mechanics')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        #org_bones = self.org_bones
        mch_chain = []
        # start by copying the stretch_bone in elements
        for ix in range(self.bbone_elements):
            mch_name = mch(strip_org(self.stretch_bone) + (".%03d" % ix) + self.suffix)
            print('super_template.make_mechanics make %03d %s' % (ix, mch_name) )
            mch_name = copy_bone_simple( self.obj, self.stretch_bone, mch_name)
            eb[ mch_name ].length /= self.bbone_elements
            if ix > 0:
                put_bone(self.obj, mch_name,  eb[ mch_chain[-1] ].tail)
            mch_chain += [ mch_name ]
        # and out
        return mch_chain

    def make_controls(self):

        # Just a control for the guide_out,
        # but keep structure to build more complex control sets
        print('super_template.make_controls')
        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones
        ctrl_chain = []
        # having a control to every bone is not needed in this system
        #for i in range( len( org_bones ) ):
        #    name = org_bones[i]
        #    ctrl_bone  = copy_bone(
        #        self.obj,
        #        name,
        #        strip_org(name)
        #    )
        #    ctrl_chain.append( ctrl_bone )
        # dedicated controls for guide_in (if guide_in_control) and guide_out
        # guide_in
        if self.guide_in_control:
            name = org_bones[0]
            ctrl_bone = copy_bone(self.obj,name,strip_org(name))
            ctrl_chain.append(ctrl_bone)
        # guide_out
        name = org_bones[2]
        ctrl_bone = copy_bone(self.obj,name,strip_org(name))
        ctrl_chain.append(ctrl_bone)
        # Make widgets
        bpy.ops.object.mode_set(mode ='OBJECT')
        for ctrl in ctrl_chain:
            create_circle_widget(self.obj, ctrl, radius=0.5, head_tail=0.5)
        return ctrl_chain

    def make_tweaks(self, mch_chain):

        # the tweaks itself are the shaped bones
        # controlling the mechanics in the bone system
        print('super_template.make_tweaks')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        tweak_chain = []
        # in this case we don't organize tweaks by the ORGs
        # but by the earlier created MCHs
        # the mch_chain has to be parameter for this
        #org_bones = self.org_bones
        #for i in range( len( org_bones ) + 1 ):
        #    if i == len( org_bones ):
        #        # Make final tweak at the tip of the tentacle
        #        name = org_bones[i-1]
        #    else:
        #        name = org_bones[i]
        #    tweak_bone = copy_bone(
        #        self.obj,
        #        name,
        #        "tweak_" + strip_org(name)
        #    )
        #    tweak_e = eb[ tweak_bone ]
        #    tweak_e.length /= 2 # Set size to half
        #    if i == len( org_bones ):
        #        # Position final tweak at the tip
        #        put_bone( self.obj, tweak_bone, eb[ org_bones[-1]].tail )
        #    tweak_chain.append( tweak_bone )
        # for over index because 1st is left out
        for ix in range( len( mch_chain)):
            if ix > 0:
                tweak_name = strip_mch(mch_chain[ix])
                tweak_bone = copy_bone(self.obj,mch_chain[ix],tweak_name)
                tweak_chain.append(tweak_bone)
                eb[ tweak_bone ].length /= 4
        # Make widgets
        bpy.ops.object.mode_set(mode = 'OBJECT')
        for tweak in tweak_chain:
            create_sphere_widget( self.obj, tweak )
            tweak_pb = self.obj.pose.bones[ tweak ]
            # Set locks
            # different locking not needed in this system
            #if tweak_chain.index( tweak ) != len( tweak_chain ) - 1:
            tweak_pb.lock_rotation = (True, False, True)
            tweak_pb.lock_scale    = (False, True, False)
            #else:
            #    tweak_pb.lock_rotation_w = True
            #    tweak_pb.lock_rotation   = (True, True, True)
            #    tweak_pb.lock_scale      = (True, True, True)
            # Set up tweak bone layers
            if self.tweak_layers:
                tweak_pb.bone.layers = self.tweak_layers
        # and out
        return tweak_chain

    def make_deform(self, mch_chain):

        # make the finally deforming skeleton meshes are rigged to
        print('super_template.make_deform')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        def_chain = []
        org_bones = self.org_bones
        # deforms in this system by guide_in, guide_out & mch_chain
        #for i in range( len( org_bones ) ):
        #    name = org_bones[i]
        #    def_bone  = copy_bone(
        #        self.obj,
        #        name,
        #        make_deformer_name(strip_org(name))
        #    )
        #    def_chain.append( def_bone )
        # should guide_in be a deform
        if self.guide_in_deform:
            def_name = make_deformer_name(strip_org(self.guide_in_bone))
            def_bone = copy_bone(self.obj, org(self.guide_in_bone), def_name)
            def_chain.append(def_bone)
        # iterate mch_chain
        for ix in range( len( mch_chain)):
            def_name = make_deformer_name(strip_mch(mch_chain[ix]))
            def_bone = copy_bone(self.obj,mch_chain[ix], def_name)
            # set segments
            eb[def_bone].bbone_segments = self.bbone_segments
            def_chain.append(def_bone)
        # should guide_out be a deform
        if self.guide_out_deform:
            def_name = make_deformer_name(strip_org(self.guide_out_bone))
            def_bone = copy_bone(self.obj, org(self.guide_out_bone), def_name)
            def_chain.append(def_bone)
        # and out
        return def_chain

    def parent_bones(self, all_bones):

        # give the parenting to the constructed bone system
        print('super_template.parent_bones')
        # test if above works out
        #return
        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones
        eb        = self.obj.data.edit_bones

        # -+ guide_in (root of construct, ctrl, excluded, if not needed as ctrl)
        #  +-+ ORG-guide_in (ORG, in case guide_in not needed, root)
        #    +-+ guide_out
        #    | +-+ ORG-guide_out
        #    |   +-- DEF-guide_out
        #    |
        #    +-+ ORG-shaft (Stretch to guide_out)
        #    | |
        #    | +-+ shaft_tweak.001
        #    | | +-- DEF-shaft.002 (Stretch to shaft_tweak.002)
        #    | |
        #    | +-+ shaft_tweak.002
        #    |   +-- DEF-shaft.003 (Stretch to guide_out)
        #    |
        #    +-- DEF-shaft.001 (Stretch to shaft_tweak.001)

        # Parent control bones
        # example of chaining the controls, not needed in this system
        #for bone in all_bones['control'][1:]:
        #    previous_index    = all_bones['control'].index( bone ) - 1
        #    eb[ bone ].parent = eb[ all_bones['control'][previous_index] ]
        if self.guide_in_control:
            # guide_out control is 2nd
            print('super_template.parent_bones parent %s to %s' % (all_bones['control'][1],org_bones[0]))
            eb[all_bones['control'][1]].parent = eb[org_bones[0]]
        else:
            print('super_template.parent_bones parent %s to %s' % (all_bones['control'][0],org_bones[0]))
            eb[all_bones['control'][0]].parent = eb[org_bones[0]]

        # Parent tweak bones
        tweaks = all_bones['tweak']
        for tweak in all_bones['tweak']:
            # are all parented to the stretch_bone
            # example of parenting to controls
            #parent = ''
            #if tweaks.index( tweak ) == len( tweaks ) - 1:
            #    parent = all_bones['control'][ -1 ]
            #else:
            #    parent = all_bones['control'][ tweaks.index( tweak ) ]
            #eb[ tweak ].parent = eb[ parent ]
            print('super_template.parent_bones parent %s to %s' % (tweak,self.stretch_bone))
            eb[ tweak ].parent = eb[ self.stretch_bone ]

        # Parent mechanics bones
        # the 1st to ORG-guide_in
        mechs = all_bones['mch']
        print('super_template.parent_bones parent %s to %s' % (mechs[0],org_bones[0]))
        eb[mechs[0]].parent = eb[org_bones[0]]
        # all other to their tweaks
        for mch in mechs[1:]:
            print('super_template.parent_bones parent %s to %s' % (mch,strip_mch(mch)))
            eb[mch].parent = eb[strip_mch(mch)]

        # Parent deform bones
        def_bones = all_bones['deform']
        ixfrom = 1
        if self.guide_in_deform:
            print('super_template.parent_bones parent %s to %s' % (def_bones[0],org_bones[0]))
            eb[def_bones[0]].parent = eb[org_bones[0]]
            ixfrom += 1
        ixto = len(def_bones)
        if self.guide_out_deform:
            print('super_template.parent_bones parent %s to %s' % (def_bones[-1],org_bones[-1]))
            eb[def_bones[-1]].parent = eb[org_bones[-1]]
            ixto -= 1
        # parent the deforms to the corresponding mchs
        for bone in all_bones['deform'][ixfrom:ixto]:
            if self.guide_in_deform:
                mch_index = all_bones['deform'].index( bone ) - 1
            else:
                mch_index = all_bones['deform'].index( bone )
            print('super_template.parent_bones parent %s to %s' % (bone,all_bones['mch'][mch_index]))
            eb[ bone ].parent = eb[ all_bones['mch'][mch_index] ]
            #eb[ bone ].use_connect = True

        # Parent org bones ( to tweaks by default, or to the controls )
        # not needed for this system
        #for org, tweak in zip( org_bones, all_bones['tweak'] ):
        #    eb[ org ].parent = eb[ tweak ]
        # if there is a guide_in-Control, this will be parent of the ORG-guide_in
        # else the ORG-guide_in is root to the system
        if self.guide_in_control:
            print('super_template.parent_bones parent %s to %s' % (org_bones[0],all_bones['control'][0]))
            eb[ org_bones[0]].parent = eb[all_bones['control'][0]]
        if self.guide_in_bone:
            print('super_template.parent_bones parent %s to %s' % (org_bones[1],org_bones[0]))
            eb[ org_bones[1]].parent = eb[org_bones[0]]
            print('super_template.parent_bones parent %s to %s' % (org_bones[2],all_bones['control'][-1]))
            eb[ org_bones[2]].parent = eb[all_bones['control'][-1]]
        else:
            print('super_template.parent_bones parent %s to %s' % (org_bones[1],all_bones['control'][-1]))
            eb[ org_bones[1]].parent = eb[all_bones['control'][-1]]
        # and out

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
        print('super_template.make_constraints')
        # test if above works out
        #return
        bpy.ops.object.mode_set(mode ='OBJECT')
        org_bones = self.org_bones
        pb        = self.obj.pose.bones
        # Deform bones' constraints
        ctrls   = all_bones['control']
        tweaks  = all_bones['tweak'  ]
        deforms = all_bones['deform' ]
        # example for looping constraints through a chain
        #for deform, tweak, ctrl in zip( deforms, tweaks, ctrls ):
        #    # copy transform
        #    con           = pb[deform].constraints.new('COPY_TRANSFORMS')
        #    con.target    = self.obj
        #    con.subtarget = tweak
        #    # damped track
        #    con           = pb[deform].constraints.new('DAMPED_TRACK')
        #    con.target    = self.obj
        #    con.subtarget = tweaks[ tweaks.index( tweak ) + 1 ]
        #    # stretch to
        #    con           = pb[deform].constraints.new('STRETCH_TO')
        #    con.target    = self.obj
        #    con.subtarget = tweaks[ tweaks.index( tweak ) + 1 ]
        #    # Control bones' constraints
        #    if ctrl != ctrls[0]:
        #        con = pb[ctrl].constraints.new('COPY_ROTATION')
        #        con.target = self.obj
        #        con.subtarget = ctrls[ctrls.index(ctrl) - 1]
        #        for i, prop in enumerate(['use_x', 'use_y', 'use_z']):
        #            if self.copy_rotation_axes[i]:
        #                setattr(con, prop, True)
        #            else:
        #                setattr(con, prop, False)
        #        con.use_offset = True
        #        con.target_space = 'LOCAL'
        #        con.owner_space = 'LOCAL'
        # STRETCH_TO for ORG-shaft (displaces the parented tweaks accordingly)
        if self.guide_in_bone:
            print('super_template.make_constraints %s stretch_to %s' % (org_bones[1],org_bones[2]))
            con = pb[org_bones[1]].constraints.new('STRETCH_TO')
            con.target = self.obj
            con.subtarget = org_bones[2]
        else:
            print('super_template.make_constraints %s stretch_to %s' % (org_bones[0],org_bones[1]))
            con = pb[org_bones[0]].constraints.new('STRETCH_TO')
            con.target = self.obj
            con.subtarget = org_bones[1]
        ixfrom = (1 if self.guide_in_deform else 0)
        for deform in deforms[ixfrom:-1]:
            target_bone = deforms[ deforms.index( deform ) + 1 ]
            print('super_template.make_constraints %s stretch_to %s' % (deform,target_bone))
            con = pb[deform].constraints.new('STRETCH_TO')
            con.target = self.obj
            con.subtarget = target_bone
            # these are also our bendy bones system
            pb[deform].use_bbone_custom_handles = True
            if deforms.index( deform ) > 0:
                from_bone = deforms[ deforms.index( deform ) - 1 ]
                print('super_template.make_constraints %s handle_in %s' % (deform,from_bone))
                pb[deform].bbone_custom_handle_start = pb[from_bone]
            print('super_template.make_constraints %s handle_out %s' % (deform,target_bone))
            pb[deform].bbone_custom_handle_end = pb[target_bone]
        if not self.guide_out_deform:
            print('super_template.make_constraints %s stretch_to %s' % (deforms[-1],org_bones[-1]))
            con = pb[deforms[-1]].constraints.new('STRETCH_TO')
            con.target = self.obj
            con.subtarget = org_bones[-1]
        # and out


    def generate(self):

        # main generation method
        print('super_template.generate')
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
    params.guide_in_bone = bpy.props.StringProperty(
        name = 'guide_in_bone',
        default = 'guide_in',
        description = "guide_in bone for bendy shaft"
        )
    # param boolean deform guide_in
    params.guide_in_deform = bpy.props.BoolProperty(
        name        = "guide_in_deform",
        default     = True,
        description = "If there should be a deform for guide_in"
        )
    # param boolean control guide_in
    params.guide_in_control = bpy.props.BoolProperty(
        name        = "guide_in_control",
        default     = True,
        description = "If there should be a control for guide_in"
        )
    # param guide_out bone, defaulted to first child of shaft
    params.guide_out_bone = bpy.props.StringProperty(
        name = 'guide_out_bone',
        default = 'guide_out',
        description = "guide_out bone for bendy shaft (usually control)"
        )
    # param boolean deform guide_out
    params.guide_out_deform = bpy.props.BoolProperty(
        name        = "guide_out_deform",
        default     = True,
        description = "If there should be a deform for guide_out"
        )
    # number of stretchy elements
    params.bbone_elements = bpy.props.IntProperty(
        name        = 'bbone elements',
        default     = 3,
        min         = 1,
        description = 'Number of stretchy elements'
    )
    # number of segments in the stretch elements
    params.bbone_segments = bpy.props.IntProperty(
        name        = 'bbone segments',
        default     = 5,
        min         = 1,
        description = 'Number of segments in bendies'
    )
    # Setting up extra tweak layers
    # do extra layer for tweaks
    params.tweak_extra_layers = bpy.props.BoolProperty(
        name        = "tweak_extra_layers",
        default     = True,
        description = ""
        )
    # the extra layer for tweaks
    params.tweak_layers = bpy.props.BoolVectorProperty(
        size        = 32,
        description = "Layers for the tweak controls to be on",
        default     = tuple( [ i == 1 for i in range(0, 32) ] )
        )


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
    r.prop_search(params, 'guide_in_bone', pb, "bones", text="Guide in bone")
    # param boolean deform guide_in
    r = layout.row()
    r.prop(params, "guide_in_deform", text="Guide in deform")
    # param boolean control guide_in
    r = layout.row()
    r.prop(params, "guide_in_control", text="Guide in control")
    # param guide_out bone
    r = layout.row()
    r.prop_search(params, 'guide_out_bone', pb, "bones", text="Guide out bone")
    # param boolean deform guide_out
    r = layout.row()
    r.prop(params, "guide_out_deform", text="Guide out deform")
    # number of stretchy elements
    r = layout.row()
    r.prop(params, "bbone_elements", text="Number stretchy elements")
    # number of segments in the stretch elements
    r = layout.row()
    r.prop(params, "bbone_segments", text="Number segments in bendies")
    # do extra layer for tweaks
    r = layout.row()
    r.prop(params, "tweak_extra_layers", text="Tweak extra")
    r.active = params.tweak_extra_layers
    # the extra layer for tweaks
    col = r.column(align=True)
    row = col.row(align=True)

    bone_layers = bpy.context.active_pose_bone.bone.layers[:]

    for i in range(8):    # Layers 0-7
        icon = "NONE"
        if bone_layers[i]:
            icon = "LAYER_ACTIVE"
        row.prop(params, "tweak_layers", index=i, toggle=True, text="", icon=icon)

    row = col.row(align=True)

    for i in range(16, 24):     # Layers 16-23
        icon = "NONE"
        if bone_layers[i]:
            icon = "LAYER_ACTIVE"
        row.prop(params, "tweak_layers", index=i, toggle=True, text="", icon=icon)

    # 2nd row for the extra layer for tweaks
    col = r.column(align=True)
    row = col.row(align=True)

    for i in range(8, 16):  # Layers 8-15
        icon = "NONE"
        if bone_layers[i]:
            icon = "LAYER_ACTIVE"
        row.prop(params, "tweak_layers", index=i, toggle=True, text="", icon=icon)

    row = col.row(align=True)

    for i in range( 24, 32 ): # Layers 24-31
        icon = "NONE"
        if bone_layers[i]:
            icon = "LAYER_ACTIVE"
        row.prop(params, "tweak_layers", index=i, toggle=True, text="", icon=icon)


def create_sample(obj):
    # to be ...
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('guide_in')
    bone.head[:] = 0.0000, 0.0000, 0.0000
    bone.tail[:] = 0.0000, 0.0000, 1.0000
    bone.roll = 0.0000
    bone.use_connect = False
    bones['guide_in'] = bone.name
    bone = arm.edit_bones.new('shaft')
    bone.head[:] = 0.0000, 0.0000, 1.0000
    bone.tail[:] = 0.0000, 0.0000, 4.0000
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['guide_in']]
    bones['shaft'] = bone.name
    bone = arm.edit_bones.new('guide_out')
    bone.head[:] = 0.0000, 0.0000, 4.0000
    bone.tail[:] = 0.0000, 0.0000, 5.0000
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['shaft']]
    bones['guide_out'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['guide_in']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['shaft']]
    pbone.rigify_type = 'experimental.super_template'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['guide_out']]
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
