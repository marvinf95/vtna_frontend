// This is just a callback construct, so python output and errors
// (stdout + stderr) on executing a kernel command can be
// viewed in a browser console.
function handle_output(data){
    console.log(data.content);
}
var callbacks = {
        iopub : {
             output : handle_output,
    }
}

var removePlot = function(id) {
    var tmpPlot = document.getElementById("tmp-plotly-plot" + id);
    if(tmpPlot != null) {
        // Note that we remove the grandparent, because jupyter embeds the plot in other divs.
        // Removing these will also prevent ugly whitespaces in the notebook
        tmpPlot.parentElement.parentElement.parentElement.removeChild(tmpPlot.parentElement.parentElement);
        // Probably not necessary I guess?
        delete tmpPlot;
    }
}

var extractPlotlyImage = function () {
    // Returns a Promise
    // We choose the second element with that class, because the first one
    // is our real plot
    Plotly.toImage(document.getElementsByClassName("plotly-graph-div")[1])
        .then(function(imgData) {
            // Remove data URL prefix and call main's callback method
            var command = "display_manager.write_export_frame(b'" + imgData.replace("data:image/png;base64,", "") + "')";
            IPython.notebook.kernel.execute(command, callbacks);
    });
}
