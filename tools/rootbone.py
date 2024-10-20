# GPL License

import bpy
from difflib import SequenceMatcher

from . import common as Common
from .register import register_wrap
from .. import globs
from .translations import t


@register_wrap
class RootButton(bpy.types.Operator):
    bl_idname = 'cats_root.create_root'
    bl_label = t('RootButton.label')
    bl_description = t('RootButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return Common.is_enum_non_empty(context.scene.root_bone)

    def execute(self, context):
        saved_data = Common.SavedData()
        Common.set_default_stage()

        Common.switch('EDIT')

        # this is the bones that will be parented
        child_bones = globs.root_bones[context.scene.root_bone]

        # Create the new root bone
        new_bone_name = 'Root_' + child_bones[0]
        root_bone = bpy.context.object.data.edit_bones.new(new_bone_name)
        root_bone.parent = bpy.context.object.data.edit_bones[child_bones[0]].parent

        # Parent all children to the new root bone
        for child_bone in child_bones:
            bpy.context.object.data.edit_bones[child_bone].use_connect = False
            bpy.context.object.data.edit_bones[child_bone].parent = root_bone

        # Set position of new bone to parent
        root_bone.head = root_bone.parent.head
        root_bone.tail = root_bone.parent.tail

        # reset the root bone cache
        globs.root_bones_choices = {}

        saved_data.load()

        self.report({'INFO'}, t('RootButton.success'))

        return{'FINISHED'}


def get_parent_root_bones(self, context):
    armature = Common.get_armature()
    check_these_bones = []
    bone_groups = {}
    choices = []

    if armature is None:
        return choices
    armature = armature.data

    # Get cache if exists
    if len(globs.root_bones_choices) >= 1:
        return globs.root_bones_choices

    for bone in armature.bones:
        check_these_bones.append(bone.name)

    ignore_bone_names_with = [
        'finger',
        'chest',
        'leg',
        'arm',
        'spine',
        'shoulder',
        'neck',
        'knee',
        'eye',
        'toe',
        'head',
        'teeth',
        'thumb',
        'wrist',
        'ankle',
        'elbow',
        'hips',
        'twist',
        'shadow',
        'dummy',
        'hand',
        'waistcancel',
        'root_'
    ]

    # Find and group bones together that look alike
    # Please do not ask how this works
    for rootbone in armature.bones:
        ignore = False
        for ignore_bone_name in ignore_bone_names_with:
            if ignore_bone_name in rootbone.name.lower():
                ignore = True
                break
        if ignore:
            continue
        for bone in armature.bones:
            if bone.name in check_these_bones:
                m = SequenceMatcher(None, rootbone.name, bone.name)
                if m.ratio() >= 0.70:
                    accepted = False
                    if bone.parent is not None:
                        for child_bone in bone.parent.children:
                            if child_bone.name == rootbone.name:
                                accepted = True

                    check_these_bones.remove(bone.name)
                    if accepted:
                        if rootbone.name not in bone_groups:
                            bone_groups[rootbone.name] = []
                        bone_groups[rootbone.name].append(bone.name)

    bone_groups_tmp = {}
    for rootbone in bone_groups:
        # NOTE: user probably doesn't want to parent bones together that have less then 2 bones
        if len(bone_groups[rootbone]) >= 2:
            choices.append((rootbone, rootbone.replace('_R', '').replace('_L', '') + ' (' + str(len(bone_groups[rootbone])) + ' bones)', rootbone))
            bone_groups_tmp[rootbone] = bone_groups[rootbone]

    # set cache
    globs.root_bones = bone_groups_tmp
    globs.root_bones_choices = choices

    return choices


@register_wrap
class RefreshRootButton(bpy.types.Operator):
    bl_idname = 'cats_root.refresh_root_list'
    bl_label = t('RefreshRootButton.label')
    bl_description = t('RefreshRootButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        print(globs.root_bones_choices)
        print('')
        print(globs.root_bones)
        globs.root_bones_choices = {}

        self.report({'INFO'}, t('RefreshRootButton.success'))

        return{'FINISHED'}
