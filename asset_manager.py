import bpy
import os

from bpy.types import Object, Collection, Operator, Context

from .ui_elements import update_ui, QueriedMaterialItem, QueriedSegmentationItem

def get_all_objects_in_collection(collection: Collection) -> list[Object]:
    objects = list(collection.objects)  # Get objects directly in the collection

    # Recursively get objects from child collections
    for child_collection in collection.children:
        objects.extend(get_all_objects_in_collection(child_collection))

    return objects

def localize_objects(objects: list[Object]):
    # Track already copied materials
    copied_materials = {}
    
    # Ensure all objects, meshes, and materials are local
    for obj in objects:
        if obj.type == 'MESH':
            # Make object and mesh data local explicitly
            obj.make_local()  # makes the object itself local
            if obj.data:
                obj.data.make_local()  # explicitly make mesh data local

            # Process materials, reuse existing copies
            for slot in obj.material_slots:
                original_material = slot.material
                if original_material:
                    if original_material.name in copied_materials:
                        # Use the existing local copy
                        slot.material = copied_materials[original_material.name]
                    else:
                        # Create a single local copy and store it
                        local_material = original_material.copy()
                        local_material.name = original_material.name + "_local"
                        copied_materials[original_material.name] = local_material
                        slot.material = local_material

def get_asset_paths(type: str) -> dict[str, str]:
    plugin_dir: str = os.path.dirname(os.path.abspath(__file__))
    assets_dir: str = os.path.join(plugin_dir, f'assets/{type}')    

    if not os.path.exists(assets_dir):
        raise FileNotFoundError(f"Assets directory '{assets_dir}' does not exist.")
        
    asset_paths = {asset: os.path.join(assets_dir, asset) for asset in os.listdir(assets_dir)}
    return asset_paths

def load_assets(paths: dict[str, str], type: str):
    for file_name, path in paths.items():
        name: str = file_name.split('.')[0]
        with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
            if type == 'collection':
                if name in data_from.collections:
                    data_to.collections.append(name)
                else:
                    raise ValueError(f"'{name}' collection not found in {path}. Make sure the collection being appended is named the same as the file.")
            elif type == 'object':
                if name in data_from.objects:
                    data_to.objects.append(name)
                else:
                    raise ValueError(f"'{name}' not found in {path}. Make sure the object being appended is named the same as the file.")

def load_all_assets():
    load_assets(get_asset_paths("bin"), 'collection')
    load_assets(get_asset_paths("environments"), 'object')

def append_bin() -> Collection:        
    # Get the appended collection
    bin_collection = bpy.data.collections.get("camera_and_bin")
    if not bin_collection:
        raise ValueError("Failed to append 'camera_and_bin' collection.")
    
    # Link the collection to the scene's master collection
    bpy.context.scene.collection.children.link(bin_collection)

    return bin_collection

class ASSET_OT_add_bin(Operator):
    bl_idname = "asset.add_bin"
    bl_label = "Add Bin"
    bl_description = "Add a grease bin to the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, ctx: Context):
        bin_collection: Collection = append_bin()
        bin_collection_objects: list[Object] = get_all_objects_in_collection(bin_collection)

        localize_objects(bin_collection_objects)

        # Update the UI
        for area in ctx.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'UI':
                        region.tag_redraw()

        return {"FINISHED"}
    
class ASSET_OT_query_materials(Operator):
    bl_idname = "asset.query_materials"
    bl_label = "Query Materials"
    bl_description = "Query and display all the materials with a settings node."
    bl_options = {'REGISTER'}

    def execute(self, ctx: Context):
        # Clear the existing queried materials
        ctx.scene.queried_materials.clear()

        # Query all materials with a node named "settings"
        for material in bpy.data.materials:
            if material.use_nodes and 'local' in material.name:
                for node in material.node_tree.nodes:
                    if node.name == "settings":
                        item = ctx.scene.queried_materials.add()
                        item.material = material
                        break

        update_ui(ctx)

        return {"FINISHED"}
    
    def register():
        # Attach a collection property to the scene for storing queried materials
        bpy.types.Scene.queried_materials = bpy.props.CollectionProperty(type=QueriedMaterialItem)

class ASSET_OT_query_seg_materials(Operator):
    bl_idname = "asset.query_seg_materials"
    bl_label = "Query Segmentation Materials"
    bl_description = "Query and display all the segmentation material's RGB nodes."
    bl_options = {'REGISTER'}

    def execute(self, ctx: Context):
        # Clear existing queries sementation materials
        ctx.scene.queried_seg_materials.clear()

        # Query all materials with a node named "RGB" and "seg" and "local" in the material name
        for material in bpy.data.materials:
            if material.use_nodes and 'seg_local' in material.name:
                for node in material.node_tree.nodes:
                    if node.name == "RGB":
                        item = ctx.scene.queried_seg_materials.add()
                        item.material = material
                        break

        update_ui(ctx)

        return {"FINISHED"}

    def register():
        # Attach a collection property to the scene for storing queried materials
        bpy.types.Scene.queried_seg_materials = bpy.props.CollectionProperty(type=QueriedSegmentationItem)
