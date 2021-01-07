A Blender addon for converting HWM (hardware morph) models from Source 1 to Source 2. Only tested with Team Fortress 2 models, but should work with most custom content as well.

Also includes a Source 2 prefab for automatically setting up flex controllers.

Instructions:

1. Install Rectus's fork of Blender Source Tools: https://github.com/Rectus/BlenderSourceTools. The original will not work.

2. Install my addon, hosted here on this Github page.

3. Copy "hwmcontrols.vmdl_prefab" to "C:\Program Files (x86)\Steam\steamapps\common\Half-Life Alyx\content\hlvr_addons\YOURADDONNAME\models\player\hwm\prefabs\"

3. Decompile your model with Crowbar.

3. In the HWMTools panel (openable with the "N" key), set the path to your decompiled .qc file and the location where you want to export your .dmx files for Source 2. Adjust other settings as you see fit.

4. Hit "Import and Process"

5. Go to the "Scene" tab (picture of a cone and circle on the right), then press the "Export" button. You will be given a drop-down, press "Scene export".

6. Open up Source 2, import your model as normal. Press the "add" button, and search for "Prefab". When asked to choose a path, select the attached "hwmcontrols.vmdl_prefab".

7. Hit "add" again, and search for "ComputeWrinkleMap". Add it, and select the mesh that contains the character's head. Set "Compress Scale" to "-5", and "Stretch Scale" to "5".

8. Done! If the face dosn't move, make sure you have "Morph Supported" and "Wrinkle" checked in your head material. For the eye material, you should use "materials\models\player\shared\eye-iris-blue.vtf" from Team Fortress 2.