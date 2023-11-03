import os
import sys
import json
import io
from compas.data import Data,json_loads,json_dumps, json_dump
from compas.datastructures import Assembly, Mesh
from compas.geometry import Transformation, Point, Vector, Frame
from compas_xr.storage.storage_interface import StorageInterface
import clr
import threading

from System.IO import File, FileStream, FileMode, MemoryStream, Stream
from System.Text import Encoding
from System.Threading import (
    ManualResetEventSlim,
    CancellationTokenSource,
    CancellationToken)

try:
    # from urllib.request import urlopen
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

lib_dir = os.path.join(os.path.dirname(__file__), "dependencies")
print (lib_dir)
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

clr.AddReference("Firebase.Auth.dll")
clr.AddReference("Firebase.dll")
clr.AddReference("Firebase.Storage.dll")
print("Are u really working?")

from Firebase.Auth import FirebaseAuthConfig
# from Firebase.Auth import FirebaseConfig
from Firebase.Auth import FirebaseAuthClient
from Firebase.Auth.Providers import FirebaseAuthProvider
from Firebase.Storage import FirebaseStorage
from Firebase.Storage import FirebaseStorageTask

# # Get the current file path
# CURRENT_FILE_PATH = os.path.abspath(__file__)
# # print (CURRENT_FILE_PATH)

# # Define the number of levels to navigate up
# LEVELS_TO_GO_UP = 2

# #Construct File path to the correct location
# PARENT_FOLDER = os.path.abspath(os.path.join(CURRENT_FILE_PATH, "../" * LEVELS_TO_GO_UP))

# # Enter another folder
# TARGET_FOLDER = os.path.join(PARENT_FOLDER, "data")
# DEFAULT_CONFIG_PATH = os.path.join(TARGET_FOLDER, "firebase_config.json")

"""
TODO: add proper exceptions. This is a function by function review.
TODO: add proper comments.
TODO: Review Function todo's
"""

