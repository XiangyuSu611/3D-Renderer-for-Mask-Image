# 3D-Renderer-for-Mask-Image
This script is designed to render **mask** and RGB image for 3D objects.

Used software: Blender (tested on version [2.83](https://download.blender.org/release/), [2.79](https://download.blender.org/release/)).

Supported 3D format: .obj. 

Here are some examples.

![RGB](https://github.com/XiangyuSu611/3D-Renderer-for-Mask-Image/blob/main/ADE_val_00000631.jpg)
![MASK_PART](https://github.com/XiangyuSu611/3D-Renderer-for-Mask-Image/blob/main/ADE_val_00000631.png)

Please notice that the second picture is not original materials desiged in ShapeNet, we use part segmentation produced by [Yi Li et al](https://cs.stanford.edu/~ericyi/project_page/part_annotation/).
And of course you can use original meterials provided by ShapeNet.

## How to Use

* First, this script is running on Blender, so please download Blender on Linux first. We recommend to use Blender 2.79.
* Second, please extract Blender, and then you can run these script.
### Render single object.
Run the following command:
```
/home/xiangyu/blender-2.79-1/blender --background --python /home/xiangyu/software/segmentation_render/render_mask_2.79.py -- --output_folder /home/xiangyu/software/mat1 {} \;
```
### Render many objects.
```
find /home/xiangyu/models/obj_change/ -name *.obj -exec /home/xiangyu/blender-2.79-1/blender --background --python /home/xiangyu/software/segmentation_render/render_mask_2.79.py -- --output_folder /home/xiangyu/software/mat1 {} \;
```
## Some options 
* views 
(Number of views to be rendered.)
* output_folder
(The path the output will be dumped to.)
* cam_mode
(Camera position sampling method, sphere or circle.)
* obj_path
(Path to target obj file.)
