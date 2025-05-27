/**
 * DataTables Basic
 */

'use strict';

$(function () {
  var dt_basic_table = $('.product-datatables-basic'),
    dt_basic;

  // DataTable with buttons
  // --------------------------------------------------------------------

  if (dt_basic_table.length) {
    dt_basic = dt_basic_table.DataTable({
      ajax: '/product-data/', // Fetch data from the Django endpoint
      columns: [
        { data: null, defaultContent: '' }, // Control column
        { data: null, defaultContent: '' }, // Checkbox column
        { data: 'product_id' },
        { data: 'product_name' },
        { data: 'category' },
        { data: 'brand' },
        { data: 'unit_price' },
        { data: 'supplier' },
        { data: null, defaultContent: '' } // Actions column
      ],
      columnDefs: [
        {
          className: 'control',
          orderable: false,
          searchable: false,
          responsivePriority: 2,
          targets: 0,
          render: function (data, type, full, meta) {
            return '';
          }
        },
        {
          targets: 1,
          orderable: false,
          searchable: false,
          responsivePriority: 3,
          render: function () {
            return '<input type="checkbox" class="dt-checkboxes form-check-input">';
          },
          checkboxes: {
            selectAllRender: '<input type="checkbox" class="form-check-input">'
          }
        },
        {
          targets: -1,
          title: 'Actions',
          orderable: false,
          searchable: false,
          render: function (data, type, full, meta) {
            return (
              '<div class="d-inline-block">' +
              '<a href="javascript:;" class="btn btn-sm btn-icon dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="text-primary ti ti-dots-vertical"></i></a>' +
              '<ul class="dropdown-menu dropdown-menu-end m-0">' +
              '<li><a href="javascript:;" class="dropdown-item">Details</a></li>' +
              '<div class="dropdown-divider"></div>' +
              '<li><a href="javascript:;" class="dropdown-item text-danger delete-record">Delete</a></li>' +
              '</ul>' +
              '</div>' +
              '<a href="javascript:;" class="btn btn-sm btn-icon item-edit" data-bs-toggle="modal" data-bs-target="#productModal" data-product-id="' + full.product_id + '"><i class="text-primary ti ti-pencil"></i></a>'
            );
          }
        }
      ],
      order: [[2, 'desc']],
      dom: '<"card-header flex-column flex-md-row"<"head-label text-center"><"dt-action-buttons text-end pt-3 pt-md-0"B>><"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>>t<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
      displayLength: 7,
      lengthMenu: [7, 10, 25, 50, 75, 100],
      buttons: [
        {
          extend: 'collection',
          className: 'btn btn-label-primary dropdown-toggle me-2',
          text: '<i class="ti ti-file-export me-sm-1"></i> <span class="d-none d-sm-inline-block">Export</span>',
          buttons: [
            {
              extend: 'print',
              text: '<i class="ti ti-printer me-1" ></i>Print',
              className: 'dropdown-item',
              exportOptions: {
                columns: [2, 3, 4, 5, 6, 7]
              }
            },
            {
              extend: 'csv',
              text: '<i class="ti ti-file-text me-1" ></i>Csv',
              className: 'dropdown-item',
              exportOptions: {
                columns: [2, 3, 4, 5, 6, 7]
              }
            },
            {
              extend: 'excel',
              text: '<i class="ti ti-file-spreadsheet me-1"></i>Excel',
              className: 'dropdown-item',
              exportOptions: {
                columns: [2, 3, 4, 5, 6, 7]
              }
            },
            {
              extend: 'pdf',
              text: '<i class="ti ti-file-description me-1"></i>Pdf',
              className: 'dropdown-item',
              exportOptions: {
                columns: [2, 3, 4, 5, 6, 7]
              }
            },
            {
              extend: 'copy',
              text: '<i class="ti ti-copy me-1" ></i>Copy',
              className: 'dropdown-item',
              exportOptions: {
                columns: [2, 3, 4, 5, 6, 7]
              }
            }
          ]
        },
        {
          text: '<i class="ti ti-plus me-sm-1"></i> <span class="d-none d-sm-inline-block">Add New Record</span>',
          className: 'create-new btn btn-primary',
          attr: {
            'data-bs-toggle': 'modal',
            'data-bs-target': '#productModal'
          },
          init: function (api, node) {
            $(node).removeClass('btn-secondary');
          }
        }
      ],
      responsive: {
        details: {
          display: $.fn.dataTable.Responsive.display.modal({
            header: function (row) {
              var data = row.data();
              return 'Details of ' + data['product_name'];
            }
          }),
          type: 'column',
          renderer: function (api, rowIdx, columns) {
            var data = $.map(columns, function (col, i) {
              return col.title !== ''
                ? '<tr data-dt-row="' + col.rowIndex + '" data-dt-column="' + col.columnIndex + '">' +
                    '<td>' + col.title + ':</td> ' +
                    '<td>' + col.data + '</td>' +
                  '</tr>'
                : '';
            }).join('');
            return data ? $('<table class="table"/><tbody />').append(data) : false;
          }
        }
      }
    });
  }

  // Delete Record
  $('.product-datatables-basic tbody').on('click', '.delete-record', function () {
    dt_basic.row($(this).parents('tr')).remove().draw();
  });

  // After initializing the DataTable
  $('.head-label.text-center').html('<h5 class="card-title mb-0">Product Catalog</h5>');

  // Filter form control to default size
  setTimeout(() => {
    $('.dataTables_filter .form-control').removeClass('form-control-sm');
    $('.dataTables_length .form-select').removeClass('form-select-sm');
  }, 300);
});

// Handle form submission using Fetch API
document.getElementById('productForm').addEventListener('submit', function (e) {
  e.preventDefault();

  const formData = new FormData(this);

  // Ensure the CSRF token is correctly retrieved
  const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
  if (!csrfTokenElement) {
    console.error('CSRF token not found. Ensure the input field with name="csrfmiddlewaretoken" exists.');
    return;
  }

  const csrfToken = csrfTokenElement.value;

  fetch(this.action, {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': csrfToken
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert(data.message);
        location.reload(); // Reload the page or update the table dynamically
      } else {
        // Display validation errors
        for (const [field, errors] of Object.entries(data.errors)) {
          const input = document.querySelector(`[name=${field}]`);
          if (input) {
            const errorContainer = input.nextElementSibling;
            errorContainer.innerHTML = errors.join('<br>');
            input.classList.add('is-invalid');
          }
        }
      }
    })
    .catch(error => console.error('Error:', error));
});