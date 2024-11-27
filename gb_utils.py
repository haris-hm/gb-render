import bpy
import os

from bpy.types import Scene, Object
from enum import Enum
from .ui import UIProperties

class FrameType(Enum):
    MASK = 'mask'
    RAW = 'raw'

class EngineType(Enum):
    EEVEE = 'BLENDER_EEVEE_NEXT'
    CYCLES = 'CYCLES'

class SceneData():
    __camera: Object = None
    __camera_track: Object = None
    __bin_cutter: Object = None
    __bin: Object = None

    def __init__(self, scene: Scene, azimuth: int=0, elevation: int=0, max_elevation=90, focal_length: int=35, liquid_level:int=100):
        self.__scene = scene
        self.__azimuth = azimuth
        self.__elevation = elevation
        self.__max_elevation = max_elevation
        self.__focal_length = focal_length  
        self.__liquid_level = liquid_level

    def setup_scene(self):
        self.__get_scene_objects()
        self.__camera.constraints["Follow Path"].offset_factor += self.__azimuth/360
        self.__camera_track.location.z += 1/self.__elevation if self.__elevation > 0 else 0

    def __get_scene_objects(self):
        ui_props = self.__scene.ui_properties
        self.__camera = ui_props.camera
        self.__camera_track = ui_props.camera_track
        self.__bin_cutter = ui_props.bin_cutter
        self.__bin = ui_props.bin
        
        # Object Validation
        if(self.__camera == None or self.__camera.type != 'CAMERA'):
            self.__camera = None
            raise Exception('Invalid camera object. Please pick a camera in the scene.')
        
        elif(self.__camera_track == None or self.__camera_track.type != 'CURVE'):
            self.__camera_track = None
            raise Exception('Invalid camera track object. Please pick a curve object.')

        elif(self.__bin_cutter == None or self.__bin_cutter.type != 'MESH'):
            self.__bin_cutter = None
            raise Exception('Invalid bin cutter object. Please pick a mesh object.')
        
        # Constraint Validation
        try: 
            self.__camera.constraints["Follow Path"].use_fixed_location = True
            self.__camera.constraints["Follow Path"].use_curve_follow = True
            self.__camera.constraints["Follow Path"].target = self.__camera_track
        except:
            raise Exception("Please add a \"Follow Path\" constraint onto the camera.")

class RenderFrame():
    def __init__(self, root_path: str, file_name: str, scene: Scene, type: FrameType, scene_data: SceneData, width: int=1920, height: int=1080, samples: int=1024):
        self.__filepath = os.path.join(root_path, f'{file_name}_{type.value}.png')
        self.__scene = scene
        self.__engine = EngineType.CYCLES if type == FrameType.RAW else EngineType.EEVEE
        self.__width = width
        self.__height = height
        self.__samples = samples if type == FrameType.RAW else None
        self.__scene_data = scene_data

    def render(self):
        self.__switch_engine()
        self.__scene_data.setup_scene()
        self.__scene.render.filepath = self.__filepath
        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)  

    def __toggle_shadows(self, val: bool):
        for obj in self.__scene.objects:
            if hasattr(obj, "visible_shadow"):
                obj.visible_shadow = val
                print(f'Shadows {"enabled" if val else "disabled"}.')
            else:
                raise Exception('Invalid object.')

    def __switch_engine(self):
        if (self.__samples == None and self.__engine == EngineType.CYCLES):
            raise Exception('Cycles must have a sample amount specified.')
        
        self.__scene.render.resolution_x = self.__width
        self.__scene.render.resolution_y = self.__height
        self.__scene.render.engine = self.__engine.value

        # Toggle settings for rendering seg masks
        if self.__engine == EngineType.CYCLES:
            self.__scene.cycles.samples = self.__samples
            self.__toggle_shadows(True)
            self.__scene.view_settings.view_transform = 'AgX'
        else:
            self.__toggle_shadows(False)
            self.__scene.view_settings.view_transform = 'Raw'

def create_frames(scene: Scene) -> list[RenderFrame]:
    props: UIProperties = scene.ui_properties

    liquid_level: int = props.liquid_level

    azimuth_step: int = props.azimuth_step
    elevation_step: int = props.elevation_step
    max_elevation: int = props.max_elevation
    focal_length: int = props.focal_length

    # frames: list[RenderFrame] = [
    #     RenderFrame(r'C:\Users\haris\OneDrive - Drake University\Documents\GB-Research\Bin Modeling\Renders\test', 'test_render', scene, FrameType.RAW, SceneData(scene), samples=1),
    #     RenderFrame(r'C:\Users\haris\OneDrive - Drake University\Documents\GB-Research\Bin Modeling\Renders\test', 'test_render', scene, FrameType.MASK, SceneData(scene))
    # ]

    frames: list[RenderFrame] = []
    curr_azimuth: int = 0
    curr_elevation: int = 0
    file_name_counter = 0
    while curr_azimuth <= 360:
        while curr_elevation <= max_elevation:
            scene_data: SceneData = SceneData(scene, curr_azimuth, curr_elevation, max_elevation, focal_length, liquid_level)
            print(f'Doing: {curr_elevation=}, {curr_azimuth=}')

            frames.append(RenderFrame(
                r'C:\Users\haris\OneDrive - Drake University\Documents\GB-Research\Bin Modeling\Renders\test\raw',
                f'test_render_{file_name_counter:>06}',
                scene,
                FrameType.RAW,
                scene_data,
                samples=1
            ))
            frames.append(RenderFrame(
                r'C:\Users\haris\OneDrive - Drake University\Documents\GB-Research\Bin Modeling\Renders\test\mask',
                f'test_render_{file_name_counter:>06}',
                scene,
                FrameType.MASK,
                scene_data
            ))

            curr_azimuth += azimuth_step
            curr_elevation += elevation_step

        curr_elevation = 0

    return frames
