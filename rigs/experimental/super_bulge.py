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
# super_bulge rig class
# by Patrick O. Ehrmann
# based on super_template.py
# feel free to reuse on your own project
#
# super_bulge is rig system to do a wobbly bulge on a fixed base
# in opposite to super_dome this uses bendy bones to follow the
# the movement of the top, keeping the basement fixed
#
# if there is a connected child named like ctr... or ctl...
# this becomes template of main Control and is taken off the
# list of ORG_bones
#
# -> needs a parent bone to fix the border to
# -> connected children are animatable on there own (normally one)
# -> unconnected children define the bordering base (and are reparanted to the base)
#
# -> it is a good idea to keep your bone lists consistent
#    with the parenting order, then it is easier to parent the bones
#    by looping the bone lists
###############################
import bpy
from ...utils import copy_bone, copy_bone_simple, put_bone
from ...utils import org, strip_org, mch, strip_mch, deformer
from ...utils import connected_children_names
from ...utils import create_dome_widget
from ...utils import create_bone_widget
from ...utils import MetarigError
from rna_prop_ui import rna_idprop_ui_prop_get

class Rig:

    def __init__(self, obj, bone_name, params):
        # constructor for this class, in here the local parameters are defined
        self.obj = obj
        print('!!!WIP!!! super_bulge on %s' % bone_name)
        # have the params with us
        self.params = params
        # just in case we have a suffix (not really watched for at time)
        # (L = Left, R = Right, F = Front, B = Back, U = to Up above, D = to Down below)
        self.suffix = ''
        if bone_name[-2].upper() in ['.L','.R','.F','.B','.U','.D']:
            self.suffix = bone_name[-2]
        eb = obj.data.edit_bones
        # base_bone is the main element of this system
        if eb[bone_name].parent:
            print('super_bulge %s parent is %s' % (bone_name,eb[bone_name].parent.name))
            self.base_bone = eb[bone_name].parent.name
        else:
            print('super_bulge %s has no parent' % bone_name)
            self.base_bone = None
        if params.base_bone:
            self.base_bone = org(params.base_bone)
            print('super_bulge %s changed parent %s' % (bone_name,self.base_bone))
        # org_bones[0] = dome_bone
        self.org_bones = [bone_name]
        # org_bones[1] = child (yet to assume only one)
        self.ctrl_bone = None
        con_children = self.collect_connected_children_names(bone_name)
        for con_name in con_children:
            print('super_bulge connected child %s' % con_name)
            if strip_org(con_name)[:3].upper() in ['CON','CTR','CTL']:
                print('super_bulge ctrl_bone %s' % con_name)
                self.ctrl_bone = con_name
        if self.ctrl_bone:
            print('super_bulge remove ctrl_bone %s' % self.ctrl_bone)
            con_children.remove(self.ctrl_bone)
        self.org_bones += con_children
        for bname in self.org_bones:
            print('super_bulge org_bones w/o border %s' % bname)
        self.ofs_border = len(con_children) + 1
        print('super_bulge ofs_border %d' % self.ofs_border)
        # org_bones[2:] add border bones
        unc_children = self.collect_uncon_children_names(bone_name)
        #print( 'super_bulge %d unconnected children' % len(unc_children))
        #for child in unc_children:
        #    print( 'super_bulge unconnected child %s' % child)
        self.org_bones += unc_children
        print('super_bulge len org_bones %d' % len(self.org_bones))
        # number of segments in the stretch elements
        self.bbone_segments = params.bbone_segments
        # create bones to help adjust roll of bones
        self.zhelper_bones = params.zhelper_bones
        # tweaks on extra layer ?
        if params.tweak_extra_layers:
            self.tweak_layers = list(params.tweak_layers)
        else:
            self.tweak_layers = None
        # construct should have at least 3 bones
        if len(self.org_bones) < 3 or not self.base_bone:
            raise MetarigError(
                "RIGIFY ERROR: invalid rig structure on bone: %s (%d bones)" % (strip_org(bone_name),len(self.org_bones))
            )

    def collect_connected_children_names(self, bone_name):
        ''' returns a list of connected children to bone_name '''
        bone = self.obj.data.bones[bone_name]
        #if bone:
        #    print('super_dome.collect_uncon_children_names bone %s' % bone.name)
        #else:
        #    print('super_dome.collect_uncon_children_names bone not found')
        names = []
        # for every unconnected child add
        for child in bone.children:
            if child.use_connect:
                print('super_bulge.collect_connected_children_names child %s' % child.name)
                names.append( child.name)
        # and out
        return names

    def collect_uncon_children_names(self, bone_name):
        ''' returns a list of unconnected children to bone_name '''
        bone = self.obj.data.bones[bone_name]
        #if bone:
        #    print('super_bulge.collect_uncon_children_names bone %s' % bone.name)
        #else:
        #    print('super_bulge.collect_uncon_children_names bone not found')
        names = []
        # for every unconnected child add
        for child in bone.children:
            if not child.use_connect:
                print('super_bulge.collect_uncon_children_names child %s' % child.name)
                names.append( child.name)
        # and out
        return names

    def gen_zhelper(self, bone_name):

        eb = self.obj.data.edit_bones
        center_bone = self.org_bones[0]
        if self.zhelper_bones:
            zhelper_name = mch('ZH-'+strip_mch(bone_name))
            zhelper_name = copy_bone_simple(self.obj,center_bone,zhelper_name)
            print('super_bulge.gen_zhelper %s' % zhelper_name)
            eb[zhelper_name].use_connect = False
            eb[zhelper_name].parent = eb[self.base_bone]
            eb[zhelper_name].tail = eb[bone_name].head
            eb[zhelper_name].length = eb[zhelper_name].length / 4;
            put_to = eb[bone_name].tail
            put_bone(self.obj,zhelper_name,put_to)
        # and try adjust it here the same
        zvec = (eb[ bone_name ].head - eb[center_bone].head)
        #print('super_bulge.make_mechanics to vector',zvec)
        #print('super_bulge.make_mechanics roll before',eb[ mch_name ].roll)
        eb[ bone_name ].align_roll(zvec)
        # and out
        #return

    def make_mechanics(self):

        # construct mechanics of the bone system
        # i.e. for tweaking the stretch route
        print('super_bulge.make_mechanics')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        org_bones = self.org_bones
        ofs_border = self.ofs_border
        mechs = []
        # start by copying the stretch_bone in elements
        # here two bones for head-guide_in and tail-guide_out
        for border in org_bones[ofs_border:]:
            # 1st head-guide_in
            mch_name = mch('H-' + strip_org(border))
            print('super_bulge.make_mechanics make %s' % mch_name)
            mch_name = copy_bone_simple( self.obj, border, mch_name)
            ## orient mech bone, so z points away from dome_bone
            #zvec = (eb[ mch_name ].tail - eb[org_bones[0]].head)
            ##print('super_bulge.make_mechanics to vector',zvec)
            ##print('super_bulge.make_mechanics roll before',eb[ mch_name ].roll)
            #eb[ mch_name ].align_roll(zvec)
            ##print('super_bulge.make_mechanics roll after',eb[ mch_name ].roll)
            ## point mech bones to the tail of the dome_bone (half length)
            #eb[ mch_name ].tail = eb[org_bones[0]].tail
            #eb[ mch_name ].length /= 2
            #print('super_bulge.make_mechanics roll after all',eb[ mch_name ].roll)
            movedir = eb[border].head - eb[border].tail
            move_to = eb[border].head + movedir
            put_bone( self.obj, mch_name, move_to)
            self.gen_zhelper(mch_name)
            mechs += [ mch_name ]
            # 2nd tail-guide_out
            mch_name = mch('T-' + strip_org(border))
            print('super_bulge.make_mechanics make %s' % mch_name)
            mch_name = copy_bone_simple( self.obj, border, mch_name)
            eb[ mch_name ].tail = eb[org_bones[0]].head
            eb[ mch_name ].length = eb[ mch_name ].length / 2
            put_to = eb[org_bones[0]].tail
            put_bone( self.obj, mch_name, put_to)
            self.gen_zhelper(mch_name)
            print('super_bulge.make_mechanics made %s' % mch_name)
            mechs += [ mch_name ]
        # and out
        return mechs

    def make_controls(self):

        # Just a control top of the dome_bone
        # other are tweaks
        print('super_bulge.make_controls')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        org_bones = self.org_bones
        ctrls = []
        # guide_out
        ctrl_name = org_bones[0]
        if self.ctrl_bone:
            ctrl_bone = copy_bone_simple(self.obj,self.ctrl_bone,strip_org(ctrl_name))
        else:
            ctrl_bone = copy_bone_simple(self.obj,ctrl_name,strip_org(ctrl_name))
            # put the control to the tail of the original
            put_bone( self.obj, ctrl_bone, eb[ org_bones[0]].tail )
        ctrls.append(ctrl_bone)
        # Make widget
        bpy.ops.object.mode_set(mode ='OBJECT')
        create_dome_widget(self.obj, ctrl_bone, size=1.0)
        ctrl_pb = self.obj.pose.bones[ ctrl_bone ]
        ctrl_pb.lock_scale = True, True, True
        return ctrls

    def make_tweaks(self):

        # the tweaks itself are the shaped bones
        # controlling the mechanics in the bone system
        # the dome_bone has its control
        # all other get a tweak
        print('super_bulge.make_tweaks')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        org_bones = self.org_bones
        tweaks = []
        for org_tweak in org_bones[1:]:
            tweak_name = strip_org(org_tweak)
            tweak_bone = copy_bone(self.obj,org_tweak,tweak_name)
            tweaks.append(tweak_bone)
        # Make widgets
        bpy.ops.object.mode_set(mode = 'OBJECT')
        for tweak in tweaks:
            create_bone_widget( self.obj, tweak)
            tweak_pb = self.obj.pose.bones[ tweak ]
            # Set locks
            tweak_pb.lock_location = True, True, True
            tweak_pb.lock_rotation = False, True, False
            tweak_pb.lock_rotation_w = False
            if tweaks.index(tweak) < self.ofs_border - 1:
                tweak_pb.lock_scale = False, False, False
            else:
                tweak_pb.lock_scale = True, True, True
            if self.tweak_layers:
                tweak_pb.bone.layers = self.tweak_layers
        # and out
        return tweaks

    def make_deform(self):

        # make the finally deforming skeleton meshes are rigged to
        # simply a copy of all org_bones
        print('super_bulge.make_deform')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        defs = []
        org_bones = self.org_bones
        ofs_border = self.ofs_border - 1
        # iterate child and border bones
        for ix, org_bone in enumerate(org_bones[1:]):
            def_name = deformer(strip_org(org_bone))
            def_bone = copy_bone(self.obj,org_bone, def_name)
            if ix >= ofs_border:
                eb[def_bone].tail = eb[org_bones[0]].tail
                eb[def_bone].bbone_segments = self.bbone_segments
                self.gen_zhelper(def_bone)
            defs.append(def_bone)
        # and out
        return defs

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
        print('super_bulge.make_constraints')
        # test if above works out
        #return
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        #for ebone in eb:
        #    print('DEBUG: eb %s' % ebone.name)
        bpy.ops.object.mode_set(mode ='OBJECT')
        org_bones = self.org_bones
        pb        = self.obj.pose.bones
        #for pbone in pb:
        #    print('DEBUG: pb %s' % pbone.name)
        mechs   = all_bones['mech'  ]
        ctrls   = all_bones['ctrl'  ]
        tweaks  = all_bones['tweak' ]
        deforms = all_bones['deform']
        ofs_border = self.ofs_border - 1
        # constraints
        # STRETCH_TO for ORG-dome_bone to ctrls[0]
        print('super_bulge.make_constraints %s to %s' % (org_bones[0],ctrls[0]))
        self.make_constraint(org_bones[0], {
            'constraint': 'STRETCH_TO'
            , 'subtarget': ctrls[0]
            })
        # locks to ctrls[0]
        pb[ctrls[0]].lock_location   = False, False, False
        pb[ctrls[0]].lock_rotation   = True, True, True
        pb[ctrls[0]].lock_rotation_w = True
        pb[ctrls[0]].lock_scale      = True, True, True
        # STRETCH_TO for border deforms to ctrl
        for ix, deform in enumerate(deforms[ofs_border:]):
            print('super_bulge.make_constraints %s to %s' % (deform,ctrls[0]))
            self.make_constraint(deform, {
                'constraint': 'STRETCH_TO'
                , 'subtarget': ctrls[0]
                })
            pb[deform].use_bbone_custom_handles = True
            from_bone = mechs[ ix * 2 ]
            print('super_bulge.make_constraints %s handle_in %s' % (deform,from_bone))
            pb[deform].bbone_custom_handle_start = pb[from_bone]
            to_bone = mechs[ ix * 2 + 1 ]
            print('super_bulge.make_constraints %s handle_out %s' % (deform,to_bone))
            pb[deform].bbone_custom_handle_end = pb[to_bone]
        # and out

    def parent_bones(self, all_bones):

        # give the parenting to the constructed bone system
        print('super_bulge.parent_bones')
        # test if above works out
        #return
        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones
        ofs_border = self.ofs_border
        ofs_cons = ofs_border-1
        eb        = self.obj.data.edit_bones
        mechs   = all_bones['mech'  ]
        ctrls   = all_bones['ctrl'  ]
        tweaks  = all_bones['tweak' ]
        deforms = all_bones['deform']
        # parenting
        # ORG-dome_bone to base
        eb[org_bones[0]].use_connect = False
        print('super_bulge.parent_bones %s to %s' % (org_bones[0],self.base_bone))
        eb[org_bones[0]].parent = eb[self.base_bone]

        # ORG-con-childs to ctrl
        for con_child in org_bones[1:ofs_border]:
            eb[con_child].use_connect = False
            print('super_bulge.parent_bones %s to %s' % (con_child,ctrls[0]))
            eb[con_child].parent = eb[ctrls[0]]
        # tweak con-childs to ORG-con-childs
        for ix, con_tweak in enumerate(tweaks[:ofs_cons]):
            eb[con_tweak].use_connect = False
            print('super_bulge.parent_bones %s to %s' % (con_tweak,org_bones[ix+1]))
            eb[con_tweak].parent = eb[org_bones[ix+1]]
        # DEF-con-childs to tweak con-childs
        for ix, con_def in enumerate(deforms[:ofs_cons]):
            eb[con_def].use_connect = False
            print('super_bulge.parent_bones %s to %s' % (con_def,tweaks[ix]))
            eb[con_def].parent = eb[tweaks[ix]]

        # border
        # border orgs to base
        for border in org_bones[ofs_border:]:
            eb[border].use_connect = False
            print('super_bulge.parent_bones %s to %s' % (border,self.base_bone))
            eb[border].parent = eb[self.base_bone]
        # border tweaks to orgs
        for ix,brd_tweak in enumerate(tweaks[ofs_cons:]):
            eb[brd_tweak].use_connect = False
            print('super_bulge.parent_bones %s to %s' % (brd_tweak,org_bones[ix+ofs_border]))
            eb[brd_tweak].parent = eb[org_bones[ix+ofs_border]]
        # border mechs to tweaks & top mechs to ctrl
        for ix, mech in enumerate(mechs):
            if ix % 2 == 0:
                eb[mech].use_connect = False
                print('super_bulge.parent_bones %s to %s' % (mech,tweaks[ofs_cons+ix//2]))
                eb[mech].parent = eb[tweaks[ofs_cons+ix//2]]
            else:
                eb[mech].use_connect = False
                print('super_bulge.parent_bones %s to %s' % (mech,ctrls[0]))
                eb[mech].parent = eb[ctrls[0]]
        # border defs to mechs
        for ix,brd_def in enumerate(deforms[ofs_cons:]):
            eb[brd_def].use_connect = False
            print('super_bulge.parent_bones %s to %s' % (brd_def,tweaks[ofs_cons+ix]))
            eb[brd_def].parent = eb[tweaks[ofs_cons+ix]]
        # and out

    def generate(self):

        # main generation method
        print('super_bulge.generate')
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones
        # create a base_bone of org_bones[0] if not set
        if not self.base_bone:
            base_name = mch(self.org_bones[0])
            self.base_bone = copy_bone(self.obj,self.org_bones[0], base_name)
            eb[self.base_bone].length /= 4
        # Creating all bones
        mechs  = self.make_mechanics()
        ctrls  = self.make_controls()
        tweaks = self.make_tweaks()
        defs   = self.make_deform()
        # join in dictionary
        all_bones = {
              'mech'    : mechs
            , 'ctrl'    : ctrls
            , 'tweak'   : tweaks
            , 'deform'  : defs
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
    params.base_bone = bpy.props.StringProperty(
        name = 'base_bone',
        default = '',
        description = "Base bone to parent to (if none build one)"
        )
    # number of segments in the stretch elements
    params.bbone_segments = bpy.props.IntProperty(
        name        = 'bbone segments',
        default     = 7,
        min         = 3,
        description = 'Number of segments in bendies'
    )
    # zhelper_bones to adjust bone roll after generation
    params.zhelper_bones = bpy.props.BoolProperty(
        name        = "zhelper_bones",
        default     = True,
        description = "Helper bones for adjusting bone roll to Z"
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
    # param base bone
    r = layout.row()
    r.prop_search(params, 'base_bone', pb, "bones", text="Base bone")
    # number of segments in the stretch elements
    r = layout.row()
    r.prop(params, "bbone_segments", text="Number segments in bendies")
    # zhelper_bones to adjust bone roll after generation
    r = layout.row()
    r.prop(params, "zhelper_bones", text="ZHelper")
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
    bone = arm.edit_bones.new('base')
    bone.head[:] = 0.0000, 0.0000, 0.0000
    bone.tail[:] = 0.0000, 0.0000, 1.0000
    bone.roll = 0.0000
    bone.use_connect = False
    bones['base'] = bone.name
    bone = arm.edit_bones.new('dome')
    bone.head[:] = 0.0000, 0.0000, 1.0000
    bone.tail[:] = 0.0000, 0.0000, 4.0000
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['base']]
    bones['dome'] = bone.name
    bone = arm.edit_bones.new('border.001')
    bone.head[:] = 2.0000, 0.0000, 1.0000
    bone.tail[:] = 2.0000, 0.0000, 2.0000
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['base']]
    bones['border.001'] = bone.name
    bone = arm.edit_bones.new('border.002')
    bone.head[:] = 0.0000, 2.0000, 1.0000
    bone.tail[:] = 0.0000, 2.0000, 2.0000
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['base']]
    bones['border.002'] = bone.name
    bone = arm.edit_bones.new('border.003')
    bone.head[:] = -2.0000, 0.0000, 1.0000
    bone.tail[:] = -2.0000, 0.0000, 2.0000
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['base']]
    bones['border.003'] = bone.name
    bone = arm.edit_bones.new('border.004')
    bone.head[:] = 0.0000, -2.0000, 1.0000
    bone.tail[:] = 0.0000, -2.0000, 2.0000
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['base']]
    bones['border.004'] = bone.name
    bone = arm.edit_bones.new('top')
    bone.head[:] = 0.0000, 0.0000, 4.0000
    bone.tail[:] = 0.0000, 0.0000, 5.0000
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['dome']]
    bones['top'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['base']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['dome']]
    pbone.rigify_type = 'experimental.super_bulge'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['border.001']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['border.002']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['border.003']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['border.004']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['top']]
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
