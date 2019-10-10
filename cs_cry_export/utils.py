import os
import sys

import lx
import modo


def get_scene_root_folder():
    scene_root = lx.eval1("query sceneservice scene.file ? current")
    if scene_root is not None:
        return os.path.dirname(scene_root)
    sys.exit()


def get_cryexportnodes():
    """ Gets all the cryexportnodes in a scene"""
    scene = modo.Scene()
    nodes = []
    for item in scene.selected:
        if item.name.startswith("cryexportnode_"):
            nodes.append(item)
    return nodes


def create_channel(name, item):
    """
    Creates a user_channel on an item
    :param name: str The name of the user channel
    :param item: modo.item.Item The modo item 
    """
    lx.eval(
        "channel.create {name} string scalar false 0.0 false 0.0 0.0 {item_name} {name}".format(
            name=name, item_name=item.name
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
