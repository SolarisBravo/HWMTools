import bpy
import bmesh
import os
import addon_utils
import io_scene_valvesource
import mathutils
from math import radians

bl_info = {
    "name" : "HWMTools",
    "author" : "Solaris",
    "description" : "A set of tools for converting Source Engine HWM models to Source 2",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D > Toolshelf",
    "warning" : "",
    "category" : "Tools"
}

class Settings(bpy.types.PropertyGroup):

    qcpath : bpy.props.StringProperty(
        name="",
        description="Path to your .qc file",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

    exportpath : bpy.props.StringProperty(
        name="",
        description="Source 2 output path",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

    replaceeyes : bpy.props.BoolProperty(
        name="Replace eyes",
        description="Highly reccomended. Eye animation will not work without this setting",
        default = True) 

    clearnormals : bpy.props.BoolProperty(
        name="Clear normals",
        description="May reduce rendering artifacts, may make them worse",
        default = False) 

    untriangulate : bpy.props.BoolProperty(
        name="Untriangulate",
        description="May reduce rendering artifacts, may make them worse. Automatically enabled with subdivision.",
        default = False) 

    subdivide : bpy.props.BoolProperty(
        name="Subdivide",
        description="Smooths out the mesh. Untriangulate is automatically enabled if this is set to True",
        default = False) 

    subdivision_sharpness : bpy.props.FloatProperty(
        name="Subdivision sharpness",
        description="Determines how smooth the mesh should be in degrees",
        default=50,
        min=1,
        max=179.0)

    eyeoffsetx : bpy.props.FloatProperty(
        name="X",
        description="Determines how smooth the mesh should be in degrees",
        default=0.14498)

    eyeoffsety : bpy.props.FloatProperty(
        name="Y",
        description="Determines how smooth the mesh should be in degrees",
        default=0.4008)

    eyeoffsetz : bpy.props.FloatProperty(
        name="Z",
        description="Determines how smooth the mesh should be in degrees",
        default=0.0199)

class HWMHelpPanel(bpy.types.Panel):
    bl_label = "Info"
    bl_idname = "HWM_PT_HELPPANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category= 'HWM Tools'

    def draw(self, context):
        layouta = self.layout
        scene = context.scene
        toolscene = context.scene.toolscene

        layouta.label(text='Requires Rectus\'s Source Tools fork')

        row = layouta.row()
        row.operator('hwm.help_operator')

class HWM_OT_TEST(bpy.types.Operator):
    bl_label = 'Test'
    bl_description = 'Accesses the "help" page'
    bl_idname = 'hwm.test_operator'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        #Get average vertice location
        mesh = bpy.context.view_layer.objects.active.data
        selected_verts = []
        for vertex in mesh.vertices:
            if vertex.select == True:
                selected_verts.append(vertex)
        vertsx = []
        vertsy = []
        vertsz = []
        for vertex in selected_verts:
            vertsx.append(vertex.co[0])
            vertsy.append(vertex.co[1])
            vertsz.append(vertex.co[2])

        vertsavgx = (sum(vertsx) / len(vertsx))
        vertsavgy = (sum(vertsy) / len(vertsy))
        vertsavgz = (sum(vertsz) / len(vertsz))
        vertsavg = (vertsavgx, vertsavgy, vertsavgz)

        #return vertsavg
        

        return{'FINISHED'}

class HWMToolsPanel(bpy.types.Panel):
    bl_label = "Configuration"
    bl_idname = "HWM_PT_MAINPANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category= 'HWM Tools'

    def draw(self, context):
        layouta = self.layout
        scene = context.scene
        toolscene = context.scene.toolscene
        layouta.label(text='Path to your .QC file:')
        rowa = layouta.row()
        rowa.prop(toolscene, "qcpath")

        layoutb = self.layout
        scene = context.scene
        toolscene = context.scene.toolscene
        layoutb.label(text='Output directory:')
        rowb = layoutb.row()
        rowb.prop(toolscene, "exportpath")

        layoutc = self.layout
        scene = context.scene
        toolscene = context.scene.toolscene
        rowc = layoutc.row()
        rowc.prop(toolscene, "replaceeyes")

        layoutd = self.layout
        scene = context.scene
        toolscene = context.scene.toolscene
        rowd = layoutd.row()
        rowd.prop(toolscene, "clearnormals")

        layoute = self.layout
        scene = context.scene
        toolscene = context.scene.toolscene
        rowe = layoute.row()
        rowe.prop(toolscene, "untriangulate")

        layoutf = self.layout
        scene = context.scene
        toolscene = context.scene.toolscene
        rowf = layoutf.row()
        rowf.prop(toolscene, "subdivide")

        layoutg = self.layout
        scene = context.scene
        toolscene = context.scene.toolscene
        rowg = layoutg.row()
        rowg.prop(toolscene, "subdivision_sharpness")

        layouth = self.layout
        scene = context.scene
        toolscene = context.scene.toolscene
        layouth.label(text='Eye offset:')
        rowh1 = layouth.row()
        rowh1.prop(toolscene, "eyeoffsetx")
        rowh2 = layouth.row()
        rowh2.prop(toolscene, "eyeoffsety")
        rowh3 = layouth.row()
        rowh3.prop(toolscene, "eyeoffsetz")

class HWMToolsPanelB(bpy.types.Panel):
    bl_label = "Tools"
    bl_idname = "HWM_PT_MAINPANELB"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category= 'HWM Tools'

    def draw(self, context):

        layout = self.layout
        scene = context.scene
        toolscene = context.scene.toolscene

        row = layout.row()

        row.operator('hwm.importqc_operator')



class HWM_OT_IMPORTQC(bpy.types.Operator):
    bl_label = 'Import and Process'
    bl_description = 'Imports and processes .QC file'
    bl_idname = 'hwm.importqc_operator'

    def execute(self, context):
        utilspath = os.path.realpath(__file__)[:-12]
        vtabuffer = 1000
        eyenames_l = ['eyeball_l', 'eye_l', 'eyeball_left', 'eye_left', 'left_eyeball', 'left_eye', 'l_eye'] #If your eye material is not detected, add it here
        eyenames_r = ['eyeball_r', 'eye_r', 'eyeball_r', 'eye_r', 'right_eyeball', 'right_eye', 'r_eye'] #If your eye material is not detected, add it here

        def getavgverts():
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            mesh = bpy.context.view_layer.objects.active.data
            selected_verts = []
            for vertex in mesh.vertices:
                if vertex.select == True:
                    selected_verts.append(vertex)
            vertsx = []
            vertsy = []
            vertsz = []
            for vertex in selected_verts:
                vertsx.append(vertex.co[0])
                vertsy.append(vertex.co[1])
                vertsz.append(vertex.co[2])

            vertsavgx = (sum(vertsx) / len(vertsx))
            vertsavgy = (sum(vertsy) / len(vertsy))
            vertsavgz = (sum(vertsz) / len(vertsz))
            vertsavg = (vertsavgx, vertsavgy, vertsavgz)

            return mathutils.Vector(vertsavg)

        def deselectall():
            bpy.ops.object.select_all(action='DESELECT')

        def removecollections():
            for obj in bpy.context.scene.objects:
                for collection in obj.users_collection:
                    collection.objects.unlink(obj)
                bpy.context.scene.collection.objects.link(obj)
            for collection in bpy.data.collections:
                bpy.data.collections.remove(collection)

        def clearscene():
            for object in bpy.context.view_layer.objects:
                object.hide_set(False)
                
            for obj in bpy.context.scene.objects:
                obj.select = True
                bpy.ops.object.delete()
            
            for block in bpy.data.meshes:
                bpy.data.meshes.remove(block)

            for block in bpy.data.materials:
                bpy.data.materials.remove(block)

            for block in bpy.data.textures:
                bpy.data.textures.remove(block)

            for block in bpy.data.images:
                bpy.data.images.remove(block)
                    
            for block in bpy.data.curves:
                bpy.data.curves.remove(block)
                    
            for block in bpy.data.actions:
                bpy.data.actions.remove(block)
                
            for block in bpy.data.armatures:
                bpy.data.armatures.remove(block)
                
            removecollections()
        def postimportcleanup():
            removecollections()
            deselectall()

            overrideupaxis = False
            with open(bpy.context.scene.toolscene.qcpath) as myfile:
                head = [next(myfile) for x in range(25)]
                for line in head:
                    if line.find('$upaxis Y') == -1:
                        overrideupaxis = True
                    else:
                        overrideupaxis = False
                        break
            try:
                bpy.data.objects['VTA vertices'].select_set(True)
            except:
                pass
            bpy.ops.object.delete()
            
            for obj in bpy.data.objects:
                if obj.type == 'ARMATURE':
                    if obj.name != 'EYEARMATURE.DELETEME':
                        if obj.name != 'smd_bone_vis':
                            armature = obj
            
            if overrideupaxis == True:
                armature.rotation_euler = (armature.rotation_euler[0] + radians(90), armature.rotation_euler[1], armature.rotation_euler[2])
                    
            armature.select_set(True)
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            for pose_bone in armature.pose.bones:
                pose_bone.location[0] = 0
                pose_bone.location[1] = 0
                pose_bone.location[2] = 0
                pose_bone.rotation_euler[0] = 0
                pose_bone.rotation_euler[1] = 0
                pose_bone.rotation_euler[2] = 0
                bpy.ops.object.mode_set(mode='OBJECT')
            armature.hide_set(True)
            
            scenehasshapekeys = False
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    if obj.data.shape_keys:
                        obj.select_set(True)
                        bpy.context.view_layer.objects.active = obj
                        scenehasshapekeys = True
            return scenehasshapekeys
            
        def bbox(ob):
            return (mathutils.Vector(b) for b in ob.bound_box)

        def bbox_center(ob):
            return sum(bbox(ob), mathutils.Vector()) / 8

        def bbox_axes(ob):
            bb = list(bbox(ob))
            return tuple(bb[i] - bb[0] for i in (4, 3, 1))

        def createvertexgroup(groupname):
            try: 
                splitgroup = obj.vertex_groups[groupname]
            except:
                splitgroup = obj.vertex_groups.new(name = groupname)
                
        def selecthalf():
            obj.show_only_shape_key = False
            
            bpy.ops.object.mode_set(mode='EDIT')
            o = bbox_center(bpy.context.edit_object)
            x, y, z = bbox_axes(bpy.context.edit_object) 
            data = bpy.context.edit_object.data
            bm = bmesh.from_edit_mesh(data)
            
            #Select half
            for v in bm.verts:
                v.select = False
                v.select = mathutils.geometry.distance_point_to_plane(v.co, o, x) <= 0
            bmesh.update_edit_mesh(data)
            
            createvertexgroup('RightSide')
            bpy.ops.object.vertex_group_assign()
            
            #Invert selection
            for v in bm.verts:
                v.select = not v.select
            bmesh.update_edit_mesh(data)
            
            createvertexgroup('LeftSide')
            bpy.ops.object.vertex_group_assign()
            
            for v in bm.verts:
                v.select = False
            bmesh.update_edit_mesh(data)
            
        def cursortoselected():
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 'region': region}
                            bpy.ops.view3d.snap_cursor_to_selected(override)

        #Import smd
        scene = context.scene
        clearscene()
        bpy.ops.import_scene.smd(filepath=bpy.context.scene.toolscene.qcpath, upAxis='Y')
        scenehasshapekeys = postimportcleanup()

        #Cleanup shape keys
        meshes = []
        for obj in bpy.context.scene.objects:
            if (obj.type == "MESH"):
                meshes.append(obj)
        
        
        #Setup export settings
        properties = bpy.context.scene.vs
        properties.dmx_encoding = '9'
        properties.dmx_format = '22'
        properties.export_format = 'DMX'
        properties.export_path = bpy.context.scene.toolscene.exportpath
        properties.forward_parity = '-Y'

        obj = bpy.context.object
        if scenehasshapekeys == True:
            selecthalf()
            bpy.ops.object.mode_set(mode='OBJECT')

            #Find vertex group names
            vtapath = bpy.context.scene.toolscene.qcpath[:-3] + '_01.vta'
            vtalines = []
            with open(vtapath) as myfile:
                head = [next(myfile) for x in range(vtabuffer)]
                for line in head:
                    if line.find('+') !=-1:
                        BlenderName = line.split('#')[1].strip()[:63]
                        LName = line.split('#')[1].strip().split('+')[0]
                        RName = line.split('#')[1].strip().split('+')[1]
                        vtalines.append((BlenderName, LName, RName))

            for line in vtalines:
                keyl = obj.data.shape_keys.key_blocks[line[0]]
                keyl.name = (line[1])
                keyl.value = 1
                keyr = obj.shape_key_add(from_mix=True,name=line[2])
                keyr.vertex_group = 'RightSide'
                keyl.vertex_group = 'LeftSide'
                keyl.value = 0
                keyr.value = 0
                
            for obj in meshes:
                obj.select_set(True)
                try:
                    for key in obj.data.shape_keys.key_blocks:
                        key.name = key.name.replace('_', '-') #Underscores cause errors
                except:
                    print('Mesh has no shape keys.')

        for obj in meshes:
            obj.select_set(True)
        for obj in meshes:
            bpy.context.view_layer.objects.active = obj
            break
        
        #raise ValueError
        ob = bpy.context.view_layer.objects.active
        for obj in bpy.data.objects:
            if obj != ob:
                obj.select_set(False)
        obj = ob
                
        if bpy.context.scene.toolscene.subdivide == True:
            bpy.context.scene.toolscene.untriangulate = True

        if bpy.context.scene.toolscene.untriangulate == True:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.tris_convert_to_quads(face_threshold=1.57, shape_threshold=1.57, uvs=True, sharp=True, materials=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
                
        if bpy.context.scene.toolscene.subdivide == True:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.edges_select_sharp(sharpness=radians(bpy.context.scene.toolscene.subdivision_sharpness))
            
            bm = bmesh.from_edit_mesh(obj.data)
            cl = bm.edges.layers.crease.verify()
            
            for edge in bm.edges:
                if edge.select == True:
                    edge[cl] = 1.0
                    
            bmesh.update_edit_mesh(obj.data, False, False)
            bpy.ops.object.mode_set(mode='OBJECT')
            subsurf = bpy.ops.object.modifier_add(type='SUBSURF')
            obj.modifiers["Subdivision"].levels = 1
            obj.modifiers["Subdivision"].render_levels = 1
            
        if bpy.context.scene.toolscene.clearnormals == True:
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            obj.data.use_auto_smooth = False

        if bpy.context.scene.toolscene.replaceeyes == True:
            ob = bpy.context.view_layer.objects.active
            for obj in bpy.data.objects:
                if obj != ob:
                    obj.select_set(False)
            obj = ob
            
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')

            uselefteye = False
            userighteye = False
            for material in obj.data.materials:
                for name in eyenames_l:
                    if material.name == name:
                        eyematerial_l = material.name
                        uselefteye = True
                for name in eyenames_r:
                    if material.name == name:
                        eyematerial_r = material.name
                        userighteye = True

            if userighteye == True or uselefteye == True:
                #Get material indices
                index = -1
                for slot in obj.material_slots:
                    index += 1
                    if uselefteye == True:
                        for name in eyenames_l:
                            if slot.name == name:
                                eyematerial_l = (name, index)
                    if userighteye == True:
                        for name in eyenames_r:
                            if slot.name == name:
                                eyematerial_r = (name, index)

                if userighteye == True:
                    #Select material, move cursor and delete
                    obj.active_material_index = eyematerial_r[1]
                    bpy.ops.object.material_slot_select()
                    reyelocation = getavgverts()
                    bpy.ops.mesh.delete(type='FACE')
                    bpy.ops.mesh.select_all(action='DESELECT')

                if uselefteye == True:
                    #Select material, move cursor and delete
                    obj.active_material_index = eyematerial_l[1]
                    bpy.ops.object.material_slot_select()
                    leyelocation = getavgverts()
                    bpy.ops.mesh.delete(type='FACE')
                    bpy.ops.mesh.select_all(action='DESELECT')
                
                filepath = utilspath+'\\eyeball.fbx'
                bpy.ops.import_scene.fbx(filepath=filepath)

                for obj2 in bpy.data.objects:
                    if obj2.type == 'ARMATURE':
                        if obj2.name != 'EYEARMATURE.DELETEME':
                            if obj2.name != 'smd_bone_vis':
                                armature = obj2
                
                if userighteye == True:
                    reyeoffset = (bpy.context.scene.toolscene.eyeoffsetx, bpy.context.scene.toolscene.eyeoffsety, bpy.context.scene.toolscene.eyeoffsetz)
                    eyeball_r = bpy.data.objects['eyeball_r']
                    #eyeball_r.location = reyelocation - mathutils.Vector((-0.14498, -0.4008, -0.0199))
                    eyeball_r.location = reyelocation + mathutils.Vector(reyeoffset)


                if uselefteye == True:
                    leyeoffset = (bpy.context.scene.toolscene.eyeoffsetx * -1, bpy.context.scene.toolscene.eyeoffsety, bpy.context.scene.toolscene.eyeoffsetz)
                    eyeball_l = bpy.data.objects['eyeball_l']
                    #eyeball_l.location = leyelocation - mathutils.Vector((0.14498, -0.4008, -0.0199))
                    eyeball_l.location = leyelocation + mathutils.Vector(leyeoffset)
                
                if userighteye == True:
                    eyeball_r.parent = armature
                    eyeball_r.select_set(True)
                if uselefteye == True:
                    eyeball_l.parent = armature
                    eyeball_l.select_set(True)
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

                if userighteye == False:
                    objs = bpy.data.objects
                    objs.remove(objs["eyeball_r"], do_unlink=True)

                if uselefteye == False:
                    objs = bpy.data.objects
                    objs.remove(objs["eyeball_l"], do_unlink=True)

                bpy.ops.object.join()
                
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for region in area.regions:
                            if region.type == 'WINDOW':
                                override = {'area': area, 'region': region}
                                bpy.ops.view3d.snap_cursor_to_center(override)

                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects['EYEARMATURE.DELETEME'].select_set(True)
                bpy.ops.object.delete() 

        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}

class HWM_OT_GETHELP(bpy.types.Operator):
    bl_label = 'Download'
    bl_description = 'Download link for Rectus\'s Blender Source Tools fork'
    bl_idname = 'hwm.help_operator'

    def execute(self, context):
        bpy.context.scene.cursor.location = (0, 0, 0)
        bpy.ops.wm.url_open(url="https://github.com/Rectus/BlenderSourceTools/archive/master.zip")

        return{'FINISHED'}

classes = (HWMHelpPanel, HWMToolsPanel, HWMToolsPanelB, HWM_OT_IMPORTQC, HWM_OT_GETHELP, HWM_OT_TEST, Settings)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.toolscene = bpy.props.PointerProperty(type=Settings)

def unregister():
    del bpy.types.Scene.toolscene
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()