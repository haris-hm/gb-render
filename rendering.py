import bpy 

from bpy.types import Operator, Scene, Context, Event
from .gb_utils import *

class RENDER_OT_render_pairs(Operator):
    """
    Adapted from: https://blender.stackexchange.com/a/71830    
    """

    bl_idname = "render.render_pairs"
    bl_label = "Render Pairs"

    timer = None
    frames: RenderQueue = None
    stop: bool = None
    rendering: bool = None

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

def create_frames(scene: Scene) -> RenderQueue:
    props: UIProperties = scene.ui_properties
    liquid_level: int = props.liquid_level
    azimuth_step: int = props.azimuth_step
    elevation_step: int = props.elevation_step
    max_elevation: int = props.max_elevation
    focal_length: int = props.focal_length

    raw_frames: RenderQueue = RenderQueue()
    mask_frames: RenderQueue = RenderQueue()

    curr_azimuth: int = 0
    curr_elevation: int = 0
    file_name_counter = 0

    while curr_elevation <= max_elevation:
        while curr_azimuth <= 360:
            scene_data: SceneData = SceneData(scene, curr_azimuth, curr_elevation, max_elevation, focal_length, liquid_level)
            print(f'Doing: {curr_elevation=}, {curr_azimuth=}')

            raw_frames.add(RenderFrame(
                r'C:\Users\haris\OneDrive - Drake University\Documents\GB-Research\Bin Modeling\Renders\test\raw',
                f'test_render_{file_name_counter:>06}',
                scene,
                FrameType.RAW,
                scene_data,
                samples=1
            ))
            mask_frames.add(RenderFrame(
                r'C:\Users\haris\OneDrive - Drake University\Documents\GB-Research\Bin Modeling\Renders\test\mask',
                f'test_render_{file_name_counter:>06}',
                scene,
                FrameType.MASK,
                scene_data
            ))

            file_name_counter += 1
            curr_azimuth += azimuth_step

        curr_elevation += elevation_step
        curr_azimuth = 0

    

    return raw_frames
