import modo
import modo.constants as c

import cs_cry_export.utils as utils
import cs_cry_export.constants as _c


def main():
    scene = modo.Scene()
    cryexport_node = utils.get_parent_cryexport_from_selected()
    materials = utils.get_submats_from_cryexport_node(cryexport_node)
    # creat the material name with a user dialog
    result = utils.get_user_input("Helper Name.")
    # create a new material mask group
    parent = scene.addItem(c.MASK_TYPE)
    parent.name = _c.CRYMAT_PREFIX + result
    # Add the needed channels to the material masks
    for material in materials:
        # add all the mats used on the mesh to that group
        material.setParent(parent)
        if material.channel(_c.CHANNEL_PROXY_TYPE_NAME) is None:
            utils.create_channel(_c.CHANNEL_PROXY_TYPE_NAME, material)
            material.channel(_c.CHANNEL_PROXY_TYPE_NAME).set("physNone")


if __name__ == "__main__":
    reload(utils)
    main()
