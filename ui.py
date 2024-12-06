import bpy

from bpy.props import *
from bpy.types import PropertyGroup, Panel, Object, Context, Scene, Operator, Event, Node, Material

def update_render_btn(self, ctx: Context):
    azimuth_step = self.azimuth_step
    elevation_step = self.elevation_step
    max_elevation = self.max_elevation

    estimate = (360/azimuth_step) * ((max_elevation/elevation_step)+1)
    if (int(self.render_sequence) == 0 or int(self.render_sequence) == 1):
        estimate *= 2

    self.render_estimate = int(round(estimate))

    for area in ctx.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'UI':
                    region.tag_redraw()
class UIProperties(PropertyGroup):
    grease: PointerProperty(
        name = 'Bin',
        type = Object,
        description = 'Select the bin',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) # type: ignore

    camera: PointerProperty(
        name = 'Camera',
        type = Object,
        description = 'Select the camera',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) # type: ignore

    camera_track: PointerProperty(
        name = 'Camera Track',
        type = Object,
        description = 'Select the camera track curve',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) # type: ignore

    bin_cutter: PointerProperty(
        name = 'Bin Cutter',
        type = Object,
        description = 'Select the bin cutter',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) # type: ignore

    liquid_level: IntProperty(
        name = 'Liquid Level',
        default = 100,
        min = 0,
        max = 100,
        subtype = 'PERCENTAGE'
    ) # type: ignore

    azimuth_step: IntProperty(
        name = 'Azimuth Step',
        default = 10,
        min = 1,
        max = 360,
        subtype = 'FACTOR',
        update = update_render_btn
    ) # type: ignore

    elevation_step: IntProperty(
        name = 'Elevation Step',
        default = 10,
        min = 1,
        max = 360,
        subtype = 'FACTOR',
        update = update_render_btn
    ) # type: ignore

    max_elevation: IntProperty(
        name = 'Max Elevation',
        default = 60,
        min = 0,
        max = 90,
        subtype = 'FACTOR',
        update = update_render_btn
    ) # type: ignore

    focal_length: IntProperty(
        name = 'Focal length',
        default = 50,
        min = 1,
        max = 150,
        subtype = 'DISTANCE_CAMERA'
    ) # type: ignore

    render_estimate: IntProperty(
        name='Render Estimate',
        default=int(round((360/10) * ((90/10)+1)))
    ) # type: ignore

    render_sequence: EnumProperty(
        items = [
            ('0', 'Pairs', 'The raw image is rendered, subsequently followed by rendering the mask image', '', 0),
            ('1', 'Masks then Images', 'All masks are rendered, followed by all images', '', 1),
            ('2', 'Images Only', 'Only the images are rendered', '', 2),
            ('3', 'Masks Only', 'Only the masks are rendered', '', 3)
        ],
        name = '',
        default = '1',
        update = update_render_btn
    )  # type: ignore

    directory: StringProperty(
        name = 'Directory',
        subtype ='DIR_PATH'
    ) # type: ignore

    mask_prefix: StringProperty(
        name = 'Mask Prefix',
        default = 'MASK'
    ) # type: ignore

    image_prefix: StringProperty(
        name = 'Image Prefix',
        default = 'RGB'
    ) # type: ignore

    sample_amount: IntProperty(
        name = 'Sample Amount',
        default = 256,
        min = 1,
        max = 2048
    ) # type: ignore

    width: IntProperty(
        name = 'Width',
        default = 1920,
        min = 1,
    ) # type: ignore

    height: IntProperty(
        name = 'Height',
        default = 1080,
        min = 1
    ) # type: ignore

    render_progress: FloatProperty(
        name = 'Render Progress',
        min = 0,
        max = 1,
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) # type: ignore

    show_render_progress: BoolProperty(
        name = 'Show Render Progress',
        default = False
    ) # type: ignore

class MaterialProperties(PropertyGroup):
    bin_int_mat: PointerProperty(
        name = 'Interior',
        type = Material,
        description = 'Select the bin interior material'
    ) # type: ignore

    bin_ext_mat: PointerProperty(
        name = 'Exterior',
        type = Material,
        description = 'Select the bin exterior material'
    ) # type: ignore

    grease_mat: PointerProperty(
        name = 'Grease',
        type = Material,
        description = 'Select the grease material'
    ) # type: ignore

    grease_group: bpy.props.StringProperty(
        name="Group",
        description="Select the grease node group"
    ) # type: ignore

    bin_ext_group: bpy.props.StringProperty(
        name="Group",
        description="Select the bin node group"
    ) # type: ignore

    bin_int_group: bpy.props.StringProperty(
        name="Group",
        description="Select the bin node group"
    ) # type: ignore

