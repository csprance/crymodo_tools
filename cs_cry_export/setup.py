import modo
import modo.constants as c

from cs_cry_export.constants import (
    CRYEXPORTNODE_PREFIX,
    CHANNEL_OUTPUT_PATH_NAME,
    CHANNEL_UDP_NAME,
)
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
    cry_node_name = CRYEXPORTNODE_PREFIX + selected[0].name
    cry_export_group = scene.addItem(c.GROUPLOCATOR_TYPE, name=cry_node_name)

    # create the group export node
    group_name = selected[0].name + "_group"
    model_group = scene.addItem(c.GROUPLOCATOR_TYPE, name=group_name)
    model_group.setParent(cry_export_group)

    # create channels on groups
    create_channel(CHANNEL_OUTPUT_PATH_NAME, cry_export_group)
    cry_export_group.channel(CHANNEL_OUTPUT_PATH_NAME).set("")
    create_channel(CHANNEL_UDP_NAME, model_group)
    model_group.channel(CHANNEL_UDP_NAME).set("")

    # set parents
    children = selected[0].children()
    for child in children:
        child.setParent(model_group)
    # remove the original group
    scene.removeItems(selected[0])
