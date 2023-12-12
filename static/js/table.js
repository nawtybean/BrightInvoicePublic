// @author: Shaun De Ponte, nawtybean3d@gmail.com

// ----- The MIT License (MIT) ----- 
// Copyright (c) 2023, Shaun De Ponte

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.



function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function drawTable(data, table_name) {
    try {
        if (data.data.length <= 0 || data.data[0].id === null) {
            // no data, clear table
            var tableHolder = $("#data-table-" + table_name + "_wrapper").parent();
            if (tableHolder.length > 0) {
                tableHolder.html("<table id=\"data-table-" + table_name + "\" class=\"table table-hover responsive\" width=\"100%\"></table>");
            }
            return;
        }

        var columns = [];
        columnNames = Object.keys(data.data[0])

        for (var i in columnNames) {
            columns.push({
                data: columnNames[i],
                title: columnNames[i],
            });
        }
        $('#data-table-' + table_name).DataTable({
            fixedHeader: {
                footer: true
            },
            destroy: true,
            "dom": '<"float-left"f><"float-right"l>tip',
            responsive: true,
            scrollX: true,
            data: data.data,
            columns: columns,
            columnDefs: [
                {
                    targets: -1,
                    className: 'dt-body-right',
                    render: function (data, type, item, full, meta) {
                        if (type === 'display') {
                                if(user_type === 4)
                                {
                                    if(show_hide_next === 0)
                                    {
                                        data = "<button class=\"btn btn-success\" onclick=\"edit_item(" + item.id + ", '" + table_name + "')\" type=\"button\" style=\"margin-right: 10px\"><i class=\"far fa-edit\"></i></button>" +
                                        "<button class=\"btn btn-danger\" onclick=\"delete_item(" + item.id + ", '" + table_name + "')\" type=\"button\" style=\"margin-right: 10px\"><i class=\"fa fa-trash\"></i> </button>";
                                    }
                                    else if (show_hide_next === 2)
                                    {
                                        data = "<button class=\"btn btn-success\" onclick=\"edit_item('" + table_name + "')\" type=\"button\" style=\"margin-right: 10px\"><i class=\"far fa-edit\"></i></button>";
                                    }
                                    else
                                    {
                                        data = "<button class=\"btn btn-success\" onclick=\"edit_item(" + item.id + ", '" + table_name + "')\" type=\"button\" style=\"margin-right: 10px\"><i class=\"far fa-edit\"></i></button>" +
                                        "<button class=\"btn btn-danger\" onclick=\"delete_item(" + item.id + ", '" + table_name + "')\" type=\"button\" style=\"margin-right: 10px\"><i class=\"fa fa-trash\"></i> </button>" +
                                        "<button class=\"btn btn-primary\" onclick=\"session_detail(" + item.id + ")\" type=\"button\"><i class=\"fa fa-arrow-right\"></i> </button>";
                                    }
                                }
                        }
                        return data;
                    }
                },
                {
                    "targets": [0,],
                    "visible": false
                }
            ],
        });
    }
    catch (e){};
};