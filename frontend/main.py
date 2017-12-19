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


NETWORK_UPLOAD_PLACEHOLDER = 'Enter URL -> Click Upload'
LOCAL_UPLOAD_PLACEHOLDER = 'Click on Upload -> Select file'


class UIDataUploadManager(object):
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
                self.__graph_data_text.placeholder = NETWORK_UPLOAD_PLACEHOLDER
                self.__metadata_data_text.disabled = False
                self.__metadata_data_text.placeholder = NETWORK_UPLOAD_PLACEHOLDER
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
                self.__graph_data_text.placeholder = LOCAL_UPLOAD_PLACEHOLDER
                self.__metadata_data_text.disabled = True
                self.__metadata_data_text.placeholder = LOCAL_UPLOAD_PLACEHOLDER
        return on_toogle_upload_type

    def handle_local_upload_graph_data(change):
        # What does the w stand for?
        w = change['owner']
        try:
            with open(w.filename, 'wb') as f:
                f.write(w.data)
                w_file_graph_data.value = 'Uploaded `{}` ({:.2f} kB)'.format(w.filename, len(w.data) / 2 ** 10)

            edge_list = vtna.data_import.read_edge_table(w.filename)

            with w_out_graph_data:
                ipydisplay.clear_output()
                print_edge_stats(w.filename, edge_list)
        # TODO: Exception catching is not exhaustive yet
        except FileNotFoundError:
            w_file_graph_data.value = f'File {w.filename} does not exist'
            with w_out_graph_data:
                ipydisplay.clear_output()
                print(f'\x1b[31m{w_file_graph_data.value}\x1b[0m')
        except ValueError:
            w_file_graph_data.value = f'Columns 1-3 in {w.filename} cannot be parsed to integers'
            with w_out_graph_data:
                ipydisplay.clear_output()
                print(f'\x1b[31m{w_file_graph_data.value}\x1b[0m')


w_metadata_settings_left = None  # type: widgets.VBox

box_layout_ = None  # type: widgets.Layout


def print_edge_stats(filename, edges):
    print('Preview {} :'.format(filename))
    print('Total Edges:', len(edges))
    print('Update Delta:', vtna.data_import.infer_update_delta(edges))
    print('Time Interval:', vtna.data_import.get_time_interval_of_edges(edges))


def print_metadata_stats(metadata):
    pass


# why the underscore?
# Upload of temporal graph data via local upload



# Upload of temporal graph data via network
def handle_network_upload_graph_data(change):
    global edge_list
    global w_out_graph_data
    global w_file_graph_data
    try:
        url = w_file_graph_data.value
        edge_list = vtna.data_import.read_edge_table(url)
        with w_out_graph_data:
            ipydisplay.clear_output()
            print_edge_stats(url, edge_list)
    # TODO: Exception catching is not exhaustive yet
    except urllib.error.HTTPError:
        w_file_graph_data.value = f'Could not access URL {url}'
        with w_out_graph_data:
            ipydisplay.clear_output()
            print(f'\x1b[31m{w_file_graph_data.value}\x1b[0m')
    except ValueError:
        w_file_graph_data.value = f'Columns 1-3 in {url} cannot be parsed to integers'
        with w_out_graph_data:
            ipydisplay.clear_output()
            print(f'\x1b[31m{w_file_graph_data.value}\x1b[0m')


# Upload of metadata via local upload
def handle_local_upload_metadata(change):
    global metadata_table
    global w_file_metadata
    global w_out_metadata
    try:
        w = change['owner']
        with open(w.filename, 'wb') as f:
            f.write(w.data)
            w_file_metadata.value = 'Uploaded `{}` ({:.2f} kB)'.format(w.filename, len(w.data) / 2 ** 10)
        # Load metadata
        metadata_table = vtna.data_import.MetadataTable(w.filename)
        with w_out_metadata:
            ipydisplay.clear_output()
            print_metadata_stats(metadata_table)
        # Load new UI for configuring metadata
        open_column_config(metadata_table)
    # TODO: Exception catching is not exhaustive yet
    except FileNotFoundError:
        w_file_metadata.value = f'File {w.filename} does not exist'
        with w_out_metadata:
            ipydisplay.clear_output()
            print(f'\x1b[31m{w_file_graph_data.value}\x1b[0m')
    except ValueError:
        w_file_metadata.value = f'Column 1 in {w.filename} cannot be parsed to integer'
        with w_out_metadata:
            ipydisplay.clear_output()
            print(f'\x1b[31m{w_file_graph_data.value}\x1b[0m')


# Upload of metadata via network
def handle_network_upload_metadata(change):
    global metadata_table
    global w_file_metadata
    global w_out_metadata
    try:
        url = w_file_metadata.value
        metadata_table = vtna.data_import.MetadataTable(url)
        with w_out_metadata:
            ipydisplay.clear_output()
            print_metadata_stats(metadata_table)
        open_column_config(metadata_table)
    # TODO: Exception catching is not exhaustive yet
    except urllib.error.HTTPError:
        w_file_metadata.value = f'Could not access URL {url}'
        with w_out_metadata:
            ipydisplay.clear_output()
            print(f'\x1b[31m{w_file_graph_data.value}\x1b[0m')
    except ValueError:
        w_file_metadata.value = f'Column 1 in {url} cannot be parsed to integer'
        with w_out_metadata:
            ipydisplay.clear_output()
            print(f'\x1b[31m{w_file_graph_data.value}\x1b[0m')


def open_column_config(metadata: vtna.data_import.MetadataTable):
    """
    Shows menu to configure metadata.
    Currently only supports setting of names.
    Changes are made to Text widgets in w_attribute_settings.children
    """
    # Load some default settings
    w_metadata_settings_left.children = []

    for idx, name in enumerate(metadata.get_attribute_names()):
        w_col_name = widgets.Text(
            value='{}'.format(name),
            placeholder='Name',
            description=f'Column {idx}:',
            disabled=False
        )
        w_metadata_settings_left.children.append(widgets.VBox([w_col_name], layout=box_layout_))
