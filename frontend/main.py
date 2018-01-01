import typing as typ
import urllib
import urllib.error

import fileupload
import IPython.display as ipydisplay
from ipywidgets import widgets
import matplotlib.pyplot as plt
import networkx as nx

import vtna.data_import
import vtna.filter
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

    def __display_graph_upload_summary(self, prepend_msgs: typ.List[str] = None):
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

    def __display_metadata_upload_summary(self, prepend_msgs: typ.List[str] = None):
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
            max=latest - earliest,
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
                    granularity_bounded_int_text.value > latest - earliest or
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


class UIAttributeQueriesManager(object):
    def __init__(self, metadata: vtna.data_import.MetadataTable, queries_main_vbox: widgets.VBox,
                 filter_box_layout: widgets.Layout):
        self.__queries_main_vbox = queries_main_vbox
        self.__filter_box_layout = filter_box_layout
        self.__metadata = transform_metadata_to_queries_format(metadata)

        self.__attributes_dropdown = None  # type: widgets.Dropdown
        self.__nominal_value_dropdown = None  # type: widgets.Dropdown
        self.__interval_value_int_slider = None  # type: widgets.Dropdown
        self.__ordinal_value_selection_range_slider = None  # type: widgets.Dropdown
        self.__color_picker = None  # type: widgets.ColorPicker
        self.__boolean_combination_dropdown = None  # type: widgets.Dropdown
        self.__add_new_filter_button = None  # type: widgets.Button
        self.__add_new_clause_msg_html = None  # type: widgets.HTML
        self.__filter_highlight_toggle_buttons = None  # type: widgets.ToggleButtons
        self.__queries_output_box = None  # type: widgets.Box

        self.__query_counter = 1  # type: int
        self.__queries = dict()  # type: typ.Dict
        self.__active_queries = list()  # type: typ.List[int]

        self.__build_queries_menu()

        self.__boolean_combination_dropdown.observe(self.__build_on_boolean_operator_change())
        self.__attributes_dropdown.observe(self.__build_on_attribute_change())
        self.__filter_highlight_toggle_buttons.observe(self.__build_on_mode_change())
        self.__add_new_filter_button.on_click(self.__build_add_query())
        self.__delete_all_queries_button.on_click(self.__build_delete_all_queries())

    def __build_queries_menu(self):
        attributes = list(self.__metadata.keys())
        initial_attribute = self.__metadata[attributes[0]]
        # Attribute drop down
        self.__attributes_dropdown = widgets.Dropdown(
            options=attributes,
            value=attributes[0],
            description='Attribute:',
            disabled=False,
        )
        # Nominal dropdown
        self.__nominal_value_dropdown = widgets.Dropdown(
            disabled=True if initial_attribute['type'] != 'N' else False,
            options=initial_attribute['values'] if initial_attribute['type'] == 'N' else ['Range'],
            value=initial_attribute['values'][0] if initial_attribute['type'] == 'N' else 'Range',
            description='Value:',
        )
        # Interval slider
        self.__interval_value_int_slider = widgets.IntRangeSlider(
            description='Value:',
            disabled=True if initial_attribute['type'] != 'I' else False,
            value=[35, 52],
            min=16,
            max=65,
            step=1,
            orientation='horizontal',
            readout=False if initial_attribute['type'] != 'I' else True,
            readout_format='d',
            layout=widgets.Layout(width='99%')
        )
        # Ordinal slider
        self.__ordinal_value_selection_range_slider = widgets.SelectionRangeSlider(
            description='Value:',
            options=initial_attribute['values'] if initial_attribute['type'] == 'O' else ['N/A'],
            index=(0, len(initial_attribute['values']) - 1) if initial_attribute['type'] == 'O' else (0, 0),
            disabled=True if initial_attribute['type'] != 'O' else False,
            layout=widgets.Layout(width='99%')
        )
        # Colorpicker
        self.__color_picker = widgets.ColorPicker(
            concise=False,
            value='blue',
            description='Color:',
            disabled=False
        )
        # Add new filter
        self.__add_new_filter_button = widgets.Button(
            disabled=False,
            description='Add new query',
            button_style='success',
            tooltip='Add filter',
            icon='plus',
            layout=widgets.Layout(width='auto')
        )
        # Delete all queries
        self.__delete_all_queries_button = widgets.Button(
            description='Reset',
            disabled=False,
            button_style='',
            tooltip='Reset filter',
            icon='refresh',
            layout=widgets.Layout(width='auto')
        )
        # switch between Filter mode or Highlight mode
        self.__filter_highlight_toggle_buttons = widgets.ToggleButtons(
            options=['Filter', 'Highlight'],
            description='',
            value='Highlight',
            button_style=''
        )
        # Query operations ('New/Not' is used to refer to a new filter with a root clause)
        self.__boolean_combination_dropdown = widgets.Dropdown(
            options=['NEW', 'NOT', 'AND', 'AND NOT', 'OR', 'OR NOT'],
            description='Operator:',
            value='NEW'
        )
        # display inputs depending on current initial data type
        if initial_attribute['type'] == 'O':
            self.__nominal_value_dropdown.layout.display = 'none'
            self.__interval_value_int_slider.layout.display = 'none'
        elif initial_attribute['type'] == 'I':
            self.__nominal_value_dropdown.layout.display = 'none'
            self.__ordinal_value_selection_range_slider.layout.display = 'none'
        else:
            self.__interval_value_int_slider.layout.display = 'none'
            self.__ordinal_value_selection_range_slider.layout.display = 'none'

        # Msg for colorpicker
        color_picker_msg_html = widgets.HTML(
            value="<span style='color:#7f8c8d'> Use the <i style='color:#9b59b6;' class='fa fa-paint-brush'></i> "
                  "to change the color of a query</span>")
        # Msg for add new clause
        self.__add_new_clause_msg_html = widgets.HTML(
            value="<span style='color:#7f8c8d'> Use the <i style='color:#2ecc71;' class='fa fa-plus-square'></i> "
                  "to add a clause to a query</span>")
        # Hiding msg untill 'operation' != New/Not
        self.__add_new_clause_msg_html.layout.visibility = 'hidden'
        # Main toolbar : Operator, Add
        main_toolbar_hbox = widgets.HBox([self.__boolean_combination_dropdown, self.__add_new_filter_button,
                                          self.__add_new_clause_msg_html],
                                         layout=widgets.Layout(width='100%', flex_flow='row', align_items='stretch'))
        # Queries toolbar: Reset(delete all), toggle mode
        queries_toolbar_hbox = widgets.HBox([self.__delete_all_queries_button, self.__filter_highlight_toggle_buttons])
        # form BOX
        queries_form_vbox = widgets.VBox(
            [self.__attributes_dropdown, self.__nominal_value_dropdown, self.__interval_value_int_slider,
             self.__ordinal_value_selection_range_slider, widgets.HBox([self.__color_picker, color_picker_msg_html]),
             main_toolbar_hbox])
        # Query output BOX
        self.__queries_output_box = widgets.Box([], layout=self.__filter_box_layout)
        # Put created components into correct container
        self.__queries_main_vbox.children = [queries_form_vbox, self.__queries_output_box, queries_toolbar_hbox]

    def __build_on_attribute_change(self) -> typ.Callable:
        def on_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                selected_attribute = self.__metadata[self.__attributes_dropdown.value]
                if selected_attribute['type'] == 'N':  # Selected attribute is nominal
                    # Activate nominal value dropdown
                    self.__nominal_value_dropdown.options = selected_attribute['values']
                    self.__nominal_value_dropdown.value = selected_attribute['values'][0]
                    self.__nominal_value_dropdown.disabled = False
                    self.__nominal_value_dropdown.layout.display = 'inline-flex'
                    # Hide interval and ordinal value sliders
                    # TODO: Not sure about these two lines, commented them out for now
                    # self.__interval_value_int_slider.disabled = True
                    # self.__interval_value_int_slider.readout = False
                    self.__interval_value_int_slider.layout.display = 'none'
                    self.__ordinal_value_selection_range_slider.layout.display = 'none'
                elif selected_attribute['type'] == 'I':  # Selected attribute is interval
                    # Activate interval value slider
                    self.__interval_value_int_slider.disabled = False
                    self.__interval_value_int_slider.readout = True
                    self.__interval_value_int_slider.value = selected_attribute['values']
                    self.__interval_value_int_slider.min = min(selected_attribute['values'])
                    self.__interval_value_int_slider.max = max(selected_attribute['values'])
                    self.__interval_value_int_slider.layout.display = 'inline-flex'
                    # Hide nominal dropdown and ordinal slider
                    self.__nominal_value_dropdown.layout.display = 'none'
                    self.__ordinal_value_selection_range_slider.layout.display = 'none'
                elif selected_attribute['type'] == 'O':  # Selected attribute is ordinal
                    # Activate ordinal value slider
                    self.__ordinal_value_selection_range_slider.disabled = False
                    self.__ordinal_value_selection_range_slider.readout = True
                    self.__ordinal_value_selection_range_slider.options = selected_attribute['values']
                    self.__ordinal_value_selection_range_slider.index = (0, len(selected_attribute) - 1)
                    self.__ordinal_value_selection_range_slider.layout.display = 'inline-flex'
                    # Hide nominal dropdown and interval slider
                    self.__nominal_value_dropdown.layout.display = 'none'
                    self.__interval_value_int_slider.layout.display = 'none'

        return on_change

    def __build_on_boolean_operator_change(self) -> typ.Callable:
        def on_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                new_operator = self.__boolean_combination_dropdown.value
                ipydisplay.display(ipydisplay.Javascript(f"je.setOperator('{new_operator}').adjustButtons();"))
                if new_operator in ['NEW', 'NOT']:
                    self.__add_new_filter_button.disabled = False
                    self.__add_new_clause_msg_html.layout.visibility = 'hidden'
                else:
                    self.__add_new_filter_button.disabled = True
                    self.__add_new_clause_msg_html.layout.visibility = 'visible'

        return on_change

    def __construct_query(self, query_id: int):
        # check which mode
        is_filter = self.__filter_highlight_toggle_buttons.value == 'Filter'
        current_operator = self.__boolean_combination_dropdown.value
        # check if new filter or a clause (this is used for css reasons and as a workaround JS issues)
        is_new = current_operator in ['NEW', 'NOT']
        # check if this query is active
        is_active = query_id in self.__active_queries
        html_string = '<ul class="query-row">'
        # delete query button
        html_string += f'<li><button class="query-btn btn-del" onclick="deleteQuery({str(query_id)})">' \
                       f'<i class="fa fa-trash"></i></button>'
        # toggle actif/inactif button
        html_string += f'<button class="query-btn btn-toggle" onclick="switchQuery({str(query_id)})">' \
                       f'<i class="fa ' + ['fa-toggle-off', 'fa-toggle-on'][is_active] + '"></i></button>'
        # paint query with new color button
        html_string += f'<button class="query-btn btn-brush" onclick="paintQuery({str(query_id)})">' \
                       f'<i class="fa fa-paint-brush"></i></button>'
        # Query bullet point in color
        html_string += '<span class="flt-element flt-row-bullet {}" style="background: {};">' \
                       '</span></li>'.format(['', 'filter-mode'][is_filter], self.__queries[query_id]['color'])
        # start of the row-item
        html_string += '<li><span class="flt-element flt-row-item {}" style="color: {};">'.format(
            ['', 'filter-mode'][is_filter], self.__queries[query_id]['color'])
        for key, clause in self.__queries[query_id]['clauses'].items():
            # Operator attribute -> value

            html_string += '<b>{}</b>{} &#8702; '.format(['', str(clause['operator'])][clause['operator'] != 'NEW'],
                                                         str(clause['value'][0]))
            if self.__metadata[clause['value'][0]]['type'] == 'N':
                html_string += str(clause['value'][1]) + ' '
            else:
                html_string += 'From {} to {}'.format(str(clause['value'][1][0]), str(clause['value'][1][1]))
            # adding 'minus' button to remove clause
            html_string += f'<button class="query-btn btn-del" onclick="deleteQueryClause({str(query_id)},' \
                           f'{str(key)})"><i class="fa fa-minus-square"></i></button>'
        # adding 'plus' button to add new clause
        html_string += '<button class="query-btn btn-add {}" {} onclick="addQueryClause({})"> ' \
                       '<i class="fa fa-plus-square"></i></button></span></li>' \
                       '</ul>'.format(['', 'btn-disabled'][is_new], ['', 'disabled'][is_new], str(query_id))
        # lookup the widget and reassign the HTML value
        for i in range(len(self.__queries_output_box.children)):
            id_ = self.__queries_output_box.children[i].children[0].description
            if int(id_) == query_id:
                self.__queries_output_box.children[i].children[1].value = html_string
                break

    def __fetch_current_value(self) -> typ.Any:
        attribute_type = self.__metadata[self.__attributes_dropdown.value]['type']
        return {'N': self.__nominal_value_dropdown.value,
                'I': self.__interval_value_int_slider,
                'O': self.__ordinal_value_selection_range_slider}[attribute_type]

    def __build_add_query(self) -> typ.Callable:
        def on_click(_):
            self.__active_queries.append(self.__query_counter)
            current_value = self.__fetch_current_value()
            self.__queries[self.__query_counter] = \
                {'color': self.__color_picker.value,
                 'clauses': {1: {'operator': 'NEW',
                                 'value': (self.__attributes_dropdown.value, current_value)}}}
            w_0 = widgets.Text(description=str(self.__query_counter), layout=widgets.Layout(display='none'))
            w_1 = widgets.HTML(value=' ', layout=widgets.Layout(display='inline-block'))
            self.__queries_output_box.children += (widgets.HBox([w_0, w_1], layout=widgets.Layout(display='block')),)
            self.__construct_query(self.__query_counter)
            self.__query_counter += 1

        return on_click

    def build_add_query_clause(self) -> typ.Callable:
        def on_click(query_id):
            value = self.__fetch_current_value()
            self.__queries[query_id]['clauses'][max(self.__queries[query_id]['clauses'], key=int) + 1] = \
                {'operator': self.__boolean_combination_dropdown.value,
                 'value': (self.__attributes_dropdown.value, value)}
            self.__construct_query(query_id)

        return on_click

    def build_delete_query_clause(self) -> typ.Callable:
        def on_click(query_id, clause_id):
            self.__queries[query_id]['clauses'].pop(clause_id)
            if len(self.__queries[query_id]['clauses']) == 0:
                keep = []
                for i in range(len(self.__queries_output_box.children)):
                    if str(query_id) != self.__queries_output_box.children[i].children[0].description:
                        keep.append(self.__queries_output_box.children[i])
                        self.__queries_output_box.children = keep
            else:
                cl_ = next(iter(self.__queries[query_id]['clauses'].values()))
                op_ = cl_['operator'].split(' ')
                if len(op_) == 2:
                    cl_['operator'] = op_[1]
                else:
                    cl_['operator'] = 'NEW'
                self.__construct_query(query_id)

        return on_click

    def build_delete_query(self) -> typ.Callable:
        def on_click(query_id):
            self.__queries.pop(query_id)
            keep = []
            for i in range(len(self.__queries_output_box.children)):
                if str(query_id) != self.__queries_output_box.children[i].children[0].description:
                    keep.append(self.__queries_output_box.children[i])
            self.__queries_output_box.children = keep

        return on_click

    def build_switch_query(self) -> typ.Callable:
        def on_click(query_id):
            q_id = int(query_id)
            if q_id in self.__active_queries:
                self.__active_queries.remove(q_id)
            else:
                self.__active_queries.append(q_id)
            self.__construct_query(q_id)

        return on_click

    def build_paint_query(self) -> typ.Callable:
        def on_click(query_id):
            self.__queries[query_id]['color'] = self.__color_picker.value
            self.__construct_query(query_id)

        return on_click

    def __build_delete_all_queries(self) -> typ.Callable:
        def on_click(_):
            self.__queries_output_box.children = []
            self.__queries = dict()
            self.__query_counter = 1

        return on_click

    def __build_on_mode_change(self) -> typ.Callable:
        def on_mode_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                ipydisplay.display(ipydisplay.Javascript("je.setMode('" + self.__filter_highlight_toggle_buttons.value
                                                         + "').switchMode();"))

        return on_mode_change


