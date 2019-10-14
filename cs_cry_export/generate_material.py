import os
import subprocess

import modo
import modo.constants as c

from cs_cry_export.constants import (
    CRYMAT_PREFIX,
    MODO_MATERIAL_STRING,
    CHANNEL_PROXY_TYPE_NAME,
)
from cs_cry_export.utils import get_scene_root_folder
from lxml import etree
from lxml.builder import ElementMaker

E = ElementMaker()


def compile_material(mat):
    # TODO: Sort these by parentIndex
    children_names = [
        submat.name.replace(MODO_MATERIAL_STRING, "").strip()
        for submat in mat.children()
    ]
    proxy_types = [
        submat.channel(CHANNEL_PROXY_TYPE_NAME).get()
        if submat.channel(CHANNEL_PROXY_TYPE_NAME) is not None
        else None
        for submat in mat.children()
    ]
    # we reverse these because modo shader list is from bottom to top
    children_names.reverse()
    proxy_types.reverse()
    xml = E.Material(
        {"MtlFlags": "524544", "vertModifType": "0"},
        E.SubMaterials(
            *map(
                lambda x: E.Material(
                    {
                        "Name": x[0],
                        "MtlFlags": "525440",
                        "Shader": "Illum" if x[1] is None else "NoDraw",
                        "GenMask": "0",
                        "StringGenMask": "",
                        "SurfaceType": "",
                        "MatTemplate": "",
                        "Diffuse": "1,1,1",
                        "Specular": "0.04,0.04,0.04",
                        "Opacity": "1",
                        "Shininess": "255",
                        "vertModifType": "0",
                        "LayerAct": "1",
                    },
                    E.Textures(),
                ),
                zip(children_names, proxy_types),
            )
        ),
        E.PublicParams(
            {
                "EmittanceMapGamma": "1",
                "SSSIndex": "0",
                "IndirectColor": "0.25,0.25,0.25",
            }
        ),
    )
    return xml


def write_material(xml, name):
    scene_root = get_scene_root_folder()
    with open(
        os.path.join(scene_root, name.replace(CRYMAT_PREFIX, "") + ".mtl"), "w"
    ) as f:
        f.write(etree.tostring(xml, pretty_print=True))


def main():
    scene = modo.Scene()
    # get the selected material masks
    materials = scene.selectedByType(c.MASK_TYPE)
    if len(materials) == 0:
        return modo.dialogs.alert("Warning", "No CryMaterial Selected")
    for mat in materials:
        if mat.name.startswith(CRYMAT_PREFIX):
            write_material(compile_material(mat), mat.name)
        if mat.parent.name.startswith(CRYMAT_PREFIX):
            write_material(compile_material(mat.parent), mat.parent.name)
    if (
        modo.dialogs.yesNo(
            "Material Created",
            "Would you like to open the folder containing the material?",
        )
        is "yes"
    ):
        subprocess.Popen(r'explorer "%s"' % get_scene_root_folder())
