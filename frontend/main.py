import typing as typ
import urllib
import urllib.error

import fileupload
import IPython.display as ipydisplay
from ipywidgets import widgets
import matplotlib.pyplot as plt
import networkx as nx

import vtna.data_import
import vtna.graph
import vtna.layout
import vtna.statistics
import vtna.utility


# Not a good solution, but "solves" the global variable problem.
class UIDataUploadManager(object):
    NETWORK_UPLOAD_PLACEHOLDER = 'Enter URL -> Click Upload'  # type: str
    LOCAL_UPLOAD_PLACEHOLDER = 'Click on Upload -> Select file'  # type: str

    def __init__(self,
                 # Run button switches to Display graph step, should be disabled by default and enabled on set
                 # granularity.
                 run_button: widgets.Button,
                 # Graph upload widgets
                 local_graph_file_upload: fileupload.FileUploadWidget,
                 network_graph_upload_button: widgets.Button,
                 graph_data_text: widgets.Text,
                 graph_data_output: widgets.Output,
                 # Metadata upload widgets
                 local_metadata_file_upload: fileupload.FileUploadWidget,
                 network_metadata_upload_button: widgets.Button,
                 metadata_text: widgets.Text,
                 metadata_output: widgets.Output,
                 # Metadata configuration widgets
                 metadata_configuration_vbox: widgets.VBox,  # Container, for configuration of each separate column
                 column_configuration_layout: widgets.Layout,  # Layout, for each separate column configuration
                 # Graph data configuration widgets
                 graph_data_configuration_vbox: widgets.VBox  # Container, for configuration of graph data
                 ):
        self.__run_button = run_button
        run_button.disabled = True

        self.__local_graph_file_upload = local_graph_file_upload
        self.__network_graph_upload_button = network_graph_upload_button
        self.__graph_data_text = graph_data_text
        self.__graph_data_output = graph_data_output

        self.__local_metadata_file_upload = local_metadata_file_upload
        self.__network_metadata_upload_button = network_metadata_upload_button
        self.__metadata_data_text = metadata_text
        self.__metadata_data_output = metadata_output

        self.__metadata_configuration_vbox = metadata_configuration_vbox
        self.__column_configuration_layout = column_configuration_layout

        self.__graph_data__configuration_vbox = graph_data_configuration_vbox

        self.__graph_data_file_name = None

        self.__edge_list = None  # type: typ.List[vtna.data_import.TemporalEdge]
        self.__metadata = None  # type: vtna.data_import.MetadataTable

        self.__granularity = None

    def get_edge_list(self) -> typ.List[vtna.data_import.TemporalEdge]:
        return self.__edge_list

    def get_metadata(self) -> vtna.data_import.MetadataTable:
        return self.__metadata

    def get_granularity(self) -> int:
        return self.__granularity

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
                # Save file name of graph data
                self.__graph_data_file_name = w.filename
                # Import graph as edge list via vtna
                self.__edge_list = vtna.data_import.read_edge_table(w.filename)
                # Display summary of loaded file to __graph_data_output
                self.__display_graph_upload_summary()
                # Display UI for graph config
                self.__open_graph_config()
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
                # Save file name of graph data
                self.__graph_data_file_name = url
                self.__edge_list = vtna.data_import.read_edge_table(url)
                self.__display_graph_upload_summary()
                # Display UI for graph config
                self.__open_graph_config()
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
                    self.__metadata_data_text.value = w.filename
                # Load metadata
                self.__metadata = vtna.data_import.MetadataTable(w.filename)
                self.__display_metadata_upload_summary()
                # Display UI for configuring metadata
                self.__open_column_config()
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
                self.__metadata = vtna.data_import.MetadataTable(url)
                self.__display_metadata_upload_summary()
                self.__open_column_config()
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

    def __display_graph_upload_summary(self, prepend_msgs: typ.List[str]=None):
        with self.__graph_data_output:
            ipydisplay.clear_output()
            if prepend_msgs is not None:
                for msg in prepend_msgs:
                    print(msg)
            print_edge_stats(self.__edge_list)
            # Collect/Generate data for edge histogram plot
            update_delta = vtna.data_import.infer_update_delta(self.__edge_list)
            earliest, _ = vtna.data_import.get_time_interval_of_edges(self.__edge_list)
            if self.__granularity is None:
                granularity = update_delta * 100
                title = f'No granularity set. Displayed with granularity: {granularity}'
            else:
                granularity = self.__granularity
                title = f'Granularity: {granularity}'
            histogram = vtna.statistics.histogram_edges(self.__edge_list, granularity)
            x = list(range(len(histogram)))
            # Plot edge histogram
            plt.figure()
            _ = plt.bar(list(range(len(histogram))), histogram)
            plt.title(title)
            plt.ylabel('#edges')
            plt.xticks(x, [''] * len(x))
            plt.show()

    def __display_metadata_upload_error(self, msg):
        self.__metadata_data_text.value = msg
        with self.__metadata_data_output:
            ipydisplay.clear_output()
            print(f'\x1b[31m{msg}\x1b[0m')

    def __display_metadata_upload_summary(self, prepend_msgs: typ.List[str]=None):
        with self.__metadata_data_output:
            ipydisplay.clear_output()
            if prepend_msgs is not None:
                for msg in prepend_msgs:
                    print(msg)
            table = ipydisplay.HTML(create_html_metadata_summary(self.__metadata))
            ipydisplay.display_html(table)  # A tuple is expected as input, but then it won't work for some reason...

    def __open_column_config(self):
        """
        Shows menu to configure metadata.
        Currently only supports setting of names.
        Changes are made to Text widgets in w_attribute_settings.children
        """
        # Load some default settings
        self.__metadata_configuration_vbox.children = []
        current_names = sorted(self.__metadata.get_attribute_names())
        column_text_fields = list()  # type: typ.List[widgets.Text]

        for name in current_names:
            w_col_name = widgets.Text(
                value='{}'.format(name),
                placeholder='New Column Name',
                description=f'Column {name}:',
                disabled=False
            )
            column_text_fields.append(w_col_name)
            self.__metadata_configuration_vbox.children += \
                (widgets.VBox([w_col_name], layout=self.__column_configuration_layout),)

        rename_button = widgets.Button(
            description='Rename',
            disabled=False,
            button_style='primary',
            tooltip='Rename columns',
        )
        self.__metadata_configuration_vbox.children += (rename_button,)

        def apply_rename(_):
            to_rename = dict()
            for i in range(len(current_names)):
                if current_names[i] != column_text_fields[i].value:
                    to_rename[current_names[i]] = column_text_fields[i].value
            msgs = list()
            try:
                self.__metadata.rename_attributes(to_rename)
                for i, new_name in enumerate(map(lambda f: f.value, column_text_fields)):
                    current_names[i] = new_name
            except vtna.data_import.DuplicateTargetNamesError as e:
                msgs.append(f'\x1b[31mRenaming failed: {", ".join(e.illegal_names)} are duplicates\x1b[0m')
            except vtna.data_import.RenamingTargetExistsError as e:
                msgs.append(f'\x1b[31mRenaming failed: {", ".join(e.illegal_names)} already exist\x1b[0m')
            self.__display_metadata_upload_summary(prepend_msgs=msgs)
        rename_button.on_click(apply_rename)

    def __open_graph_config(self):
        earliest, latest = vtna.data_import.get_time_interval_of_edges(self.__edge_list)
        update_delta = vtna.data_import.infer_update_delta(self.__edge_list)

        granularity_bounded_int_text = widgets.BoundedIntText(
            description='Granularity',
            value=update_delta,
            min=update_delta,
            max=latest-earliest,
            step=update_delta,
            disabled=False
        )
        apply_granularity_button = widgets.Button(
            description='Apply',
            disabled=False,
            button_style='primary',
            tooltip='Use selected granularity on graph',
        )

        def update_granularity_and_graph_data_output(_):
            apply_granularity_button.disabled = True
            old_name = apply_granularity_button.description
            apply_granularity_button.description = 'Loading...'

            extra_msgs = []
            if (granularity_bounded_int_text.value < update_delta or
                    granularity_bounded_int_text.value > latest-earliest or
                    granularity_bounded_int_text.value % update_delta != 0):
                error_msg = f'\x1b[31m{granularity_bounded_int_text.value} is an invalid granularity\x1b[0m'
                extra_msgs.append(error_msg)
            else:
                self.__granularity = granularity_bounded_int_text.value
                self.__run_button.disabled = False
            self.__display_graph_upload_summary(prepend_msgs=extra_msgs)

            apply_granularity_button.description = old_name
            apply_granularity_button.disabled = False

        apply_granularity_button.on_click(update_granularity_and_graph_data_output)

        self.__graph_data__configuration_vbox.children = \
            [widgets.HBox([granularity_bounded_int_text, apply_granularity_button])]