def transform_metadata_to_queries_format(metadata: vtna.data_import.MetadataTable) -> typ.Dict[str, typ.Dict]:
    result = dict((name,
                   {'type': 'O' if metadata.is_ordered(name) else 'N',
                    'values': metadata.get_categories(name)})
                  for name in metadata.get_attribute_names())
    return result


def transform_queries_to_filter(queries: typ.Dict, metadata: vtna.data_import.MetadataTable, ) -> vtna.filter.NodeFilter:
    clauses = list()  # type: typ.List[vtna.filter.NodeFilter]
    for raw_clause in map(lambda t: t[1]['clauses'], sorted(queries.items(), key=lambda t: int(t[0]))):
        clause = build_clause(raw_clause, metadata)
        clauses.append(clause)
    result_filter = None
    for i, clause in enumerate(clauses):
        if i == 0:
            result_filter = clause
        else:
            result_filter += clause
    return result_filter


def transform_queries_to_color_mapping(queries: typ.Dict, metadata: vtna.data_import.MetadataTable,
                                       temp_graph: vtna.graph.TemporalGraph, default_color: str) \
        -> typ.Dict[int, str]:
    # Init all nodes with the default color
    colors = dict((node.get_id(), default_color) for node in temp_graph.get_nodes())
    for raw_clauses in map(lambda t: t[1], sorted(queries.items(), key=lambda t: int(t[1]), reverse=True)):
        raw_clause = raw_clauses['clauses']
        color = raw_clauses['color']
        clause = build_clause(raw_clause, metadata)
        nodes_to_color = clause(temp_graph.get_nodes())
        for node_id in map(lambda n: n.get_id(), nodes_to_color):
            colors[node_id] = color
    return colors


