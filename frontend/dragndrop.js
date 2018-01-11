var enableSorting = function (ul_list, id) {
    sortable(ul_list, {
        forcePlaceholderSize: true
    })[0].addEventListener('sortupdate', function(e) {
        /*
        This event is triggered when the user stopped sorting and the DOM position has changed.
        e.detail.newEndList contains all elements in the list the dragged item was dragged to
        */
        var orderList = e.detail.newEndList;
        var kernel = IPython.notebook.kernel;
        // Assign values to python dictionary
        var pythonCommand = "order_list['" + id + "'] = {";
        for (var i = 0; i < orderList.length; i++) {
            pythonCommand += "'" + i + "': " + orderList[i].value;
            // Append comma if not last dictionary entry
            if (i < orderList.length - 1) {
                pythonCommand += ",";
            }
        }
        pythonCommand += "}"
        kernel.execute(pythonCommand);
    });
};

var disableSorting = function (ul_list, id) {
    sortable(ul_list, 'destroy')
};

function toggleSortable(checkbox) {
    ul_list = document.getElementById("attr_list" + checkbox.value);
    if(checkbox.checked) {
        ul_list.classList.add('sortlist')
        enableSorting(ul_list, checkbox.value)
    } else {
        if(ul_list.classList.contains('sortlist')) {
            ul_list.classList.remove('sortlist');
        }
        disableSorting(ul_list, checkbox.value)
    }
};
