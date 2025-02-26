import bpy

# from bpy.props import *
from bpy.types import Panel, Context, Scene, Operator, Event, Material

from .ui_elements import ObjectSelectionElements, SegmentationColorsElements, MaterialElements, ParameterSettingsElements, RenderSettingsElements, DataElements

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
        props = ctx.scene.segmentation_colors_elements

        layout.label(text="Configure Colors:")
        box = layout.box()

        row = box.row()
        row.prop(props, "bin_interior", text="Bin Interior")

        row = box.row()
        row.prop(props, "bin_exterior", text="Bin Exterior")

        row = box.row()
        row.prop(props, "bin_rim", text="Bin Rim")

        row = box.row()
        row.prop(props, "grease", text="Grease")
        

    def register():
        Scene.segmentation_colors_elements = bpy.props.PointerProperty(type=SegmentationColorsElements)

    def unregister():
        del Scene.segmentation_colors_elements

class VIEW3D_PT_materials(Panel):
    bl_idname = "VIEW3D_PT_materials"
    bl_label = "Materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GB-Render"

    def draw(self, ctx: Context):
        layout = self.layout
        mat_props = ctx.scene.material_elements

        layout.label(text="Select Materials:")
        box = layout.box()
        row = box.row()
        row.prop(mat_props, "bin_int_mat", text="Interior")
        self.display_nodes_for_mat(mat_props.bin_int_mat, mat_props.bin_int_group, "bin_int_group", mat_props, box)

        box = layout.box()
        row = box.row()
        row.prop(mat_props, "bin_ext_mat", text="Exterior")
        self.display_nodes_for_mat(mat_props.bin_ext_mat, mat_props.bin_ext_group, "bin_ext_group", mat_props, box)
        
        box = layout.box()
        row = box.row()
        row.prop(mat_props, "grease_mat", text="Grease")
        self.display_nodes_for_mat(mat_props.grease_mat, mat_props.grease_group, "grease_group", mat_props, box)

    def display_nodes_for_mat(self, material: Material, group: str, group_name: str, props: MaterialElements, layout):
        # Display nodes only if a material is selected
        if material and material.use_nodes:
            # node_tree = material.node_tree
            
            # Populate a dropdown with node names from the material's node tree
            # node_names = [node.name for node in node_tree.nodes]
            layout.prop_search(props, group_name, material.node_tree, "nodes")
            
            # Display node inputs once a node is selected
            if group:
                selected_node = self.get_selected_node(material.node_tree, group)
                if selected_node:
                    self.draw_node_inputs(layout, selected_node)

    def get_selected_node(self, node_tree, node_name):
        # Retrieve the selected node by name
        for node in node_tree.nodes:
            if node.name == node_name:
                return node
        return None

    def draw_node_inputs(self, layout, node):
        # Display the inputs of the selected node
        for input_socket in node.inputs:
            if input_socket.is_linked:  # If the socket is linked to other nodes
                layout.label(text=f"{input_socket.name}: Linked")
            else:
                if hasattr(input_socket, 'default_value'):
                    layout.prop(input_socket, "default_value", text=input_socket.name)
    
    def register():
        Scene.material_elements = bpy.props.PointerProperty(type=MaterialElements)

    def unregister():
        del Scene.material_elements
        
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
    