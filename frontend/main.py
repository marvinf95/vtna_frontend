import typing as typ
import urllib
import urllib.error

import fileupload
import IPython.display as ipydisplay
from ipywidgets import widgets

import vtna.data_import
import vtna.graph
import vtna.layout
import vtna.utility


class UIDataUploadManager(object):
    NETWORK_UPLOAD_PLACEHOLDER = 'Enter URL -> Click Upload'  # type: str
    LOCAL_UPLOAD_PLACEHOLDER = 'Click on Upload -> Select file'  # type: str

    def __init__(self,
                 # Graph upload widgets
                 local_graph_file_upload: fileupload.FileUploadWidget,
                 network_graph_upload_button: widgets.Button,
                 graph_data_text: widgets.Text,
                 graph_data_output: widgets.Output,
                 # Metadata upload widgets
                 local_metadata_file_upload: fileupload.FileUploadWidget,
                 network_metadata_upload_button: widgets.Button,
                 metadata_text: widgets.Text,
                 metadata_output: widgets.Output
                 ):
        self.__local_graph_file_upload = local_graph_file_upload
        self.__network_graph_upload_button = network_graph_upload_button
        self.__graph_data_text = graph_data_text
        self.__graph_data_output = graph_data_output

        self.__local_metadata_file_upload = local_metadata_file_upload
        self.__network_metadata_upload_button = network_metadata_upload_button
        self.__metadata_data_text = metadata_text
        self.__metadata_data_output = metadata_output

        self.__edge_list = None
        self.__metadata = None

    def get_edge_list(self) -> typ.List[vtna.data_import.TemporalEdge]:
        return self.__edge_list

    def get_metadata(self) -> vtna.data_import.MetadataTable:
        return self.__metadata

    def build_on_toggle_upload_type(self) -> typ.Callable:
        # TODO: What is the type of change? Dictionary?
        def on_toogle_upload_type(change):
            # Switch to network upload option
            if change['new'] == 'Network':
                # Hide local upload widgets
                self.__local_graph_file_upload.layout.display = 'none'
                self.__local_metadata_file_upload.layout.display = 'none'
                # Show network upload widgets
                self.__network_graph_upload_button.layout.display = 'inline'
                self.__network_metadata_upload_button.layout.display = 'inline'
                # Enable text input for URLs
                self.__graph_data_text.disabled = False
                self.__graph_data_text.placeholder = UIDataUploadManager.NETWORK_UPLOAD_PLACEHOLDER
                self.__metadata_data_text.disabled = False
                self.__metadata_data_text.placeholder = UIDataUploadManager.NETWORK_UPLOAD_PLACEHOLDER
            # Switch to local upload option
            else:
                # Show local upload widgets
                self.__local_graph_file_upload.layout.display = 'inline'
                self.__local_metadata_file_upload.layout.display = 'inline'
                # Hide network upload widgets
                self.__network_graph_upload_button.layout.display = 'none'
                self.__network_metadata_upload_button.layout.display = 'none'
                # Disable text input for local upload
                self.__graph_data_text.disabled = True
                self.__graph_data_text.placeholder = UIDataUploadManager.LOCAL_UPLOAD_PLACEHOLDER
                self.__metadata_data_text.disabled = True
                self.__metadata_data_text.placeholder = UIDataUploadManager.LOCAL_UPLOAD_PLACEHOLDER
        return on_toogle_upload_type

    def build_handle_local_upload_graph_data(self) -> typ.Callable:
        def handle_local_upload_graph_data(change):
            # TODO: What does the w stand for?
            w = change['owner']
            try:
                # Upload and store file to notebook directory
                # TODO: put it into a tmp folder
                with open(w.filename, 'wb') as f:
                    f.write(w.data)
                    self.__graph_data_text.value = w.filename
                # Import graph as edge list via vtna
                self.__edge_list = vtna.data_import.read_edge_table(w.filename)
                # Display summary of loaded file to __graph_data_output
                self.__display_graph_upload_summary(w.filename)
            # TODO: Exception catching is not exhaustive yet
            except FileNotFoundError:
                error_msg = f'File {w.filename} does not exist'
                self.__display_graph_upload_error(error_msg)
            except ValueError:
                error_msg = f'Columns 1-3 in {w.filename} cannot be parsed to integers'
                self.__display_graph_upload_error(error_msg)
        return handle_local_upload_graph_data

    def build_handle_network_upload_graph_data(self) -> typ.Callable:
        def handle_network_upload_graph_data(change):
            try:
                url = self.__graph_data_text.value
                self.__edge_list = vtna.data_import.read_edge_table(url)
                self.__display_graph_upload_summary(url)
            # TODO: Exception catching is not exhaustive yet
            except urllib.error.HTTPError:
                error_msg = f'Could not access URL {url}'
                self.__display_graph_upload_error(error_msg)
            except ValueError:
                error_msg = f'Columns 1-3 in {url} cannot be parsed to integers'
                self.__display_graph_upload_error(error_msg)
        return handle_network_upload_graph_data

    def build_handle_local_upload_metadata(self) -> typ.Callable:
        def handle_local_upload_metadata(change):
            w = change['owner']
            try:
                with open(w.filename, 'wb') as f:
                    f.write(w.data)
                    self.__graph_data_text.value = w.filename
                # Load metadata
                metadata_table = vtna.data_import.MetadataTable(w.filename)
                self.__display_metadata_upload_summary(w.filename)
                # Display UI for configuring metadata
                open_column_config(metadata_table)
            # TODO: Exception catching is not exhaustive yet
            except FileNotFoundError:
                error_msg = f'File {w.filename} does not exist'
                self.__display_metadata_upload_error(error_msg)
            except ValueError:
                error_msg = f'Column 1 in {w.filename} cannot be parsed to integer'
                self.__display_metadata_upload_error(error_msg)
        return handle_local_upload_metadata

    def build_handle_network_upload_metadata(self) -> typ.Callable:
        def handle_network_upload_metadata(change):
            try:
                url = self.__metadata_data_text.value
                metadata_table = vtna.data_import.MetadataTable(url)
                self.__display_metadata_upload_summary(url)
                open_column_config(metadata_table)
            # TODO: Exception catching is not exhaustive yet
            except urllib.error.HTTPError:
                error_msg = f'Could not access URL {url}'
                self.__display_metadata_upload_error(error_msg)
            except ValueError:
                error_msg = f'Column 1 in {url} cannot be parsed to integer'
                self.__display_metadata_upload_error(error_msg)
        return handle_network_upload_metadata

    def __display_graph_upload_error(self, msg: str):
        self.__graph_data_text.value = msg
        with self.__graph_data_output:
            ipydisplay.clear_output()
            print(f'\x1b[31m{msg}\x1b[0m')

    def __display_graph_upload_summary(self, filename: str):
        with self.__graph_data_output:
            ipydisplay.clear_output()
            print_edge_stats(filename, self.__edge_list)

    def __display_metadata_upload_error(self, msg):
        self.__metadata_data_text.value = msg
        with self.__metadata_data_output:
            ipydisplay.clear_output()
            print(f'\x1b[31m{msg}\x1b[0m')

    def __display_metadata_upload_summary(self, filename: str):
        with self.__metadata_data_output:
            ipydisplay.clear_output()
            print_metadata_stats(filename, self.__metadata)


