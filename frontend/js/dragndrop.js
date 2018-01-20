var kernel = IPython.notebook.kernel;

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
        var updateDictsCommand = "order_dict[" + id + "] = {";
        for (var i = 0; i < orderList.length; i++) {
            updateDictsCommand += i + ": " + orderList[i].value;
            // Append comma if not last dictionary entry
            if (i < orderList.length - 1) {
                updateDictsCommand += ", ";
            }
        }
        updateDictsCommand += "}"
        kernel.execute(updateDictsCommand);
        // Call set order method in main.py to store values already in main,
        // for easier restoring of values after redrawing the metadata table
        kernel.execute("upload_manager.set_attribute_order(order_dict, order_enabled)");

    });
    kernel.execute("order_enabled[" + id + "] = True");
};

var disableSorting = function (ul_list, id) {
    // Removes sortability listeners
    sortable(ul_list, 'destroy');
    kernel.execute("order_enabled[" + id + "] = False");
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
