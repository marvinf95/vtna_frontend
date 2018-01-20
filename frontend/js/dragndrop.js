var kernel = IPython.notebook.kernel;

var getUlList = function (id) {
    return document.getElementById("attr_list" + id);
}

var enableSorting = function (id) {
    var ul_list = getUlList(id);
    // For changing list style to make sortability visible
    ul_list.classList.add('sortlist')
    sortable(ul_list, {
        forcePlaceholderSize: true
    })[0].addEventListener('sortupdate', function(e) {
        /*
        This event is triggered when the user stopped sorting and the DOM position has changed.
        e.detail.newEndList contains all elements in the list the dragged item was dragged to
        */
        var orderList = e.detail.newEndList;
        console.log(orderList);
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
        notifyMain();

    });
    kernel.execute("order_enabled[" + id + "] = True");
    notifyMain();
};

var disableSorting = function (id) {
    var ul_list = getUlList(id);
    // Remove from css class if attached
    if(ul_list.classList.contains('sortlist')) {
        ul_list.classList.remove('sortlist');
    }
    // Removes sortability listeners
    sortable(ul_list, 'destroy');
    kernel.execute("order_enabled[" + id + "] = False");
    notifyMain();
};

var notifyMain = function () {
    // Call set order method in main.py to store values already in main,
    // for easier restoring of values after redrawing the metadata table
    kernel.execute("upload_manager.set_attribute_order(order_dict, order_enabled)");
}

function toggleSortable(checkbox) {
    if(checkbox.checked) {
        enableSorting(checkbox.value)
    } else {
        disableSorting(checkbox.value)
    }
};
