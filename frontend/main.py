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

NETWORK_UPLOAD_PLACEHOLDER = 'www.url_to_file.de (Allowed types: .zip, .txt)'
LOCAL_UPLOAD_PLACEHOLDER = 'Allowed types: .zip, .txt'

w_upload_local_nf = None  # type: fileupload.FileUploadWidget
w_upload_local_af = None  # type: fileupload.FileUploadWidget
w_upload_network_nf = None  # type: widgets.Button
w_upload_network_af = None  # type: widgets.Button

w_file_graph_data = None  # type: widgets.Text
w_file_metadata = None  # type: widgets.Text

w_out_graph_data = None  # type: widgets.Output
w_out_metadata = None  # type: widgets.Output

w_metadata_settings_left = None  # type: widgets.VBox

box_layout_ = None  # type: widgets.Layout

metadata_table = None  # type: vtna.data_import.MetadataTable
edge_list = None  # type: typ.List[vtna.data_import.TemporalEdge]


def on_toogle_upload_type(change):
    global w_upload_local_nf
    global w_upload_local_af
    global w_upload_network_nf
    global w_upload_network_af
    global w_file_graph_data
    global w_file_metadata

    if change['new'] == 'Network':
        w_upload_local_nf.layout.display = 'none'
        w_upload_local_af.layout.display = 'none'

        w_upload_network_nf.layout.display = 'inline'
        w_upload_network_af.layout.display = 'inline'

        w_file_metadata.disabled = False
        w_file_metadata.placeholder = NETWORK_UPLOAD_PLACEHOLDER
        w_file_graph_data.disabled = False
        w_file_graph_data.placeholder = NETWORK_UPLOAD_PLACEHOLDER
    else:
        w_upload_local_nf.layout.display = 'inline'
        w_upload_local_af.layout.display = 'inline'

        w_upload_network_nf.layout.display = 'none'
        w_upload_network_af.layout.display = 'none'

        w_file_metadata.disabled = True
        w_file_metadata.placeholder = LOCAL_UPLOAD_PLACEHOLDER
        w_file_graph_data.disabled = True
        w_file_graph_data.placeholder = LOCAL_UPLOAD_PLACEHOLDER


def print_edge_stats(filename, edges):
    print('Preview {} :'.format(filename))
    print('Total Edges:', len(edges))
    print('Update Delta:', vtna.data_import.infer_update_delta(edges))
    print('Time Interval:', vtna.data_import.get_time_interval_of_edges(edges))


def print_metadata_stats(metadata):
    pass


# why the underscore?
# Upload of temporal graph data via local upload
def handle_local_upload_graph_data(change):
    global edge_list
    global w_out_graph_data

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
