import os
import sys

import lx
import modo
import modo.constants as c

from cs_cry_export.constants import (
    CRYMAT_PREFIX,
    CRYEXPORTNODE_PREFIX,
    MODO_MATERIAL_STRING,
    PROXY_NONE,
    CHANNEL_PROXY_TYPE_NAME,
)


def get_submats_from_cryexport_node(cryexport_node):
    """
    Gets the materials from a passed in cryexport_node
    :param cryexport_node:
    :return:
    """
    scene = modo.Scene()
    material_names = set()
    meshes = cryexport_node.children(itemType=c.MESH_TYPE, recursive=True)
    for mesh in meshes:
        geo = mesh.geometry
        for x in xrange(geo.PTagCount(lx.symbol.i_PTAG_MATR)):
            material_names.add(geo.PTagByIndex(lx.symbol.i_PTAG_MATR, x))
    material_names = list(material_names)
    material_names.reverse()
    materials = []
    for mat in scene.items(c.MASK_TYPE):
        if mat.name.replace(MODO_MATERIAL_STRING, "").strip() in material_names:
            materials.append(mat)
    # sort backwards cuz modo
    return sorted(materials, key=lambda y: 1 - y.parentIndex)


def get_cry_materials(selected=False):
    # gets all the cry materials in the scene
    scene = modo.Scene()
    materials = (
        scene.selectedByType(c.MASK_TYPE) if selected else scene.items(c.MASK_TYPE)
    )
    ret_mats = []
    for mat in materials:
        if mat.name.startswith(CRYMAT_PREFIX):
            ret_mats.append(mat)

    return ret_mats


def mat_name(mat):
    """Get mat name with (Material) Stripped off"""
    return mat.name.replace(MODO_MATERIAL_STRING, "").strip()


def make_phys_material_name(mat, idx, hash=False):
    phys_type = (
        mat.channel(CHANNEL_PROXY_TYPE_NAME).get()
        if mat.channel(CHANNEL_PROXY_TYPE_NAME) is not None
        else PROXY_NONE
    )
    return "%s%s__%s__%s__%s" % (
        "#" if hash else "",
        mat.parent.name,
        mat_name(mat),
        idx + 1,
        phys_type,
    )


def get_parent_cryexport_from_selected():
    scene = modo.Scene()
    child = (
        scene.selectedByType(c.MESH_TYPE) + scene.selectedByType(c.GROUPLOCATOR_TYPE)
    )[0]
    return get_parent_cryexport_from_child(child)


def get_parent_cryexport_from_child(child):
    if child.name.startswith(CRYEXPORTNODE_PREFIX):
        return child
    if child.parents is None:
        return None
    if len(child.parents) == 0:
        return None
    for parent in child.parents:
        if parent.name.startswith(CRYEXPORTNODE_PREFIX):
            return parent
        get_parent_cryexport_from_child(parent)


def make_effect_name(mat, idx):
    return "%s-%s-submat-effect" % (mat.parent.name, idx + 1)


def get_scene_root_folder():
    scene_root = lx.eval1("query sceneservice scene.file ? current")
    if scene_root is not None:
        return os.path.dirname(scene_root)
    sys.exit()


def get_cryexportnodes(selected=True):
    """ Gets all the cryexportnodes in a scene"""
    scene = modo.Scene()
    nodes = []
    items = scene.selected if selected else scene.items(c.GROUPLOCATOR_TYPE)
    for item in items:
        if item.name.startswith(CRYEXPORTNODE_PREFIX):
            nodes.append(item)

    return nodes


def create_channel(name, item):
    """
    Creates a user_channel on an item
    :param name: str The name of the user channel
    :param item: modo.item.Item The modo item 
    """
    lx.eval(
        "channel.create {name} string item:{item_name} username:{name}".format(
            name=name, item_name=item.id
        )
    )


def get_user_input(title):
    """
    Opens a dialog to get a user input
    :param title: str The title of the
    :return: str
    """
    # Create a user values.
    lx.eval("user.defNew name:UserValue type:string life:momentary")
    # Set the label name for the popup we're going to call
    lx.eval('user.def UserValue dialogname "{0}"'.format(title))
    # Set the user names for the values that the users will see
    lx.eval("user.def UserValue username {Name}")
    # The '?' before the user.value call means we are calling a popup to have the user set the value
    try:
        lx.eval("?user.value UserValue")
        lx.eval("dialog.result ?")
    except RuntimeError as e:
        lx.eval("dialog.result ?")
    # Now that the user set the values, we can just query it
    user_input = lx.eval("user.value UserValue ?")

    return user_input
