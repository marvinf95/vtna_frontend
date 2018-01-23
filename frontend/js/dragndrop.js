var kernel = IPython.notebook.kernel;

function handlePythonOutput(data){
        console.log(data.content);
    }
var pythonCallback = {
        iopub : {
             output : handlePythonOutput,
    }
}

var enableSorting = function (ul_list, id) {
    sortable(ul_list, {
        forcePlaceholderSize: true
    })[0].addEventListener('sortupdate', function(e) {
        /*
        This event is triggered when the user stopped sorting and the DOM position has changed.
        e.detail.newEndList contains all elements in the list the dragged item was dragged to
        */
        var orderList = e.detail.newEndList;
        // Assign values to python dictionary
        var updateDictCommand = "order_dict[" + id + "] = [";
        for (var i = 0; i < orderList.length; i++) {
            updateDictCommand += "'" + orderList[i].textContent + "'";
            // Append comma if not last dictionary entry
            if (i < orderList.length - 1) {
                updateDictCommand += ", ";
            }
        }
        updateDictCommand += "]";
        kernel.execute(updateDictCommand, pythonCallback);
        // Update metadata order after every change
        kernel.execute("upload_manager.set_attribute_order(order_dict)", pythonCallback);

    });
    //kernel.execute("order_enabled[" + id + "] = True", pythonCallback);
    kernel.execute("upload_manager.toggle_order_enabled(id_=" + id + ", enabled=True)", pythonCallback);
};

var disableSorting = function (ul_list, id) {
    // Removes sortability listeners
    sortable(ul_list, 'destroy');
    kernel.execute("upload_manager.toggle_order_enabled(id_=" + id + ", enabled=False)", pythonCallback);
};

function toggleSortable(checkbox) {
    // Choose the attribute list corresponding to the toggled checkbox
    ul_list = document.getElementById("attr_list" + checkbox.value);
    if(checkbox.checked) {
        // For changing list style to make sortability visible
        ul_list.classList.add('sortlist')
        enableSorting(ul_list, checkbox.value)
    } else {
        if(ul_list.classList.contains('sortlist')) {
            ul_list.classList.remove('sortlist');
        }
        disableSorting(ul_list, checkbox.value)
    }
};
