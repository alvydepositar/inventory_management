/**
 * DataTables Basic
 */

'use strict';
let productModalInstance = null;
let categoryModalInstance = null;
let brandModalInstance = null;

// Product DataTable and Modal
if (document.getElementById('productModal')) {
  document.getElementById('productModal').addEventListener('hidden.bs.modal', function () {
    // Reset the form when the modal is closed
    document.getElementById('productForm').reset();
    document.querySelectorAll('#productForm input').forEach(input => {
      input.classList.remove('is-invalid');
      const errorContainer = input.nextElementSibling;
      if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
        errorContainer.innerHTML = '';
      }
    });
  });

  $(function () {
  productModalInstance = new bootstrap.Modal(document.getElementById('productModal'));
  var dt_basic_table = $('.product-datatables-basic'),
    dt_basic;

  // DataTable with buttons
  // --------------------------------------------------------------------

  if (dt_basic_table.length) {
    dt_basic = dt_basic_table.DataTable({
      ajax: '/product-data/', // Fetch data from the Django endpoint
      columns: [
        { data: null, defaultContent: '' }, // Control column
        { data: 'id' }, // Checkbox column
        { data: 'product_id' },
        { data: 'product_name' },
        { data: 'category' },
        { data: 'brand' },
        { data: 'unit_price' },
        { data: 'supplier' },
        { data: 'id', defaultContent: '' } // Actions column
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
              '<li><a href="javascript:;" class="dropdown-item item-view" data-bs-toggle="modal" data-bs-target="#productModal" data-id="' + full.id + '">Details</a></li>' +
              '<div class="dropdown-divider"></div>' +
              '<li><a href="javascript:;" class="dropdown-item text-danger delete-record">Delete</a></li>' +
              '</ul>' +
              '</div>' +
              '<a href="javascript:;" class="btn btn-sm btn-icon item-edit" data-bs-toggle="modal" data-bs-target="#productModal" data-id="' + full.id + '"><i class="text-primary ti ti-pencil"></i></a>'
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
              text: '<i class="ti ti-file-text me-1" ></i>CSV',
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
              text: '<i class="ti ti-file-description me-1"></i>PDF',
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

  // Handle view button click
  $('.product-datatables-basic tbody').on('click', '.item-view', function () {
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    // Fill modal fields
    $('#productModalLabel').text('View Product');
    $('#productForm').attr('action', '/view-product/' + data.id + '/');
    $('#productForm input[name="product_id"]').val(data.product_id).prop('readonly', true);
    $('#productForm input[name="product_name"]').val(data.product_name).prop('readonly', true);
    $('#productForm input[name="category"]').val(data.category).prop('readonly', true);
    $('#productForm input[name="brand"]').val(data.brand).prop('readonly', true);
    $('#productForm input[name="unit_price"]').val(data.unit_price).prop('readonly', true);
    $('#productForm input[name="supplier"]').val(data.supplier).prop('readonly', true);

    // Remove submit button
    $('#productForm button[type="submit"]').remove();
    
    productModalInstance.show();
  });

  // Handle edit button click
  $('.product-datatables-basic tbody').on('click', '.item-edit', function () {
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    // Fill modal fields
    $('#productModalLabel').text('Edit Product');
    $('#productForm').attr('action', '/edit-product/' + data.id + '/');
    $('#productForm input[name="product_id"]').val(data.product_id).prop('readonly', true);
    $('#productForm input[name="product_name"]').val(data.product_name);
    $('#productForm input[name="category"]').val(data.category);
    $('#productForm input[name="brand"]').val(data.brand);
    $('#productForm input[name="unit_price"]').val(data.unit_price);
    $('#productForm input[name="supplier"]').val(data.supplier);

    // Show the modal
    productModalInstance.show();
  });

  // Delete Record
  $('.product-datatables-basic tbody').on('click', '.delete-record', function () {
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    // Perform the delete action here
    if (confirm('Are you sure you want to delete this record?')) {
      // Send a request to the server to delete the record
      fetch('/delete-product/' + data.id, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            alert(data.message);
            row.remove().draw();
          } else {
            alert('Error deleting record: ' + data.message);
          }
        });
    }
  });

  // After initializing the DataTable
  $('.head-label.text-center').html('<h5 class="card-title mb-0">Product Catalog</h5>');

  // Filter form control to default size
  setTimeout(() => {
    $('.dataTables_filter .form-control').removeClass('form-control-sm');
    $('.dataTables_length .form-select').removeClass('form-select-sm');
  }, 300);
});
}

if (document.getElementById('productForm')) {
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
}

// Category DataTable and Modal
if (document.getElementById('categoryModal')) {
  document.getElementById('categoryModal').addEventListener('hidden.bs.modal', function () {
    // Reset the form when the modal is closed
    document.getElementById('categoryForm').reset();
    document.querySelectorAll('#categoryForm input').forEach(input => {
      input.classList.remove('is-invalid');
      const errorContainer = input.nextElementSibling;
      if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
        errorContainer.innerHTML = '';
      }
    });
  });

  $(function () {
    categoryModalInstance = new bootstrap.Modal(document.getElementById('categoryModal'));
    var dt_basic_table = $('.category-datatables-basic'),
      dt_basic;

    // DataTable with buttons
    // --------------------------------------------------------------------

    if (dt_basic_table.length) {
      dt_basic = dt_basic_table.DataTable({
        ajax: '/category-data/', // Fetch data from the Django endpoint
        columns: [
          { data: null, defaultContent: '' }, // Control column
          { data: 'id' }, // Checkbox column
          { data: 'name' },
          { data: 'id' } // Actions column
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
                '<li><a href="javascript:;" class="dropdown-item item-view" data-bs-toggle="modal" data-bs-target="#categoryModal" data-id="' + full.id + '">Details</a></li>' +
                '<div class="dropdown-divider"></div>' +
                '<li><a href="javascript:;" class="dropdown-item text-danger delete-record">Delete</a></li>' +
                '</ul>' +
                '</div>' +
                '<a href="javascript:;" class="btn btn-sm btn-icon item-edit" data-bs-toggle="modal" data-bs-target="#categoryModal" data-id="' + full.id + '"><i class="text-primary ti ti-pencil"></i></a>'
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
            text: '<i class="ti ti-plus me-sm-1"></i> <span class="d-none d-sm-inline-block">Add Category</span>',
            className: 'create-new btn btn-primary',
            attr: {
              'data-bs-toggle': 'modal',
              'data-bs-target': '#categoryModal'
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
                return 'Details of ' + data['name'];
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

    // Handle view button click
    $('.category-datatables-basic tbody').on('click', '.item-view', function () {
      var tr = $(this).closest('tr');
      var row = dt_basic.row(tr);
      var data = row.data();

      // Fill modal fields
      $('#categoryModalLabel').text('View Category');
      $('#categoryForm').attr('action', '/view-category/' + data.id + '/');
      $('#categoryForm input[name="name"]').val(data.name).prop('readonly', true);

      // Remove submit button
      $('#categoryForm button[type="submit"]').remove();

      categoryModalInstance.show();
    });

    // Handle edit button click
    $('.category-datatables-basic tbody').on('click', '.item-edit', function () {
      var tr = $(this).closest('tr');
      var row = dt_basic.row(tr);
      var data = row.data();

      // Fill modal fields
      $('#categoryModalLabel').text('Edit Category');
      $('#categoryForm').attr('action', '/edit-category/' + data.id + '/');
      $('#categoryForm input[name="name"]').val(data.name);

      // Bring the submit button back and cancel button side by side
      if (!$('#categoryForm button[type="submit"]').length && !$('#categoryForm button[type="button"]').length) {
        $('#categoryForm .col-12.text-center').html(`
          <button type="submit" class="btn btn-primary me-sm-3 me-1 waves-effect waves-light">Submit</button>
          <button type="button" class="btn btn-label-secondary waves-effect" data-bs-dismiss="modal">Cancel</button>
        `);
      } else {
        // If only one is missing, ensure both are present and styled side by side
        if (!$('#categoryForm button[type="submit"]').length) {
          $('#categoryForm .col-12.text-center').prepend(
            '<button type="submit" class="btn btn-primary me-sm-3 me-1 waves-effect waves-light">Submit</button>'
          );
        }
        if (!$('#categoryForm button[type="button"]').length) {
          $('#categoryForm .col-12.text-center').append(
            '<button type="button" class="btn btn-label-secondary waves-effect" data-bs-dismiss="modal">Cancel</button>'
          );
        }
      }

      // Show the modal
      categoryModalInstance.show();
    });

    // Delete Record
    $('.category-datatables-basic tbody').on('click', '.delete-record', function () {
      var tr = $(this).closest('tr');
      var row = dt_basic.row(tr);
      var data = row.data();

      // Perform the delete action here
      if (confirm('Are you sure you want to delete this record?')) {
        // Send a request to the server to delete the record
        fetch('/delete-category/' + data.id, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              alert(data.message);
              row.remove().draw();
            } else {
              alert('Error deleting record: ' + data.message);
            }
          });
      }
    });

    // After initializing the DataTable
    $('.category-datatables-basic').closest('.card').find('.head-label.text-center').html('<h5 class="card-title mb-0">Category Catalog</h5>');

    // Filter form control to default size
    setTimeout(() => {
      $('.dataTables_filter .form-control').removeClass('form-control-sm');
      $('.dataTables_length .form-select').removeClass('form-select-sm');
    }, 300);
  });
}

// Handle category form submission using Fetch. If page is category-catalog.html
if (document.getElementById('categoryForm')) {
  document.getElementById('categoryForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    const csrfTokenElement = document.querySelector("[name='csrfmiddlewaretoken']");
    if (!csrfTokenElement) {
      console.error('CSRF token not found. Ensure the CSRF input field exists in your form.');
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
}

// Brand DataTable and Modal
if (document.getElementById('brandModal')) {
  document.getElementById('brandModal').addEventListener('hidden.bs.modal', function () {
    // Reset the form when the modal is closed
    document.getElementById('brandForm').reset();
    document.querySelectorAll('#brandForm input').forEach(input => {
      input.classList.remove('is-invalid');
      const errorContainer = input.nextElementSibling;
      if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
        errorContainer.innerHTML = '';
      }
    });
  });

  $(function () {
    brandModalInstance = new bootstrap.Modal(document.getElementById('brandModal'));
    var dt_basic_table = $('.brand-datatables-basic'),
      dt_basic;

    // DataTable with buttons
    // --------------------------------------------------------------------

    if (dt_basic_table.length) {
      dt_basic = dt_basic_table.DataTable({
        ajax: '/brand-data/', // Fetch data from the Django endpoint
        columns: [
          { data: null, defaultContent: '' }, // Control column
          { data: 'id' }, // Checkbox column
          { data: 'name' },
          { data: 'id', defaultContent: '' } // Actions column
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
                '<li><a href="javascript:;" class="dropdown-item item-view" data-bs-toggle="modal" data-bs-target="#brandModal" data-id="' + full.id + '">Details</a></li>' +
                '<div class="dropdown-divider"></div>' +
                '<li><a href="javascript:;" class="dropdown-item text-danger delete-record">Delete</a></li>' +
                '</ul>' +
                '</div>' +
                '<a href="javascript:;" class="btn btn-sm btn-icon item-edit" data-bs-toggle="modal" data-bs-target="#brandModal" data-id="' + full.id + '"><i class="text-primary ti ti-pencil"></i></a>'
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
            text: '<i class="ti ti-plus me-sm-1"></i> <span class="d-none d-sm-inline-block">Add Brand</span>',
            className: 'create-new btn btn-primary',
            attr: {
              'data-bs-toggle': 'modal',
              'data-bs-target': '#brandModal'
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
                return 'Details of ' + data['name'];
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

    // Handle view button click
    $('.brand-datatables-basic tbody').on('click', '.item-view', function () {
      var tr = $(this).closest('tr');
      var row = dt_basic.row(tr);
      var data = row.data();

      // Fill modal fields
      $('#brandModalLabel').text('View Brand');
      $('#brandForm').attr('action', '/view-brand/' + data.id + '/');
      $('#brandForm input[name="name"]').val(data.name).prop('readonly', true);

      // Remove submit button and cancel button
      $('#brandForm button[type="submit"]').remove();

      brandModalInstance.show();
    });

    // Handle edit button click
    $('.brand-datatables-basic tbody').on('click', '.item-edit', function () {
      var tr = $(this).closest('tr');
      var row = dt_basic.row(tr);
      var data = row.data();

      // Fill modal fields
      $('#brandModalLabel').text('Edit Brand');
      $('#brandForm').attr('action', '/edit-brand/' + data.id + '/');
      $('#brandForm input[name="name"]').val(data.name);

      // Bring the submit button back and cancel button side by side
      if (!$('#brandForm button[type="submit"]').length && !$('#brandForm button[type="button"]').length) {
        $('#brandForm .col-12.text-center').html(`
          <button type="submit" class="btn btn-primary me-sm-3 me-1 waves-effect waves-light">Submit</button>
          <button type="button" class="btn btn-label-secondary waves-effect" data-bs-dismiss="modal">Cancel</button>
        `);
      } else {
        // If only one is missing, ensure both are present and styled side by side
        if (!$('#brandForm button[type="submit"]').length) {
          $('#brandForm .col-12.text-center').prepend(
            '<button type="submit" class="btn btn-primary me-sm-3 me-1 waves-effect waves-light">Submit</button>'
          );
        }
        if (!$('#brandForm button[type="button"]').length) {
          $('#brandForm .col-12.text-center').append(
            '<button type="button" class="btn btn-label-secondary waves-effect" data-bs-dismiss="modal">Cancel</button>'
          );
        }
      }

      // Show the modal
      brandModalInstance.show();
    });

    // Delete Record
    $('.brand-datatables-basic tbody').on('click', '.delete-record', function () {
      var tr = $(this).closest('tr');
      var row = dt_basic.row(tr);
      var data = row.data();

      // Perform the delete action here
      if (confirm('Are you sure you want to delete this record?')) {
        // Send a request to the server to delete the record
        fetch('/delete-brand/' + data.id, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              alert(data.message);
              row.remove().draw();
            } else {
              alert('Error deleting record: ' + data.message);
            }
          });
      }
    });

    // After initializing the DataTable
    $('.brand-datatables-basic').closest('.card').find('.head-label.text-center').html('<h5 class="card-title mb-0">Brand Catalog</h5>');
    // Filter form control to default size
    setTimeout(() => {
      $('.dataTables_filter .form-control').removeClass('form-control-sm');
      $('.dataTables_length .form-select').removeClass('form-select-sm');
    }, 300);
  });
}

if (document.getElementById('brandForm')) {
  document.getElementById('brandForm').addEventListener('submit', function (e) {
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
}