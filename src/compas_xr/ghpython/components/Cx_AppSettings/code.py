"""
Application Settings.

COMPAS XR v0.8.0
"""

from compas_xr.project import ProjectManager
from compas_xr.ghpython.app_settings import AppSettings

from ghpythonlib.componentbase import executingcomponent as component


class ApplicationSettingsComponent(component):
    def RunScript(self, config_filepath, project_name, storage_folder, z_to_y_remap, write):
        if not (config_filepath):
            self.Message = "Missing Config"

        elif not (project_name):
            self.Message = "Missing Settings Data"

        else:
            app_settings = AppSettings(project_name, storage_folder, z_to_y_remap)
            pm = ProjectManager(config_filepath)
            self.Message = None

            if write:
                pm.application_settings_writer(app_settings.project_name, app_settings.storage_folder, app_settings.z_to_y_remap)