def print_edge_stats(edges: typ.List[vtna.data_import.TemporalEdge]):
    print('Total Edges:', len(edges))
    print('Update Delta:', vtna.data_import.infer_update_delta(edges))
    print('Time Interval:', vtna.data_import.get_time_interval_of_edges(edges))


def create_html_metadata_summary(metadata: vtna.data_import.MetadataTable) -> str:
    col_names = metadata.get_attribute_names()
    categories = [metadata.get_categories(name) for name in col_names]
    max_categories = max(map(len, categories))

    table_rows = list()
    for row in range(max_categories):
        table_rows.append(list())
        for col in range(len(col_names)):
            if len(categories[col]) > row:
                table_rows[row].append(categories[col][row])
            else:
                table_rows[row].append('')

    header_html = f'<tr>{"".join(f"<th>{name}</th>" for name in col_names)}</tr>'
    body_html = ''.join('<tr>{}</tr>'.format(''.join(f'<td>{cell}</td>' for cell in row)) for row in table_rows)
    table_html = f"""
        <table>
            {header_html}
            {body_html}
        </table>
    """
    return table_html


class UIGraphDisplayManager(object):
    DEFAULT_UPDATE_DELTA = 20
    DEFAULT_LAYOUT_IDX = 0
    LAYOUT_FUNCTIONS = [
        vtna.layout.static_spring_layout,
        vtna.layout.flexible_spring_layout,
        vtna.layout.static_weighted_spring_layout,
        vtna.layout.flexible_weighted_spring_layout,
        vtna.layout.random_walk_pca_layout
    ]

    def __init__(self,
                 time_slider: widgets.IntSlider,
                 play: widgets.Play,
                 layout_vbox: widgets.VBox
                 ):
        self.__time_slider = time_slider
        self.__play = play
        self.__layout_vbox = layout_vbox

        self.__temp_graph = None  # type: vtna.graph.TemporalGraph
        self.__update_delta = UIGraphDisplayManager.DEFAULT_UPDATE_DELTA  # type: int
        self.__granularity = None  # type: int

        self.__layout_function = UIGraphDisplayManager.LAYOUT_FUNCTIONS[UIGraphDisplayManager.DEFAULT_LAYOUT_IDX]
        self.__layout = None  # type: typ.List[typ.Dict[int, typ.Tuple[float, float]]]

        layout_options = dict((func.name, func) for func in UIGraphDisplayManager.LAYOUT_FUNCTIONS)
        self.__layout_select = widgets.Dropdown(
            options=layout_options,
            value=UIGraphDisplayManager.LAYOUT_FUNCTIONS[UIGraphDisplayManager.DEFAULT_LAYOUT_IDX],
            description='Layout:',
            # Width of dropdown is based on maximal length of function name.
            layout=widgets.Layout(width=f'{max(map(len, layout_options.keys())) + 1}rem')
        )

        # left padding so the right align of the drop down label is simulated, I cannot get text-align to work,
        # so this is the alternative approach.
        self.__layout_description_output = widgets.Output(layout=widgets.Layout(padding='0 0 0 4rem'))
        self.__display_layout_description()

        self.__apply_layout_button = widgets.Button(
            description='Apply',
            disabled=False,
            button_style='primary',
            tooltip='Apply Layout',
        )

        self.__apply_layout_button.on_click(self.__build_apply_layout())

        self.__layout_vbox.children = [widgets.HBox([self.__layout_select, self.__apply_layout_button]),
                                       self.__layout_description_output]

    def init_temporal_graph(self,
                            edge_list: typ.List[vtna.data_import.TemporalEdge],
                            metadata: vtna.data_import.MetadataTable,
                            granularity: int
                            ):
        self.__temp_graph = vtna.graph.TemporalGraph(edge_list, metadata, granularity)
        # TODO: Allow selection of layout
        self.__layout = self.__layout_function(self.__temp_graph)

        self.__time_slider.min = 0
        self.__time_slider.max = len(self.__temp_graph)
        self.__time_slider.value = 0

        self.__play.min = 0
        self.__play.max = len(self.__temp_graph)
        self.__play.value = 0

        self.__update_delta = vtna.data_import.infer_update_delta(edge_list)

    def get_temporal_graph(self) -> vtna.graph.TemporalGraph:
        return self.__temp_graph

    # TODO: allow selection of layout
    def build_display_current_graph(self, fig_num: int) -> typ.Callable[[int], None]:
        def display_current_graph(current_time_step: int):
            graph = self.__temp_graph[current_time_step]
            plt.figure(fig_num, figsize=(8, 8))
            axes = plt.gca()
            axes.set_xlim((-1.2, 1.2))
            axes.set_ylim((-1.2, 1.2))
            nxgraph = vtna.utility.graph2networkx(graph)
            nx.draw_networkx(nxgraph, self.__layout[current_time_step], ax=axes, with_labels=False, node_size=75,
                             node_color='green')
            axes.set_title(f'time step: {current_time_step}')
            plt.show()

        return display_current_graph

    def __display_layout_description(self):
        description_html = '<p style="color: blue;">{}</p>'.format(self.__layout_function.description)

        with self.__layout_description_output:
            ipydisplay.clear_output()
            ipydisplay.display_html(ipydisplay.HTML(description_html))

    def __build_apply_layout(self):
        def apply_layout(_):
            # Disable button and change name to Loading...
            self.__apply_layout_button.disabled = True
            old_button_name = self.__apply_layout_button.description
            self.__apply_layout_button.description = 'Loading...'
            # Compute layout, may take time
            self.__layout_function = self.__layout_select.value
            self.__display_layout_description()
            self.__layout = self.__layout_function(self.__temp_graph)
            # Refresh display by jumping from original position -> +-1 -> original position.
            # Looks like an ugly fix to get a refresh, but I did not find a better way to do it.
            old_value = self.__play.value
            self.__play.value = old_value - 1 if old_value > 0 else old_value + 1
            self.__play.value = old_value
            # Enable button, restore old name
            self.__apply_layout_button.description = old_button_name
            self.__apply_layout_button.disabled = False
        return apply_layout
