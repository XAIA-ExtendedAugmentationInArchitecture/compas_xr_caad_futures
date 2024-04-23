import os
import json

class RealtimeDatabaseInterface(object):
    
    def construct_reference(self, project_name):
        raise NotImplementedError("Implemented on child classes")
    
    def construct_child_refrence(self, parentname, childname):
        raise NotImplementedError("Implemented on child classes")
    
    def construct_grandchild_refrence(self, parentname, childname, grandchildname):
        raise NotImplementedError("Implemented on child classes")

    def construct_reference_from_list(self, reference_list):
        raise NotImplementedError("Implemented on child classes")

    def upload_data_to_reference(self, data, database_reference):
        raise NotImplementedError("Implemented on child classes")
    
    def get_data_from_reference(self, database_reference):
        raise NotImplementedError("Implemented on child classes")
    
    def delete_data_from_reference(self, database_reference):
        raise NotImplementedError("Implemented on child classes")
    
    def stream_data_from_reference(self, callback, database_reference):
        raise NotImplementedError("Implemented on child classes")

    def application_settings_writer(self, databaseparentname, storagefolder="None", objorientation=True):
        data = {"parentname": databaseparentname, "storagename": storagefolder, "objorientation": objorientation}
        self.upload_data(data, "ApplicationSettings")

    def upload_data(self, data, project_name):
        database_reference = self.construct_reference(project_name)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_to_project(self, data, project_name, child_name):
        database_reference = self.construct_child_refrence(project_name, child_name)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_to_deep_reference(self, data, reference_list):
        database_reference = self.construct_reference_from_list(reference_list)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_from_file(self, path_local, project_name):
        if not os.path.exists(path_local):
            raise Exception("path does not exist {}".format(path_local))
        with open(path_local) as config_file:
            data = json.load(config_file)
        database_reference = self.construct_reference(project_name)
        self.upload_data_to_reference(data, database_reference)

    def get_data(self, project_name):
        database_reference = self.construct_reference(project_name)
        return self.get_data_from_reference(database_reference)

    def get_data_from_project(self, project_name, child_name):
        database_reference = self.construct_child_refrence(project_name, child_name)
        return self.get_data_from_reference(database_reference)

    def get_data_from_deep_reference(self, reference_list):
        database_reference = self.construct_reference_from_list(reference_list)
        return self.get_data_from_reference(database_reference)
    
    def delete_data(self, project_name):
        database_reference = self.construct_reference(project_name)
        self.delete_data_from_reference(database_reference)

    def delete_data_from_project(self, project_name, child_name):
        database_reference = self.construct_child_refrence(project_name, child_name)
        self.delete_data_from_reference(database_reference)

    def delete_data_from_deep_reference(self, reference_list):
        database_reference = self.construct_reference_from_list(reference_list)
        self.delete_data_from_reference(database_reference)