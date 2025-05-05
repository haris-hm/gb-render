import bpy

# from bpy.props import *
from bpy.types import Panel, Context, Scene, Material, Operator, Event

from .ui_elements import ObjectSelectionElements, ParameterSettingsElements, RenderSettingsElements, DataElements, EnvironmentsDropdown

class VIEW3D_PT_assets(Panel):
    bl_idname = "VIEW3D_PT_assets"
    bl_label = "Assets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GB-Assets"

    def draw(self, ctx: Context):
        layout = self.layout
        props = ctx.scene.environment_dropdown

        row = layout.row()
        row.operator("asset.add_bin", text='Import Bin', icon="IMPORT")
        layout.label(text="Select an Environment:")
        layout.prop(props, "dropdown_option", text="")

    def register():
        Scene.environment_dropdown = bpy.props.PointerProperty(type=EnvironmentsDropdown)

    def unregister():
        del Scene.environment_dropdown


class VIEW3D_PT_objects(Panel):
    bl_idname = "VIEW3D_PT_objects"
    bl_label = "Objects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GB-Render"

    def draw(self, ctx: Context):
        layout = self.layout
        props = ctx.scene.object_selection_elements

        layout.label(text="Select Objects:")
        layout.prop_search(props, "grease", bpy.data, "objects", text="Bin")
        layout.prop_search(props, "camera", bpy.data, "objects", text="Camera")
        layout.prop_search(props, "camera_track", bpy.data, "objects", text="Cam Track")
        layout.prop_search(props, "bin_cutter", bpy.data, "objects", text="Grease Cutter")
        layout.prop_search(props, "seg_bin_cutter", bpy.data, "objects", text="Seg Cutter")
        layout.prop_search(props, "rgb_bin", bpy.data, "collections", text="RGB Bin")
        layout.prop_search(props, "seg_bin", bpy.data, "collections", text="SEG Bin")
        

    def register():
        Scene.object_selection_elements = bpy.props.PointerProperty(type=ObjectSelectionElements)

    def unregister():
        del Scene.object_selection_elements

class VIEW3D_PT_seg_colors(Panel):
    bl_idname = "VIEW3D_PT_seg_colors"
    bl_label = "Segmentation Colors"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GB-Render"

    def draw(self, ctx: Context):
        layout = self.layout

        row = layout.row()
        row.operator("asset.query_seg_materials", text='Query Segmentation Materials', icon="HELP")        

        # Display the queried materials
        queried_seg_materials = ctx.scene.queried_seg_materials
        if queried_seg_materials:
            for item in queried_seg_materials:
                box = layout.box()
                box.label(text=item.material.name)
                self.display_rgb_node(item.material, box)

    def display_rgb_node(self, material: Material, layout):
        """
        Display the RGB node's color input socket for the given material.
        """
        if material and material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'RGB':  # Check if the node is an RGB node
                    layout.prop(node.outputs[0], "default_value", text="Color")

class VIEW3D_PT_materials(Panel):
    bl_idname = "VIEW3D_PT_materials"
    bl_label = "Materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GB-Render"

    def draw(self, ctx: Context):
        layout = self.layout

        row = layout.row()
        row.operator("asset.query_materials", text='Query Materials', icon="HELP")        

        # Display the queried materials
        queried_materials = ctx.scene.queried_materials
        if queried_materials:
            for item in queried_materials:
                box = layout.box()
                box.label(text=item.material.name)
                self.display_nodes_for_mat(item.material, 'settings', box)

    def display_nodes_for_mat(self, material: Material, node_name: str, layout):
        # Display nodes only if a material is selected
        if material and material.use_nodes:
            for node in material.node_tree.nodes:
                if node.name == node_name:  # Only display the specified named node
                    self.draw_node_inputs(layout, node)

    def draw_node_inputs(self, layout, node):
        # Display the inputs of the selected node
        for input_socket in node.inputs:
            if input_socket.is_linked:  # If the socket is linked to other nodes
                layout.label(text=f"{input_socket.name}: Linked")
            else:
                if hasattr(input_socket, 'default_value'):
                    layout.prop(input_socket, "default_value", text=input_socket.name)
        