class VIEW3D_PT_objects(Panel):
    bl_idname = "VIEW3D_PT_objects"
    bl_label = "Objects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Grease Bin Rendering"

    def draw(self, ctx: Context):
        layout = self.layout
        props = ctx.scene.ui_properties

        layout.label(text="Select Objects:")
        layout.prop_search(props, "grease", bpy.data, "objects", text="Bin")
        layout.prop_search(props, "camera", bpy.data, "objects", text="Camera")
        layout.prop_search(props, "camera_track", bpy.data, "objects", text="Cam Track")
        layout.prop_search(props, "bin_cutter", bpy.data, "objects", text="Bin Cutter")

class VIEW3D_PT_materials(Panel):
    bl_idname = "VIEW3D_PT_materials"
    bl_label = "Materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Grease Bin Rendering"

    def draw(self, ctx: Context):
        layout = self.layout
        mat_props = ctx.scene.material_properties

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

    def display_nodes_for_mat(self, material: Material, group: str, group_name: str, props: MaterialProperties, layout):
        # Display nodes only if a material is selected
        if material and material.use_nodes:
            node_tree = material.node_tree
            
            # Populate a dropdown with node names from the material's node tree
            node_names = [node.name for node in node_tree.nodes]
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
        Scene.material_properties = bpy.props.PointerProperty(type=MaterialProperties)

    def unregister():
        del Scene.material_properties

class VIEW3D_PT_controls(Panel):
    bl_idname = "VIEW3D_PT_controls"
    bl_label = "Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Grease Bin Rendering"
    
    def draw (self, ctx: Context):
        layout = self.layout
        props = ctx.scene.ui_properties

        box = layout.box()
        row = box.row()
        row.operator("wm.parameter_tuning", text="Adjust Parameters", icon="SETTINGS")

        row = box.row()
        row.operator("wm.render_settings", text="Adjust Render Settings", icon="SETTINGS")

        layout.separator(factor=1)

        row = self.layout.row()
        row.operator("render.render_queued_items", text=f'Render ({props.render_estimate} Images)', icon="RENDER_RESULT")
        if props.show_render_progress == True:
            row = self.layout.row()
            row.progress(factor=props.render_progress)

        layout.separator(factor=1)
        row = self.layout.row()
        row.operator("render.render_as_animation", text=f'Render as Animation ({props.render_estimate} Frames)', icon="RENDER_RESULT")

    def register():
        Scene.ui_properties = bpy.props.PointerProperty(type=UIProperties)

    def unregister():
        del Scene.ui_properties
        
class WM_OT_parameter_tuning(Operator):
    bl_idname = 'wm.parameter_tuning'
    bl_label = 'Parameter Settings'

    def invoke(self, ctx: Context, event: Event):
        wm = ctx.window_manager
        return wm.invoke_props_dialog(self, width=500)
    
    def draw(self, ctx: Context):
        props = ctx.scene.ui_properties
        layout = self.layout

        layout.label(text="Camera Movement (Extrinsic):")
        box = layout.box()
        row = box.row()
        row.label(text="Liquid Level:", icon='DOT')
        row.prop(props, 'liquid_level')

        layout.separator(factor= 1)

        layout.label(text="Camera Movement (Extrinsic):")
        box = layout.box()
        row = box.row()
        row.label(text= "Azimuth Step:", icon = 'ARROW_LEFTRIGHT')
        row.prop(props, "azimuth_step")

        row = box.row()
        row.label(text= "Elevation Step:", icon = 'EVENT_UP_ARROW')
        row.prop(props, "elevation_step")

        row = box.row()
        row.label(text= "Max Elevation", icon = 'EMPTY_SINGLE_ARROW')
        row.prop(props, "max_elevation")

        layout.separator(factor= 1)

        layout.label(text="Camera Properties (Intrinsic):")
        box = layout.box()
        row = box.row()
        row.label(text= "Focal Length", icon = 'VIEW_CAMERA')
        row.prop(props, "focal_length")

    def execute(self, ctx: Context):
        return {"FINISHED"}
    
    
class WM_OT_render_settings(Operator):
    bl_idname = 'wm.render_settings'
    bl_label = 'Render Settings'

    def invoke(self, ctx: Context, event: Event):
        wm = ctx.window_manager
        return wm.invoke_props_dialog(self, width=700)
    
    def draw(self, ctx: Context):
        props = ctx.scene.ui_properties
        layout = self.layout

        row = layout.row()
        row.label(text='File Settings:')
        box = layout.box()
        row = box.row()
        row.prop(props, 'directory')
        row = box.row()
        row.prop(props, 'mask_prefix')
        row.prop(props, 'image_prefix')

        row = layout.row()
        row.label(text='Image Quality Settings')
        box = layout.box()
        row = box.row()
        row.prop(props, 'width')
        row.prop(props, 'height')
        row = box.row()
        row.prop(props, 'sample_amount')

        row = layout.row()
        row.label(text='Render Sequence (Render Only)')
        row.prop(props, 'render_sequence')
        row = layout.row()
        row.label(text='Note: Render sequence settings only works when not rendering as an animation. Animations always render all masks, then all images.')

    def execute(self, ctx: Context):
        return {"FINISHED"}