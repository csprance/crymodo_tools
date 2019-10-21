import modo
import modo.constants as c

import cs_cry_export.constants as _c
from cs_cry_export.utils import create_channel, get_user_input


def main():
    scene = modo.Scene()
    # if it's a group
    selected = scene.selectedByType(c.GROUPLOCATOR_TYPE)
    # not a group
    if len(selected) == 0:
        # check if it's a mesh
        selected = scene.selectedByType(c.MESH_TYPE)
        # it's a mesh
        if len(selected) > 0:
            # group all selected meshes
            group = scene.addItem(
                c.GROUPLOCATOR_TYPE, name=get_user_input("CryExport Node Name")
            )
            for item in selected:
                item.setParent(group)
            # set group to be selected
            scene.select(group)
            selected = scene.selectedByType(c.GROUPLOCATOR_TYPE)

    # create the main export group
    cry_node_name = _c.CRYEXPORTNODE_PREFIX + selected[0].name
    cry_export_group = scene.addItem(c.GROUPLOCATOR_TYPE, name=cry_node_name)

    # create the group export node
    group_name = selected[0].name + "_group"
    model_group = scene.addItem(c.GROUPLOCATOR_TYPE, name=group_name)
    model_group.setParent(cry_export_group)

    # create channels on groups
    create_channel(_c.CHANNEL_OUTPUT_PATH_NAME, cry_export_group).set("..\\")
    create_channel(_c.CHANNEL_FILETYPE_NAME, cry_export_group).set("1")
    create_channel(_c.CHANNEL_EXPORTABLE_NAME, cry_export_group).set("1")
    create_channel(_c.CHANNEL_MERGE_OBJECTS_NAME, cry_export_group).set("0")
    create_channel(_c.CHANNEL_UDP_NAME, model_group).set("")

    # set parents
    children = selected[0].children()
    for child in children:
        child.setParent(model_group)
    # remove the original group
    scene.removeItems(selected[0])