def build_clause(raw_clause: typ.Dict, metadata: vtna.data_import.MetadataTable) \
        -> vtna.filter.NodeFilter:
    clause = None
    for raw_predicate in map(lambda t: t[1], sorted(raw_clause.items(), key=lambda t: int(t[0]))):
        predicate = build_predicate(raw_predicate, metadata)
        node_filter = vtna.filter.NodeFilter(predicate)
        # Case distinction for different operators:
        op = raw_predicate['operator']
        if op == 'NEW':
            clause = node_filter
        elif op == 'NOT':
            clause = -node_filter
        elif op == 'AND':
            clause *= node_filter
        elif op == 'OR':
            clause += node_filter
        elif op == 'AND NOT':
            clause *= -node_filter
        elif op == 'OR NOT':
            clause += -node_filter
        else:
            # Either the front end provided a bad queries dict, or the matching is not correct.
            raise Exception(f'Unknown filter combinator: {op}')
    return clause


def build_predicate(raw_predicate: typ.Dict, metadata: vtna.data_import.MetadataTable) \
        -> typ.Callable[[vtna.graph.TemporalNode], bool]:
    # TODO: Currently assumes only string type values. More case distinctions needed for more complex types.
    # build_predicate assumes correctness of the input in regards to measure type assumptions.
    # e.g. range type queries will only be made for truly ordinal or interval values.
    name, value = raw_predicate['value']
    if isinstance(value, (list, tuple)):  # Range type
        order = metadata.get_categories(name)
        lower_bound = vtna.filter.ordinal_attribute_greater_than_equal(name, value[0], order)
        inv_upper_bound = vtna.filter.ordinal_attribute_greater_than(name, value[1], order)
        pred = lambda n: lower_bound(n) and not inv_upper_bound(n)
    else:  # Equality
        pred = vtna.filter.categorical_attribute_equal(name, value)
    return pred