class WM_OT_parameter_tuning(Operator):
    bl_idname = 'wm.parameter_tuning'
    bl_label = 'Parameter Settings'
    bl_description = "Adjust parameters for environment set up"
    bl_options = {"REGISTER"}

    def invoke(self, ctx: Context, event: Event):
        wm = ctx.window_manager
        return wm.invoke_props_dialog(self, width=500)
    
    def draw(self, ctx: Context):
        props = ctx.scene.parameter_settings_elements
        layout = self.layout

        layout.label(text="Grease Settings:")
        box = layout.box()
        row = box.row()
        row.label(text="Starting Liquid Level:", icon='RIGID_BODY')
        row.prop(props, 'starting_liquid_level')

        row = box.row()
        row.label(text="Liquid Level Step:", icon='TRACKING_BACKWARDS_SINGLE')
        row.prop(props, 'liquid_level_step')

        layout.separator(factor= 1)

        layout.label(text="Camera Movement (Extrinsic):")
        box = layout.box()
        box.label(text="Azimuth Settings:")
        azimuth_settings = box.box()
        row = azimuth_settings.row()
        row.label(text= "Azimuth Step:", icon = 'ARROW_LEFTRIGHT')
        row.prop(props, "azimuth_step")

        box.label(text="Elevation Settings")
        elevation_settings = box.box()
        row = elevation_settings.row()
        row.label(text= "Starting Elevation:", icon = 'DOT')
        row.prop(props, "starting_elevation")

        row = elevation_settings.row()
        row.label(text= "Max Elevation:", icon = 'EMPTY_SINGLE_ARROW')
        row.prop(props, "max_elevation")

        row = elevation_settings.row()
        row.label(text= "Elevation Step:", icon = 'EVENT_UP_ARROW')
        row.prop(props, "elevation_step")

        box.label(text="Zoom Settings")
        zoom_settings = box.box()
        row = zoom_settings.row()
        row.label(text= "Starting Zoom:", icon = 'ZOOM_ALL')
        row.prop(props, "starting_zoom")

        row = zoom_settings.row()
        row.label(text= "Zoom Step:", icon = 'ZOOM_IN')
        row.prop(props, "zoom_step")

        row = zoom_settings.row()
        row.label(text= "Zoom Levels:", icon = 'ZOOM_SELECTED')
        row.prop(props, "zoom_levels")

        layout.separator(factor= 1)

        layout.label(text="Camera Properties (Intrinsic):")
        box = layout.box()
        row = box.row()
        row.label(text= "Focal Length", icon = 'VIEW_CAMERA')
        row.prop(props, "focal_length")

    def execute(self, ctx: Context):
        return {"FINISHED"}
    
    def register():
        Scene.parameter_settings_elements = bpy.props.PointerProperty(type=ParameterSettingsElements)

    def unregister():
        del Scene.parameter_settings_elements
    
class WM_OT_render_settings(Operator):
    bl_idname = 'wm.render_settings'
    bl_label = 'Render Settings'
    bl_description = "Adjust render settings"
    bl_options = {"REGISTER"}

    def invoke(self, ctx: Context, event: Event):
        wm = ctx.window_manager
        return wm.invoke_props_dialog(self, width=700)
    
    def draw(self, ctx: Context):
        props = ctx.scene.render_settings_elements
        layout = self.layout

        row = layout.row()
        row.label(text='File Settings:')
        box = layout.box()
        row = box.row()
        row.prop(props, 'directory')
        row = box.row()
        row.prop(props, 'mask_prefix')
        row.prop(props, 'image_prefix')
        row = box.row()
        row.prop(props, 'dataset_name')

        row = layout.row()
        row.label(text='Image Quality Settings')
        box = layout.box()
        row = box.row()
        row.prop(props, 'width')
        row.prop(props, 'height')
        row = box.row()
        row.prop(props, 'sample_amount')
        row = box.row()
        row.prop(props, 'subset_size')

        row = layout.row()
        row.label(text='Render Sequence')
        row.prop(props, 'render_sequence')

    def execute(self, ctx: Context):
        return {"FINISHED"}
    
    def register():
        Scene.render_settings_elements = bpy.props.PointerProperty(type=RenderSettingsElements)

    def unregister():
        del Scene.render_settings_elements
    
class VIEW3D_PT_controls(Panel):
    bl_idname = "VIEW3D_PT_controls"
    bl_label = "Rendering"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GB-Render"
    
    def draw (self, ctx: Context):
        layout = self.layout
        data = ctx.scene.gb_data

        box = layout.box()
        row = box.row()
        row.operator("wm.parameter_tuning", text="Adjust Parameters", icon="SETTINGS")

        row = box.row()
        row.operator("wm.render_settings", text="Adjust Render Settings", icon="SETTINGS")

        layout.separator(factor=1)
        box = layout.box()
        row = box.row()
        row.operator("render.render_generated_animation", text=f'Render Images ({data.render_estimate} Frames)', icon="RENDER_RESULT")

    def register():
        Scene.gb_data = bpy.props.PointerProperty(type=DataElements)

    def unregister():
        del Scene.gb_data
    