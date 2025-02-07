# GB-Render

Addon designed to streamline the process of rendering grease bins for our research project.

## Installation
1. Download the zip file from releases.
2. Open Blender and go to `Edit > Preferences > Add-ons`, or press `Ctrl+,` and go to `Add-ons`.
3. Click on the drop down arrow in the top right of the window.
4. Select `Install from Disk...`.
5. Navigate to your downloads folder, select the zip file, and click `Install from Disk`.
6. Double check the addon is enabled in the addon list. There should be a checkmark next to `GB-Render`.

## Quickstart Guide
1. Access the addon's panel in the 3D viewport.
    - Hit `N` while in the viewport and click on `GB-Render`.
2. Select all the relevant objects in the `Objects` category.
3. Select the relevant materials in the `Materials` category in order to more easily tweak the settings.
4. Adjust parameters by clicking `Adjust Parameters`.
5. Configure the render settings by clicking `Render Settings`.
    - Make sure to select an empty folder as the directory.
    - Also ensure you have selected the correct sequence to render images in.
6. Click render and wait.

## Adjustable Parameters
### Liquid Level
`Liquid Level` defines how high the liquid in the bin will be.
- 0% would be no liquid in the bin, 100% would be a full bin.
- Works by setting the height of the selected `Bin Cutter` object

### Extrinsic Camera Properties
`Azimuth Step` defines how many degrees the camera will rotate around the bin 
horizontally every keyframe.
- For each full orbit around the bin, $\alpha=\frac{360}{\text{Azimuth Step}}$ frames will be rendered.

`Elevation Step` defines how many degrees the camera will rotate around the bin vertically after going 360° around it horizontally.
- For each elevation, the camera will orbit fully around the bin. 
- The camera will keep rotating vertically until it hits the `Max Elevation` parameter (capped at 90°, which would looking directly down at the bin).
- This means that, in total, the amount of frames rendered will be $\alpha\left(\frac{\text{Max Elevation}}{\text{Elevation Step}}\right)$

### Intrinsic Camera Properties
`Focal Length` defines the focal length of the camera.

## Render Settings
`Directory` defines where the files will be saved.
- The addon creates two folders: `images` and `masks`. All RGB images rendered will be saved in the former, whereas all the segmented masks will be saved in the latter.
- `Image Prefix` and `Mask Prefix` define the prefix for the file name of each image type. Currently, the file name structure is `[prefix]_[four digit padded number]`.
`Width` and `Height` define the resolution of the rendered images.
- `Sample Amount` defines how many samples cycles will use when rendering RGB images. The higher the sample amount, the slower it will render. Don't set this to a high amount if you aren't using a dedicated GPU.

`Render Sequence` will define the order in which images will be rendered.
- `Masks then Images` renders all the masks first, followed by all the RGB images. This will take the most amount of time.
- `Images Only` and `Masks Only` renders only its respective image type.
- If you ever want to cancel a render, just click on the main Blender window and hit the escape key.

When you're ready to render, just hit the `Render Images` button. The button will provide an estimate as to how many frames it will render.


