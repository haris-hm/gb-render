import bpy
import os

from bpy.types import Scene
from enum import Enum

class FrameType(Enum):
    MASK = 'mask'
    RAW = 'raw'

class EngineType(Enum):
    EEVEE = 'BLENDER_EEVEE_NEXT'
    CYCLES = 'CYCLES'

class CameraData():
    def __init__(self, azimuth: int=0, elevation: int=0, focal_length: int=35):
        self.__azimuth = azimuth
        self.__elevation = elevation
        self.__focal_length = focal_length  

class RenderFrame():
    def __init__(self, root_path: str, file_name: str, scene: Scene, type: FrameType, camera_data: CameraData=CameraData(), width: int=1920, height: int=1080, samples: int=1024):
        self.__filepath = os.path.join(root_path, f'{file_name}_{type.value}.png')
        self.__scene = scene
        self.__engine = EngineType.CYCLES if type == FrameType.RAW else EngineType.EEVEE
        self.__width = width
        self.__height = height
        self.__samples = samples if type == FrameType.RAW else None
        self.__camera_data = camera_data

    def render(self):
        switch_engine(self.__scene, self.__engine, self.__width, self.__height, self.__samples)
        self.__scene.render.filepath = self.__filepath
        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)  

def toggle_shadows(scene: Scene, val: bool):
    for obj in scene.objects:
        if hasattr(obj, "visible_shadow"):
            obj.visible_shadow = val
            print(f'Shadows {"enabled" if val else "disabled"}.')
        else:
            raise Exception('Invalid object.')

def switch_engine(scene: Scene, engine: EngineType, width: int, height: int, samples: int=None):
    if (samples == None and engine == EngineType.CYCLES):
        raise Exception('Cycles must have a sample amount specified.')
    
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.engine = engine.value

    # Toggle settings for rendering seg masks
    if engine == EngineType.CYCLES:
        scene.cycles.samples = samples
        toggle_shadows(scene, True)
        scene.view_settings.view_transform = 'AgX'
    else:
        toggle_shadows(scene, False)
        scene.view_settings.view_transform = 'Raw'

def create_frames(scene: Scene) -> list[RenderFrame]:
    frames: list[RenderFrame] = [
        RenderFrame(r'C:\Users\haris\OneDrive - Drake University\Documents\GB-Research\Bin Modeling\Renders\test', 'test_render', scene, FrameType.RAW, samples=1),
        RenderFrame(r'C:\Users\haris\OneDrive - Drake University\Documents\GB-Research\Bin Modeling\Renders\test', 'test_render', scene, FrameType.MASK)
    ]

    return frames
