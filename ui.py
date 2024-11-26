import bpy
from bpy.types import PropertyGroup, Panel, Object

class MyAddonProperties(PropertyGroup):
    target_object: bpy.props.PointerProperty(
        name='Target Object',
        type=Object,
        description='Select an object'
    ) # type: ignore

class VIEW3D_PT_custom_panel(Panel):
    # Where to add panel in UI
    bl_space_type = 'VIEW_3D' # 3D Viewport Area
    bl_region_type = 'UI' # Sidebar region
    
    # Add labels
    bl_category = 'Grease Bin Rendering'
    bl_label = 'Grease Bin Rendering'
    
    def draw (self, context):
        layout = self.layout
        props = context.scene.my_addon_props
        row = self.layout.row()
        row.operator("render.render_pairs", text="Render Pairs")