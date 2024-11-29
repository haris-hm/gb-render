import bpy 
import threading

from bpy.types import Operator, Scene, Context, Event
from .gb_utils import *
from .ui import UIProperties

class RENDER_OT_render_queued_items(Operator):
    """
    Adapted from: https://blender.stackexchange.com/a/71830    
    """

    bl_idname = "render.render_queued_items"
    bl_label = "Render Images"
    bl_description = "Renders all images in the render queue. Make sure to select all relevant objects"
    bl_options = {"REGISTER"}

    timer = None
    frames: RenderQueue = None
    stop: bool = None
    rendering: bool = None

    # @classmethod
    # def poll(cls, ctx: Context):
    #     try:
    #         get_objects(ctx.scene)
    #         return True
    #     except:
    #         return False

    def pre(self, scene: Scene, ctx: Context=None):
        self.rendering = True

    def post(self, scene: Scene, ctx: Context=None):
        self.rendering = False
    
    def cancelled(self, scene: Scene, ctx: Context=None):
        self.stop = True

    def execute(self, ctx: Context):
        self.stop = False
        self.rendering = False

        try:
            get_objects(ctx.scene)

            if(not self.__is_path_valid(bpy.path.abspath(ctx.scene.ui_properties.directory))):
                raise Exception('Please choose a valid path under "Adjust Render Settings"')
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        self.frames = create_frames(ctx.scene)

        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)

        self.timer = ctx.window_manager.event_timer_add(0.5, window=ctx.window)
        ctx.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}
    
    def modal(self, ctx: Context, event: Event):
        if event.type == 'TIMER':
            if True in (not self.frames, self.stop is True): 
                bpy.app.handlers.render_pre.remove(self.pre)
                bpy.app.handlers.render_post.remove(self.post)
                bpy.app.handlers.render_cancel.remove(self.cancelled)
                ctx.window_manager.event_timer_remove(self.timer)
                
                return {"FINISHED"}
            elif self.rendering is False:
                try:
                    self.frames.pop().render()
                except Exception as e:
                    self.report({"ERROR"}, str(e))
                    return {"CANCELLED"}
                
        return {"PASS_THROUGH"}
    
    def __is_path_valid(self, path) -> bool:
        if (os.path.exists(path) and os.path.isdir(os.path.abspath(path)) and path != ''):
            return True
        else:
            return False

def create_frames(scene: Scene) -> RenderQueue:
    props: UIProperties = scene.ui_properties

    # Scene Settings
    liquid_level: int = props.liquid_level
    azimuth_step: int = props.azimuth_step
    elevation_step: int = props.elevation_step
    max_elevation: int = props.max_elevation
    focal_length: int = props.focal_length

    # Render Settings
    directory: str = bpy.path.abspath(props.directory)
    mask_dir: str = os.path.join(directory, 'masks')
    image_dir: str = os.path.join(directory, 'images')
    sequence_setting: int = int(props.render_sequence)
    mask_prefix: str = props.mask_prefix
    image_prefix: str = props.image_prefix
    sample_amount: int = props.sample_amount
    width: int = props.width
    height: int = props.height

    # Creating Directories
    if (not os.path.exists(mask_dir)):
        os.mkdir(mask_dir)
    if (not os.path.exists(image_dir)):
        os.mkdir(image_dir)

    # Loop variables
    image_frames: RenderQueue = RenderQueue()
    mask_frames: RenderQueue = RenderQueue()
    paired_frames: RenderQueue = RenderQueue()

    curr_azimuth: int = 0
    curr_elevation: int = 0
    file_name_counter = 0

    while curr_elevation <= max_elevation:
        while curr_azimuth < 360:
            scene_data: SceneData = SceneData(scene, curr_azimuth, curr_elevation, focal_length, liquid_level)
            mask_file_name = f'{mask_prefix}_{file_name_counter:>08}'
            image_file_name = f'{image_prefix}_{file_name_counter:>08}'
            print(f'Doing: {curr_elevation=}, {curr_azimuth=}')

            image = RenderFrame(image_dir, image_file_name, scene, FrameType.RAW, scene_data, width=width, height=height, samples=sample_amount)
            mask = RenderFrame(mask_dir, mask_file_name, scene, FrameType.MASK, scene_data, width=width, height=height)

            image_frames.add(image)
            mask_frames.add(mask)
            paired_frames.add(image).add(mask)

            file_name_counter += 1
            curr_azimuth += azimuth_step

        curr_elevation += elevation_step
        curr_azimuth = 0

    # print(f'{paired_frames=}\n\nmask, image: {mask_frames+image_frames}\n\n{image_frames=}\n\n{mask_frames=}')

    # Return correct render queue
    if sequence_setting == 0:
        return paired_frames
    elif sequence_setting == 1:
        return mask_frames + image_frames
    elif sequence_setting == 2:
        return image_frames
    else:
        return mask_frames
