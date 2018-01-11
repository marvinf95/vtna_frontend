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
        kernel.execute("order_list[" + id + "].clear()");
        for (var i = 0; i < orderList.length; i++) {
            kernel.execute("order_list[" + id + "].append(" + orderList[i].value + ")");
        }
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