w_metadata_settings_left = None  # type: widgets.VBox

box_layout_ = None  # type: widgets.Layout


def print_edge_stats(filename: str, edges: typ.List[vtna.data_import.TemporalEdge]):
    print(f'Preview {filename}:')
    print('Total Edges:', len(edges))
    print('Update Delta:', vtna.data_import.infer_update_delta(edges))
    print('Time Interval:', vtna.data_import.get_time_interval_of_edges(edges))


def print_metadata_stats(filename: str, metadata: vtna.data_import.MetadataTable):
    print(f'Preview {filename}:')
    for idx, name in enumerate(metadata.get_attribute_names()):
        print(f'Column {name}:')
        for category in metadata.get_categories(name):
            print(f'- {category}')


def open_column_config(metadata: vtna.data_import.MetadataTable):
    """
    Shows menu to configure metadata.
    Currently only supports setting of names.
    Changes are made to Text widgets in w_attribute_settings.children
    """
    # Load some default settings
    w_metadata_settings_left.children = []

    for name in enumerate(metadata.get_attribute_names()):
        w_col_name = widgets.Text(
            value='{}'.format(name),
            placeholder='New Column Name',
            description=f'Column {name}:',
            disabled=False
        )
        w_metadata_settings_left.children.append(widgets.VBox([w_col_name], layout=box_layout_))