class Storage(StorageInterface):
    
    _shared_storage = None

    def __init__(self, config_path = None):
        
        self.config_path = config_path #or DEFAULT_CONFIG_PATH
        self.storage = self._ensure_storage()

    def _ensure_storage(self):
        # Initialize Firebase connection and storage only once
        if not Storage._shared_storage:
            path = self.config_path
            print ("This is your path" + path)

            # Load the Firebase configuration file from the JSON file if the file exists
            if os.path.exists(path):
                with open(path) as config_file:
                    config = json.load(config_file)

                #TODO: Authorization for storage security (Works for now for us because our Storage is public)

                #Initialize Storage from storage bucket
                storage_client = FirebaseStorage(config["storageBucket"])
                print (storage_client)
                Storage._shared_storage = storage_client

        # Still no storage? Fail, we can't do anything
        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

        return Storage._shared_storage
    
    #Internal Class Functions
    def _start_async_call(self, fn, timeout=10):
        result = {}
        result["event"] = threading.Event()
        
        async_thread = threading.Thread(target=fn, args=(result, ))
        async_thread.start()
        async_thread.join(timeout=timeout)

        return result["data"]
    
    def _get_file_from_remote(self, url):
        
        """
        This function is used to get the information form the source url and returns a string
        """

        try:
            get = urlopen(url).read()

        except:
            raise Exception("unable to get file from url {}".format(url))
        
        return get
    
    #Upload Functions
    def upload_file(self, path_on_cloud, path_local): #DONE
        
        self._ensure_storage()
        
        # Shared storage instance with a specification of file name.
        storage_refrence = Storage._shared_storage.Child(path_on_cloud)

        if os.path.exists(path_local):

            with FileStream(path_local, FileMode.Open) as file_stream:

                def _begin_upload(result):

                    uploadtask = storage_refrence.PutAsync(file_stream)
                    task_upload = uploadtask.GetAwaiter()
                    task_upload.OnCompleted(lambda: result["event"].set())

                    result["event"].wait()
                    result["data"] = True
                
                upload = self._start_async_call(_begin_upload)
            
        else:
            raise Exception("path does not exist {}".format(path_local))

    #TODO: NEEDS TO BE MOVED
    def upload_assembly(self, path_on_cloud, assembly):
        
        self._ensure_storage()
        
        # Shared storage instance with a specification of file name.
        storage_refrence = Storage._shared_storage.Child(path_on_cloud)
            
        data = json_dumps(assembly, pretty=True)

        byte_data = Encoding.UTF8.GetBytes(data)
        stream = MemoryStream(byte_data)

        def _begin_upload(result):

            uploadtask = storage_refrence.PutAsync(stream)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())

            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
 
    def upload_data(self, path_on_cloud, data):
        
        self._ensure_storage()
        
        # Shared storage instance with a specification of file name.
        storage_refrence = Storage._shared_storage.Child(path_on_cloud)
        
        #Serialize data
        serialized_data = json_dumps(data)

        byte_data = Encoding.UTF8.GetBytes(serialized_data)
        stream = MemoryStream(byte_data)

        def _begin_upload(result):

            uploadtask = storage_refrence.PutAsync(stream)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())

            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print ("data uploaded")

    #Download Functions
    def download_file(self, path_on_cloud, path_local):
        
        self._ensure_storage()
        
        storage_refrence = Storage._shared_storage.Child(path_on_cloud)

        def _begin_download(result):
            downloadurl_task = storage_refrence.GetDownloadUrlAsync()
            task_download = downloadurl_task.GetAwaiter()
            task_download.OnCompleted(lambda: result["event"].set())

            result["event"].wait()
            result["data"] = downloadurl_task.Result
        
        url = self._start_async_call(_begin_download)
        
        data = self._get_file_from_remote(url)

        if os.path.exists(path_local):
            #TODO: Pretty is not working and I do not know why.
            json_dump(data, path_local, pretty= True)
        
        else:
            raise Exception("path does not exist {}".format(path_local))

    #TODO: NEEDS TO BE MOVED
    def download_assembly(self, path_on_cloud):
        
        self._ensure_storage()
        
        # Shared storage instance with a specificatoin of file name.
        storage_refrence = Storage._shared_storage.Child(path_on_cloud)
        print (storage_refrence)

        def _begin_download(result):
            downloadurl_task = storage_refrence.GetDownloadUrlAsync()
            task_download = downloadurl_task.GetAwaiter()
            task_download.OnCompleted(lambda: result["event"].set())

            result["event"].wait()
            result["data"] = downloadurl_task.Result
        
        url = self._start_async_call(_begin_download)

        data = self._get_file_from_remote(url)

        desearialized_data = json_loads(data)

        return desearialized_data

    def download_data(self, path_on_cloud):
        
        self._ensure_storage()
        
        # Shared storage instance with a specificatoin of file name.
        storage_refrence = Storage._shared_storage.Child(path_on_cloud)
        print (storage_refrence)

        def _begin_download(result):
            downloadurl_task = storage_refrence.GetDownloadUrlAsync()
            task_download = downloadurl_task.GetAwaiter()
            task_download.OnCompleted(lambda: result["event"].set())

            result["event"].wait()
            result["data"] = downloadurl_task.Result
        
        url = self._start_async_call(_begin_download)
        
        data = self._get_file_from_remote(url)

        # data_serialized = json_dumps(json_data)
        desearialized_data = json_loads(data)
        print (type(desearialized_data))

        return desearialized_data

    #Manage Objects - .obj export and upload
    #TODO: NEEDS TO BE MOVED
    def export_timberassembly_objs(self, assembly, folder_path, new_folder_name):
        
        assembly_graph = assembly.graph.data
        nodes = assembly_graph["node"]
        assembly_beam_keys = assembly.beam_keys
        origin_frame = Frame(Point(0,0,0), Vector.Xaxis(), Vector.Yaxis())

        #Construct file path with the new folder name
        target_folder_path = os.path.join(folder_path, new_folder_name)
        
        #Make a folder with the folder name if it does not exist
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)
        
        #Iterate through assembly beams and perform transformation and export
        for key in assembly_beam_keys:
            beam = nodes[str(key)]["part"]
            frame = beam.frame
            
            #Extract compas box from beam
            beam_box = beam.shape
            
            #Create Transformation from beam frame to world_xy frame and maybe a copy?
            transformation = Transformation.from_frame_to_frame(frame, origin_frame)
            
            #Transform box from frame to world xy
            box_transformed = beam_box.transformed(transformation)
            
            #Get all information from the box and convert to mesh
            box_vertices = box_transformed.vertices
            box_faces = box_transformed.faces
            box_mesh = Mesh.from_vertices_and_faces(box_vertices, box_faces)
            
            # Mesh to obj with file name being KEY and folder being the newly created folder
            if os.path.exists(target_folder_path):
                file_name = str(key)+".obj"
                obj_file_path = os.path.join(target_folder_path, file_name)
                box_mesh.to_obj(obj_file_path)
            
            else:
                raise Exception("File path does not exist {}".format(target_folder_path))
    
    def upload_obj(self, path_on_cloud, cloud_folder, path_local):
        
        self._ensure_storage()
        
        storage_refrence = Storage._shared_storage.Child("obj_storage").Child(cloud_folder).Child(path_on_cloud)

        if os.path.exists(path_local):
            
            data = File.ReadAllBytes(path_local)
            stream = MemoryStream(data)
            print (path_local)

            def _begin_upload(result):

                uploadtask = storage_refrence.PutAsync(stream)
                task_upload = uploadtask.GetAwaiter()
                task_upload.OnCompleted(lambda: result["event"].set())

                result["event"].wait()
                result["data"] = True
            
            upload = self._start_async_call(_begin_upload)
        
        else:
            raise Exception("path does not exist {}".format(path_local))

    def upload_objs(self, folder_local, cloud_folder_name):
        
        
        self._ensure_storage()
    
        # TODO: Shared storage instance with a specification of file name. Does not work with the reference below, only works if I construct the reference every time.
        """
        Folder reference:
        storagefolder_refrence = Storage._shared_storage.Child("obj_storage").Child(cloud_folder_name)

        File reference below later in code loop:
        storage_reference = storagefolder_reference.Child(name)

        """
                    
        if os.path.exists(folder_local) and os.path.isdir(folder_local):
            
            file_info = []

            for f in os.listdir(folder_local):
                file_path = os.path.join(folder_local, f)
                if os.path.isfile(file_path):
                    file_info.append((file_path, f))

            for path, name in file_info:

                if os.path.exists(path):
                    #TODO: Question
                    """
                    Also works with the function call below, but not sure if this is the best idea
                    # self.upload_obj(name, cloud_folder_name, path)
                    """
                    data = File.ReadAllBytes(path)
                    stream = MemoryStream(data)

                    def _begin_upload(result):
                        storage_refrence = Storage._shared_storage.Child("obj_storage").Child(cloud_folder_name).Child(name)
                        uploadtask = storage_refrence.PutAsync(stream)
                        task_upload = uploadtask.GetAwaiter()
                        task_upload.OnCompleted(lambda: result["event"].set())

                        result["event"].wait()
                        result["data"] = True

                    upload = self._start_async_call(_begin_upload)
                
                else:
                    raise Exception("path does not exist {}".format(path))


        else:
            raise Exception("path does not exist {}".format(folder_local))
