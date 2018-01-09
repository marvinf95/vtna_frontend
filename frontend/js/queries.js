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


JsEngine.prototype.adjustButtons = function () {
    if (['NEW', 'NOT'].indexOf(this.operator) >= 0) {
        $('.btn-add').prop('disabled', true);
        $('.btn-add').addClass('btn-disabled');
    } else {
        $('.btn-add').prop('disabled', false);
        $('.btn-add').removeClass('btn-disabled');
    }
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


function addQueryClause(q_id) {
    je.execute('addQueryClause(' + q_id + ')');
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
