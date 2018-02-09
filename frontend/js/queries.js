var JsEngine = function () {
    this.kernel = IPython.notebook.kernel;
    this.operator = 'NEW';
    this.mode = 'Filter';
};


JsEngine.prototype.execute = function (command) {
    this.kernel.execute(command);
    return this;
};

JsEngine.prototype.setOperator = function (operator) {
    this.operator = operator;
    return this;
};

JsEngine.prototype.setMode = function (mode) {
    this.mode = mode;
    return this;
};


JsEngine.prototype.switchMode = function () {
    if (this.mode == 'Filter') {
        $(".flt-element").addClass('filter-mode');
    } else {
        $(".flt-element").removeClass('filter-mode');
    }
    return this;
};

var je = new JsEngine();

// https://www.w3schools.com/howto/howto_js_dropdown.asp (dropdown-related code)
function openAddQueryOperatorDropdown(elem, dropdown_elem_id, query_id) {
    $('body').append("<div id=\"" + dropdown_elem_id + "\" class=\"query-add-dropdown-content\">\n" +
        "<a onclick=\"addQueryClause(" + query_id + ", 'AND')\">AND</a>\n" +
        "<a onclick=\"addQueryClause(" + query_id + ", 'OR')\">OR</a>\n" +
        "<a onclick=\"addQueryClause(" + query_id + ", 'AND NOT')\">AND NOT</a>\n" +
        "<a onclick=\"addQueryClause(" + query_id + ", 'OR NOT')\">OR NOT</a>\n" +
        "</div>");
    let left = $(elem).offset().left + $(elem).width();
    let top = $(elem).offset().top + $(elem).height();
    $('#' + dropdown_elem_id).css('left', left);
    $('#' + dropdown_elem_id).css('top', top);
}

window.addEventListener('click', function(event) {
    if (!event.target.matches('.query-add-btn-box *,.query-add-btn-box')) {
        $('.query-add-dropdown-content').remove();
    }
}, false);

function addQueryClause(q_id, operator) {
    je.execute('addQueryClause(' + q_id + ', "' + operator + '")');
}

function deleteQueryClause(q_id, c_id) {
    je.execute('deleteQueryClause(' + q_id + ',' + c_id + ')');
}

function switchQuery(q_id) {
    je.execute('switchQuery(' + q_id + ')');
}

function deleteQuery(q_id) {
    je.execute('deleteQuery(' + q_id + ')');
}

function paintQuery(q_id) {
    je.execute('paintQuery(' + q_id + ')');
}
