# Modo CryExport
> CRYENGINE exporter for modo 13^

## Materials
* To create a CRYENGINE material. Create a material group and group your materials into it. The name must start with `crymat_`
* The materials order will be used to order the material exported and material ids

## Meshes
> The following structure should be used
* `CryExportNode_example`
    * `example_group` - UDP options go hjere
        * `proxy_mesh`
        * `mesh1`
        * `mesh2`
        * `_lod1_example_group`
            * `lod1_mesh`
        * `_lod2_example_group`
            * `lod2_mesh`     

## Customer User Channels
### outputPath
> Where the cgf file will be export to
> This is added to the parent CryExportNode
    
    * STRING<DIRECTORY PATH>
     
### proxyType
> What type of proxy material. This is added to the material

    * physProxyNoDraw
    * physNoCollide
    * physObstruct
    * physNone

### udp
> Defines the type of primitive proxy if it's not defined it's considered a RENDERMESH
> This is added to the mesh_group containing the proxy.
    
    * rendermesh
    * box
    * cylinder
    * sphere

### cryHelper
> Just defined what is a CryHelper Locator