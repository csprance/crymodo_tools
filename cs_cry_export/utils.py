import os
import re

import lx
import modo
import modo.constants as c
import cs_cry_export.constants as _c
from cs_cry_export.constants import (
    CRYMAT_PREFIX,
    CRYEXPORTNODE_PREFIX,
    MODO_MATERIAL_STRING,
    PROXY_NONE,
    CHANNEL_PROXY_TYPE_NAME,
)


def vtos(vec):
    return " ".join(map(str, vec))


def restore_selection(func):
    """Decorator Function to restore user selection"""

    def function_wrapper(*args, **kwargs):
        scene = modo.Scene()
        selected = scene.selected
        x = func(*args, **kwargs)
        scene.deselect()
        scene.select(selected)
        return x

    return function_wrapper


def get_submats_from_nodes(meshes):
    scene = modo.Scene()
    material_names = set()
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
    return sorted(materials, key=lambda sm: 1 - sm.parentIndex)


def get_submats_from_cryexport_node(cryexport_node):
    """
    Gets the materials from a passed in cryexport_node
    :param cryexport_node:
    :return:
    """
    meshes = cryexport_node.children(itemType=c.MESH_TYPE, recursive=True)
    return get_submats_from_nodes(meshes)


def get_cry_materials(selected=False):
    """
    gets all the cry materials in the scene
    :param selected: Boolean should we look in the scene or the selected items
    :return: [modo.item.Item] material nodes
    """
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
    """
    Get mat name with (Material) Stripped off
    :param mat: modo.item.Item the material item
    :return: string The material name with the (material) stripped off
    """
    return mat.name.replace(MODO_MATERIAL_STRING, "").strip()


def group_name(group):
    """
    Get group name with _group Stripped off
    :param group: modo.item.Item the group locator item
    :return: string The group name with the _group stripped off
    """
    return group.name.replace(_c.GROUP_SUFFIX, "").strip()


def make_phys_material_name(mat, idx=None, hash=False):
    if idx is None:
        idx = (len(mat.parent.children()) - mat.parentIndex) - 1
    phys_type = (
        mat.channel(CHANNEL_PROXY_TYPE_NAME).get()
        if mat.channel(CHANNEL_PROXY_TYPE_NAME) is not None
        else PROXY_NONE
    )
    return (
        "%s%s__%s__%s__%s"
        % ("#" if hash else "", mat.parent.name, mat_name(mat), idx + 1, phys_type)
    ).replace(_c.CRYMAT_PREFIX, "")


def delete_item(item):
    """
    Delete an item
    :param item: modo.item.Item
    :return: None
    """
    try:
        lx.eval("item.delete item:{0}".format(item.id))
    except Exception as e:
        print(e)


def get_groups_from_cryexport_node(node):
    """
    Given a CryExportNode get the groups in that folder
    :param node: modo.item.Item The CryExportNode item
    :return: list of GroupLocator modo.item
    """
    groups = []
    for child in node.children():
        if child.name.endswith("_group"):
            groups.append(child)
    return groups


def strip_lod(name):
    return re.sub(r"_lod._", "", name)


@restore_selection
def merge_group_meshes(group, name="DELETEME"):
    """
    Merge a groups meshes into a single mesh and return that modo.item.Item
    :param group: modo.item.Item GroupLocator
    :param name: string Name of the item Default: DELETME
    :return: modo.item.Item
    """
    scene = modo.Scene()
    combine = scene.addItem(c.MESH_TYPE, name=name)
    for child in group.childrenByType(c.MESH_TYPE):
        scene.select(child, add=True)
        lx.eval("item.componentMode polygon true")
        lx.eval("select.drop polygon")
        lx.eval("select.invert")
        lx.eval("copy")
        scene.select(combine)
        lx.eval("paste")
    return combine


def get_parent_cryexport_from_selected():
    """
    Given any selected mesh/groupLocator find it's parent CryExportNode
    :return: modo.item.Item CryExportNode Item
    """
    scene = modo.Scene()
    child = (
        scene.selectedByType(c.MESH_TYPE) + scene.selectedByType(c.GROUPLOCATOR_TYPE)
    )[0]

    return get_parent_cryexport_from_child(child)


def get_parent_cryexport_from_child(child):
    """
    Given a child node go and find the parent CryExportNode
    :param child: modo.item.Item the item to look in it's parents for
    :return: None | modo.item.Item the parent CryExportNode
    """
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
    """
    Make the <effect> dae xml tag name
    :param mat: modo.item.Item of a c.MASK_TYPE
    :param idx: int
    :return: string effect name
    """
    return ("%s-%s-submat-effect" % (mat.parent.name, idx + 1)).replace(
        _c.CRYMAT_PREFIX, ""
    )


def get_scene_root_folder():
    """
    Get the scenes source location root folder
    :return: string Root Folder Path
    """
    filename = modo.Scene().filename
    if filename:
        return os.path.dirname(filename)
    modo.dialogs.alert("Save Scene", "Please save scene before exporting.")
    raise Exception("Please Save Scene First")


def get_cryexportnodes(selected=True):
    """
    Gets all the cryexportnodes in a scene
    :param selected: Boolean should we get from the selected items or the scene
    :return: [modo.item.Item]
    """
    scene = modo.Scene()
    nodes = []
    items = scene.selected if selected else scene.items(c.GROUPLOCATOR_TYPE)
    for item in items:
        if item.name.startswith(CRYEXPORTNODE_PREFIX):
            nodes.append(item)

    return nodes


def create_channel(name, item, datatype="string"):
    """
    Creates a user_channel on an item
    :param datatype: string integer float
    :param name: str The name of the user channel
    :param item: modo.item.Item The modo item 
    """
    lx.eval(
        "channel.create {name} {datatype} item:{item_id} username:{name}".format(
            name=name, item_id=item.id, datatype=datatype
        )
    )
    return modo.channel.Channel(name, item)


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
