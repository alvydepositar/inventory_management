/**
 * DataTables Basic
 */

'use strict';
// Redirect to login if any jQuery AJAX call hits 401 (unauthenticated)
if (window.jQuery) {
  $(document).ajaxError(function (event, jqxhr) {
    if (jqxhr && jqxhr.status === 401) {
      window.location.href = '/';
    }
  });
}
let usersModalInstance, productModalInstance, categoryModalInstance, brandModalInstance, supplierModalInstance, branchModalInstance, stockModalInstance, stockConversionModalInstance;

// Users DataTable and Modal
if (document.getElementById('userModal')) {
  document.getElementById('userModal').addEventListener('hidden.bs.modal', function () {
    // Reset the form when the modal is closed
    document.getElementById('userForm').reset();
    // Reset action to default Add endpoint to avoid editing previous record
    document.getElementById('userForm').setAttribute('action', '/add-user/');
    document.querySelectorAll('#userForm input').forEach(input => {
      input.classList.remove('is-invalid');
      const errorContainer = input.nextElementSibling;
      if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
        errorContainer.innerHTML = '';
      }
    });
    const roleSelect = document.querySelector('#userForm select[name="user_role"]');
    const branchSelect = document.querySelector('#userForm select[name="assigned_branch"]');
    const activeCheckbox = document.querySelector('#userForm input[name="is_active"]');
    if (roleSelect) roleSelect.value = '';
    if (branchSelect) branchSelect.value = '';
    if (activeCheckbox) {
      activeCheckbox.checked = true;
      activeCheckbox.disabled = false;
    }
  });
  $(function () {
    usersModalInstance = new bootstrap.Modal(document.getElementById('userModal'));
    var dt_basic_table = $('.users-datatables-basic'),
      dt_basic;
    // DataTable with buttons
    // --------------------------------------------------------------------
    if (dt_basic_table.length) {
      dt_basic = dt_basic_table.DataTable({
        ajax: '/users-data/', // Fetch data from the Django endpoint
        columns: [
          { data: null, defaultContent: '' }, // Control column
          { data: null, defaultContent: '' }, // Control column
          { data: 'id' }, // Checkbox column
          { data: 'username' },
          { data: 'email' },
          { 
            data: null, 
            defaultContent: '', 
            render: function(data, type, row, meta) {
              return (row.first_name ? row.first_name : '') + ' ' + (row.last_name ? row.last_name : '');
            }
          },
          { data: 'user_role', render: function (data, type, full, meta) { return String(data || '').charAt(0).toUpperCase() + String(data || '').slice(1).replace('_', ' '); } },
          { data: 'assigned_branch__name', defaultContent: '', render: function (data) { return data || '-'; } },
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
                '<li><a href="javascript:;" class="dropdown-item item-view" data-bs-toggle="modal" data-bs-target="#userModal" data-id="' + full.id + '">Details</a></li>' +
                '<div class="dropdown-divider"></div>' +
                '<li><a href="javascript:;" class="dropdown-item text-danger delete-record">Delete</a></li>' +
                '</ul>' +
                '</div>' +
                '<a href="javascript:;" class="btn btn-sm btn-icon item-edit" data-bs-toggle="modal" data-bs-target="#userModal" data-id="' + full.id + '"><i class="text-primary ti ti-pencil"></i></a>'
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
                extend: 'csv',
                text: '<i class="ti ti-file-text me-sm-1"></i> <span class="d-none d-sm-inline-block">CSV</span>',
                className: 'dropdown-item',
                exportOptions: {
                  columns: [2, 3, 4, 5, 6, 7]
                }
              },
              {
                extend: 'excel',
                text: '<i class="ti ti-file-spreadsheet me-sm-1"></i> <span class="d-none d-sm-inline-block">Excel</span>',
                className: 'dropdown-item',
                exportOptions: {
                  columns: [2, 3, 4, 5, 6, 7]
                }
              },
              {
                extend: 'pdf',
                text: '<i class="ti ti-file-description me-sm-1"></i> <span class="d-none d-sm-inline-block">PDF</span>',
                className: 'dropdown-item',
                exportOptions: {
                  columns: [2, 3, 4, 5, 6, 7]
                }
              },
              {
                extend: 'copy',
                text: '<i class="ti ti-copy me-sm-1"></i> <span class="d-none d-sm-inline-block">Copy</span>',
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
              'data-bs-target': '#userModal'
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
                return 'Details for ' + data[2]; // Customize the header content
              }
            })
          }
        }
      });
    }

    // Ensure Add New Record always targets the add endpoint
    $(document).on('click', '.create-new[data-bs-target="#userModal"]', function () {
      resetModalInputs('userModal');
      $('#userModalLabel').text('Add New User');
      $('#userForm').attr('action', '/add-user/');
      $('#userForm input[name="is_active"]').prop('checked', true).prop('disabled', false);
      syncUserAssignedBranchField();
    });

    // Handle view button click
    $('.users-datatables-basic tbody').on('click', '.item-view', function () {
      resetModalInputs('userModal');
      var tr = $(this).closest('tr');
      var row = dt_basic.row(tr);
      var data = row.data();
      // Fill modal fields
      $('#userModalLabel').text('View User');
      $('#userForm').attr('action', '/view-user/' + data.id + '/');
      $('#userForm input[name="username"]').val(data.username).prop('readonly', true);
      $('#userForm input[name="email"]').val(data.email).prop('readonly', true);
      $('#userForm input[name="first_name"]').val(data.first_name).prop('readonly', true);
      $('#userForm input[name="last_name"]').val(data.last_name).prop('readonly', true);
      $('#userForm select[name="user_role"]').val(String(data.user_role)).prop('disabled', true);
      $('#userForm select[name="assigned_branch"]').val(data.assigned_branch_id ? String(data.assigned_branch_id) : '').prop('disabled', true);
      $('#userForm input[name="is_active"]').prop('checked', !!data.is_active).prop('disabled', true);
      // Remove submit button
      $('#userForm button[type="submit"]').remove();
      usersModalInstance.show();
    });

    // Handle edit button click
    $('.users-datatables-basic tbody').on('click', '.item-edit', function () {
      resetModalInputs('userModal'); // This resets the form
      var tr = $(this).closest('tr');
      if (tr.hasClass('child')) tr = tr.prev();
      var row = dt_basic.row(tr);
      var data = row.data();
      // Fill modal fields
      $('#userModalLabel').text('Edit User');
      $('#userForm').attr('action', '/edit-user/' + data.id + '/');
      $('#userForm input[name="username"]').val(data.username);
      $('#userForm input[name="email"]').val(data.email);
      $('#userForm input[name="first_name"]').val(data.first_name);
      $('#userForm input[name="last_name"]').val(data.last_name);
      $('#userForm select[name="user_role"]').val(String(data.user_role)).prop('disabled', false);
      $('#userForm select[name="assigned_branch"]').val(data.assigned_branch_id ? String(data.assigned_branch_id) : '').prop('disabled', false);
      $('#userForm input[name="is_active"]').prop('checked', !!data.is_active).prop('disabled', false);
      $('#userForm input[name="password"]').val(''); // Clear password field
      syncUserAssignedBranchField();
      // Bring the submit button back and cancel button side by side
      if (!$('#userForm button[type="submit"]').length && !$('#userForm button[type="button"]').length) {
        $('#userForm .col-12.text-center').html(`
          <button type="submit" class="btn btn-primary me-sm-3 me-1 waves-effect waves-light">Submit</button>
          <button type="button" class="btn btn-secondary waves-effect waves-light" data-bs-dismiss="modal">Cancel</button>
        `);
      }
    });

    // Delete Record
    $('.users-datatables-basic tbody').on('click', '.delete-record', function () {
      var tr = $(this).closest('tr');
      if (tr.hasClass('child')) tr = tr.prev();
      var row = dt_basic.row(tr);
      var data = row.data();
      if (!data || !data.id) return;

      if (confirm('Are you sure you want to delete this user?')) {
        fetch('/delete-user/' + data.id + '/', {
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
              alert('Error deleting user: ' + (data.message || 'Unknown error.'));
            }
          });
      }
    });
  });
}

function syncUserAssignedBranchField() {
  const roleField = document.querySelector('#userForm select[name="user_role"]');
  const branchField = document.querySelector('#userForm select[name="assigned_branch"]');
  if (!roleField || !branchField) return;

  const roleValue = roleField.value;
  const needsBranch = roleValue === 'user' || roleValue === 'branch_manager';
  if (!needsBranch) {
    branchField.value = '';
  }
  branchField.required = needsBranch;
  branchField.disabled = !needsBranch && !roleField.disabled;
}

$(document).on('change', '#userForm select[name="user_role"]', syncUserAssignedBranchField);

if (document.getElementById('userForm')) {
  document.getElementById('userForm').addEventListener('submit', function (e) {
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
      .then(async response => {
        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
          const text = await response.text();
          throw new Error('Unexpected server response (' + response.status + '): ' + text.slice(0, 120));
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          alert(data.message);
          location.reload(); // Reload the page or update the table dynamically
        } else {
          // Display validation errors
          if (data.errors) {
            for (const [field, errors] of Object.entries(data.errors)) {
              const input = document.querySelector(`[name=${field}]`);
              if (input) {
                const errorContainer = input.nextElementSibling;
                if (errorContainer) {
                  errorContainer.innerHTML = (Array.isArray(errors) ? errors : [errors]).join('<br>');
                }
                input.classList.add('is-invalid');
              }
            }
          } else if (data.message) {
            alert(data.message);
          }
        }
      })
      .catch(error => console.error('Error:', error));
  });
}

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
        { data: 'category__name' },
        { data: 'brand__name' },
        { data: 'unit_price' },
        { data: 'low_stock_limit' },
        { data: 'supplier__name' },
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
                columns: [2, 3, 4, 5, 6, 7, 8]
              }
            },
            {
              extend: 'csv',
              text: '<i class="ti ti-file-text me-1" ></i>CSV',
              className: 'dropdown-item',
              exportOptions: {
                columns: [2, 3, 4, 5, 6, 7, 8]
              }
            },
            {
              extend: 'excel',
              text: '<i class="ti ti-file-spreadsheet me-1"></i>Excel',
              className: 'dropdown-item',
              exportOptions: {
                columns: [2, 3, 4, 5, 6, 7, 8]
              }
            },
            {
              extend: 'pdf',
              text: '<i class="ti ti-file-description me-1"></i>PDF',
              className: 'dropdown-item',
              exportOptions: {
                columns: [2, 3, 4, 5, 6, 7, 8]
              }
            },
            {
              extend: 'copy',
              text: '<i class="ti ti-copy me-1" ></i>Copy',
              className: 'dropdown-item',
              exportOptions: {
                columns: [2, 3, 4, 5, 6, 7, 8]
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
    resetModalInputs('productModal');
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    // Fill modal fields
    $('#productModalLabel').text('View Product');
    $('#productForm').attr('action', '/view-product/' + data.id + '/');
    $('#productForm input[name="product_id"]').val(data.product_id).prop('readonly', true);
    $('#productForm input[name="product_name"]').val(data.product_name).prop('readonly', true);
    $('#productForm select[name="category"]').val(String(data.category__id)).prop('disabled', true); 
    $('#productForm select[name="brand"]').val(String(data.brand__id)).prop('disabled', true);
    $('#productForm input[name="unit_price"]').val(data.unit_price).prop('readonly', true);
    $('#productForm input[name="low_stock_limit"]').val(data.low_stock_limit).prop('readonly', true);
    $('#productForm select[name="supplier"]').val(String(data.supplier__id)).prop('disabled', true);

    // Remove submit button
    $('#productForm button[type="submit"]').remove();
    
    productModalInstance.show();
  });

  // Handle edit button click
  $('.product-datatables-basic tbody').on('click', '.item-edit', function () {
    resetModalInputs('productModal'); // This resets the form
  
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();
  
    // Fill modal fields
    $('#productModalLabel').text('Edit Product');
    $('#productForm').attr('action', '/edit-product/' + data.id + '/');
    $('#productForm input[name="product_id"]').val(data.product_id).prop('readonly', true);
    $('#productForm input[name="product_name"]').val(data.product_name);
    $('#productForm select[name="category"]').val(String(data.category__id)); 
    $('#productForm select[name="brand"]').val(String(data.brand__id));
    $('#productForm input[name="unit_price"]').val(data.unit_price);
    $('#productForm input[name="low_stock_limit"]').val(data.low_stock_limit);
    $('#productForm select[name="supplier"]').val(String(data.supplier__id));

    console.log(data);

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
      resetModalInputs('categoryModal');
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
      resetModalInputs('categoryModal');
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
      resetModalInputs('brandModal');
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
      resetModalInputs('brandModal'); // This resets the form
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

// Supplier DataTable and Modal
if (document.getElementById('supplierModal')) {
  document.getElementById('supplierModal').addEventListener('hidden.bs.modal', function () {
    // Reset the form when the modal is closed
    document.getElementById('supplierForm').reset();
    document.querySelectorAll('#supplierForm input').forEach(input => {
      input.classList.remove('is-invalid');
      const errorContainer = input.nextElementSibling;
      if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
        errorContainer.innerHTML = '';
      }
    });
  });

  $(function () {
  supplierModalInstance = new bootstrap.Modal(document.getElementById('supplierModal'));
  var dt_basic_table = $('.supplier-datatables-basic'),
    dt_basic;

  // DataTable with buttons
  // --------------------------------------------------------------------

  if (dt_basic_table.length) {
    dt_basic = dt_basic_table.DataTable({
      ajax: '/supplier-data/', // Fetch data from the Django endpoint
      columns: [
        { data: null, defaultContent: '' }, // Control column
        { data: 'id' }, // Checkbox column
        { data: 'id' },
        { data: 'name' },
        { data: 'contact_person' },
        { data: 'contact_number' },
        { data: 'email' },
        { data: 'address' },
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
              '<li><a href="javascript:;" class="dropdown-item item-view" data-bs-toggle="modal" data-bs-target="#supplierModal" data-id="' + full.id + '">Details</a></li>' +
              '<div class="dropdown-divider"></div>' +
              '<li><a href="javascript:;" class="dropdown-item text-danger delete-record">Delete</a></li>' +
              '</ul>' +
              '</div>' +
              '<a href="javascript:;" class="btn btn-sm btn-icon item-edit" data-bs-toggle="modal" data-bs-target="#supplierModal" data-id="' + full.id + '"><i class="text-primary ti ti-pencil"></i></a>'
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
          text: '<i class="ti ti-plus me-sm-1"></i> <span class="d-none d-sm-inline-block">Add New Record</span>',
          className: 'create-new btn btn-primary',
          attr: {
            'data-bs-toggle': 'modal',
            'data-bs-target': '#supplierModal'
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
              return 'Details of ' + data['supplier_name'] + ' (' + data['supplier_id'] + ')';
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
  $('.supplier-datatables-basic tbody').on('click', '.item-view', function () {
    resetModalInputs('supplierModal');
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    // Fill modal fields
    $('#supplierModalLabel').text('View Supplier');
    $('#supplierForm').attr('action', '/view-supplier/' + data.id + '/');
    $('#supplierForm input[name="supplier_id"]').val(data.id).prop('readonly', true);
    $('#supplierForm input[name="supplier_name"]').val(data.name).prop('readonly', true);
    $('#supplierForm input[name="contact_person"]').val(data.contact_person).prop('readonly', true);
    $('#supplierForm input[name="contact_number"]').val(data.contact_number).prop('readonly', true);
    $('#supplierForm input[name="email"]').val(data.email).prop('readonly', true);
    $('#supplierForm textarea[name="address"]').val(data.address).prop('readonly', true);

    // Remove submit button
    $('#supplierForm button[type="submit"]').remove();

    supplierModalInstance.show();
  });

  // Handle edit button click
  $('.supplier-datatables-basic tbody').on('click', '.item-edit', function () {
    resetModalInputs('supplierModal'); // This resets the form
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    // Fill modal fields
    $('#supplierModalLabel').text('Edit Supplier');
    $('#supplierForm').attr('action', '/edit-supplier/' + data.id + '/');
    $('#supplierForm input[name="supplier_id"]').val(data.id).prop('readonly', true);
    $('#supplierForm input[name="name"]').val(data.name);
    $('#supplierForm input[name="contact_person"]').val(data.contact_person);
    $('#supplierForm input[name="contact_number"]').val(data.contact_number);
    $('#supplierForm input[name="email"]').val(data.email);
    $('#supplierForm textarea[name="address"]').val(data.address);

    // Show the modal
    supplierModalInstance.show();
  });

  // Delete Record
  $('.supplier-datatables-basic tbody').on('click', '.delete-record', function () {
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    // Perform the delete action here
    if (confirm('Are you sure you want to delete this record?')) {
      // Send a request to the server to delete the record
      fetch('/delete-supplier/' + data.id, {
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
  $('.head-label.text-center').html('<h5 class="card-title mb-0">Supplier Catalog</h5>');

  // Filter form control to default size
  setTimeout(() => {
    $('.dataTables_filter .form-control').removeClass('form-control-sm');
    $('.dataTables_length .form-select').removeClass('form-select-sm');
  }, 300);
});
}

if (document.getElementById('supplierForm')) {
  document.getElementById('supplierForm').addEventListener('submit', function (e) {
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

// Branch DataTable and Modal
if (document.getElementById('branchModal')) {
  document.getElementById('branchModal').addEventListener('hidden.bs.modal', function () {
    // Reset the form when the modal is closed
    document.getElementById('branchForm').reset();
    document.querySelectorAll('#branchForm input').forEach(input => {
      input.classList.remove('is-invalid');
      const errorContainer = input.nextElementSibling;
      if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
        errorContainer.innerHTML = '';
      }
    });
  });

  $(function () {
  branchModalInstance = new bootstrap.Modal(document.getElementById('branchModal'));
  var dt_basic_table = $('.branch-datatables-basic'),
    dt_basic;

  // DataTable with buttons
  // --------------------------------------------------------------------

  if (dt_basic_table.length) {
    dt_basic = dt_basic_table.DataTable({
      ajax: '/branch-data/', // Fetch data from the Django endpoint
      columns: [
        { data: null, defaultContent: '' }, // Control column
        { data: 'id' }, // Checkbox column
        { data: 'id' },
        { data: 'name' },
        { data: 'location' },
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
              '<li><a href="javascript:;" class="dropdown-item item-view" data-bs-toggle="modal" data-bs-target="#branchModal" data-id="' + full.id + '">Details</a></li>' +
              '<div class="dropdown-divider"></div>' +
              '<li><a href="javascript:;" class="dropdown-item text-danger delete-record">Delete</a></li>' +
              '</ul>' +
              '</div>' +
              '<a href="javascript:;" class="btn btn-sm btn-icon item-edit" data-bs-toggle="modal" data-bs-target="#branchModal" data-id="' + full.id + '"><i class="text-primary ti ti-pencil"></i></a>' +
              '<a href="/manage-stocks/' + full.id + '/" class="btn btn-sm btn-icon item-manage-stocks"><i class="text-primary ti ti-package"></i></a>'
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
          text: '<i class="ti ti-plus me-sm-1"></i> <span class="d-none d-sm-inline-block">Add New Record</span>',
          className: 'create-new btn btn-primary',
          attr: {
            'data-bs-toggle': 'modal',
            'data-bs-target': '#branchModal'
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
              return 'Details of ' + data['branch_name'] + ' (' + data['branch_id'] + ')';
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
  $('.branch-datatables-basic tbody').on('click', '.item-view', function () {
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    // Fill modal fields
    $('#branchModalLabel').text('View Branch');
    $('#branchForm').attr('action', '/view-branch/' + data.id + '/');
    $('#branchForm input[name="branch_id"]').val(data.id).prop('readonly', true);
    $('#branchForm input[name="name"]').val(data.name).prop('readonly', true);
    $('#branchForm textarea[name="location"]').val(data.location).prop('readonly', true);

    // Remove submit button
    $('#branchForm button[type="submit"]').remove();
    // Remove cancel button if it exists
    $('#branchForm button[type="button"]').remove();

    branchModalInstance.show();
  });

  // Handle edit button click
  $('.branch-datatables-basic tbody').on('click', '.item-edit', function () {
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    // Fill modal fields
    $('#branchModalLabel').text('Edit Branch');
    $('#branchForm').attr('action', '/edit-branch/' + data.id + '/');
    $('#branchForm input[name="branch_id"]').val(data.id).prop('readonly', true);
    $('#branchForm input[name="name"]').val(data.name);
    $('#branchForm textarea[name="location"]').val(data.location);

    // Show the modal
    branchModalInstance.show();
  });

  // Delete Record
  $('.branch-datatables-basic tbody').on('click', '.delete-record', function () {
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    // Perform the delete action here
    if (confirm('Are you sure you want to delete this record?')) {
      // Send a request to the server to delete the record
      fetch('/delete-branch/' + data.id, {
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
  $('.head-label.text-center').html('<h5 class="card-title mb-0">Branch Catalog</h5>');

  // Filter form control to default size
  setTimeout(() => {
    $('.dataTables_filter .form-control').removeClass('form-control-sm');
    $('.dataTables_length .form-select').removeClass('form-select-sm');
  }, 300);
});
}

if (document.getElementById('branchForm')) {
  document.getElementById('branchForm').addEventListener('submit', function (e) {
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

let stockBalanceRequestSequence = 0;
let stockHistoryModalInstance = null;
let stockHistoryDt = null;

function getStockActionLabel(typeValue) {
  if (typeValue === 'OUT') return 'Release Stock';
  if (typeValue === 'BACKLOAD') return 'Transfer to Branch';
  return 'Receive Stock';
}

function renderMovementActionMarkup(quantity, row) {
  if (!row) return '';
  const relatedBranchName = row['related_branch__name'] || '';
  const conversionRef = row.conversion_id ? ' (Conversion #' + row.conversion_id + ')' : '';
  if (row['transaction_type'] === 'IN') {
    return '<span class="fw-semibold text-success">Received ' + quantity + '</span>';
  }
  if (row['transaction_type'] === 'BLI') {
    return '<span class="fw-semibold text-success">Transferred In ' + quantity + (relatedBranchName ? ' from ' + relatedBranchName : '') + '</span>';
  }
  if (row['transaction_type'] === 'BLO') {
    return '<span class="fw-semibold text-danger">Transferred Out ' + quantity + (relatedBranchName ? ' to ' + relatedBranchName : '') + '</span>';
  }
  if (row['transaction_type'] === 'MIX_OUT') {
    return '<span class="fw-semibold text-danger">Used for Mixing ' + quantity + conversionRef + '</span>';
  }
  if (row['transaction_type'] === 'MIX_IN') {
    return '<span class="fw-semibold text-success">Produced from Mixing ' + quantity + conversionRef + '</span>';
  }
  return '<span class="fw-semibold text-danger">Released ' + quantity + '</span>';
}

function resolveTableRow(dataTableApi, triggerElement) {
  var tr = $(triggerElement).closest('tr');
  if (tr.hasClass('child')) {
    tr = tr.prev();
  }
  return dataTableApi.row(tr);
}

function clearStockFieldError(field) {
  if (!field) return;
  field.classList.remove('is-invalid');
  const errorContainer = field.nextElementSibling;
  if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
    errorContainer.innerHTML = '';
  }
}

function setStockFieldError(field, messages) {
  if (!field) return;
  const items = Array.isArray(messages) ? messages : [messages];
  field.classList.add('is-invalid');
  const errorContainer = field.nextElementSibling;
  if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
    errorContainer.innerHTML = items.join('<br>');
  }
}

function clearStockFormValidation() {
  const form = document.getElementById('stockForm');
  if (!form) return;

  form.querySelectorAll('input, select, textarea').forEach(clearStockFieldError);
}

function getStockBalanceCopy(typeValue) {
  if (typeValue === 'OUT') {
    return {
      label: 'Current Balance Before Release',
      hint: 'This is the quantity currently available in the selected branch.'
    };
  }
  if (typeValue === 'BACKLOAD') {
    return {
      label: 'Current Balance in Source Branch',
      hint: 'This is the quantity available to transfer from the selected branch.'
    };
  }
  return {
    label: 'Current Balance',
    hint: 'This is the quantity currently on hand before you receive more stock.'
  };
}

function updateStockBalancePanel(balanceValue, hintOverride) {
  const wrapper = document.getElementById('stockCurrentBalanceWrapper');
  const labelEl = document.getElementById('stockCurrentBalanceLabel');
  const valueEl = document.getElementById('stockCurrentBalanceValue');
  const hintEl = document.getElementById('stockCurrentBalanceHint');
  const typeField = document.getElementById('stockType');

  if (!wrapper || !labelEl || !valueEl || !hintEl || !typeField) return;

  const copy = getStockBalanceCopy(typeField.value);
  labelEl.textContent = copy.label;
  valueEl.textContent = balanceValue;
  hintEl.textContent = hintOverride || copy.hint;
}

async function refreshStockBalance() {
  const branchField = document.getElementById('stockBranch');
  const productField = document.getElementById('stockProduct');
  const wrapper = document.getElementById('stockCurrentBalanceWrapper');

  if (!branchField || !productField || !wrapper) return null;

  const branchId = branchField.value;
  const productId = productField.value;
  if (!branchId || !productId) {
    wrapper.dataset.currentBalance = '';
    wrapper.classList.add('d-none');
    updateStockBalancePanel('-', 'Select a branch and product to view the current balance.');
    return null;
  }

  wrapper.classList.remove('d-none');
  updateStockBalancePanel('...', 'Checking current balance for the selected branch and product.');

  const requestId = ++stockBalanceRequestSequence;
  try {
    const response = await fetch(
      '/stock-data/?branch_id=' + encodeURIComponent(branchId) + '&product_id=' + encodeURIComponent(productId)
    );
    if (!response.ok) {
      throw new Error('Unable to load current balance.');
    }

    const payload = await response.json();
    if (requestId !== stockBalanceRequestSequence) {
      return wrapper.dataset.currentBalance === '' ? null : Number(wrapper.dataset.currentBalance);
    }

    const firstRow = Array.isArray(payload.data) && payload.data.length ? payload.data[0] : null;
    const balance = firstRow && firstRow.quantity != null ? Number(firstRow.quantity) : 0;
    wrapper.dataset.currentBalance = String(balance);
    updateStockBalancePanel(String(balance));
    return balance;
  } catch (error) {
    if (requestId !== stockBalanceRequestSequence) {
      return wrapper.dataset.currentBalance === '' ? null : Number(wrapper.dataset.currentBalance);
    }

    wrapper.dataset.currentBalance = '';
    updateStockBalancePanel('-', 'Current balance could not be loaded right now.');
    return null;
  }
}

function syncStockTransactionFields() {
  const typeField = document.getElementById('stockType');
  const relatedWrapper = document.getElementById('stockRelatedBranchWrapper');
  const relatedBranch = document.getElementById('stockRelatedBranch');
  const branchLabel = document.querySelector('label[for="stockBranch"]');
  const relatedLabel = document.querySelector('label[for="stockRelatedBranch"]');
  const actionGuide = document.getElementById('stockActionGuide');
  const submitButton = document.getElementById('stockSubmitButton');

  if (!typeField || !relatedWrapper || !relatedBranch) return;

  const typeValue = typeField.value;
  const isTransfer = typeValue === 'BACKLOAD';

  relatedWrapper.classList.toggle('d-none', !isTransfer);
  relatedBranch.required = isTransfer;
  if (!isTransfer) {
    relatedBranch.value = '';
    clearStockFieldError(relatedBranch);
  }

  if (branchLabel) {
    branchLabel.textContent = isTransfer ? 'From Branch' : 'Branch';
  }
  if (relatedLabel) {
    relatedLabel.textContent = 'To Branch';
  }
  if (actionGuide) {
    if (typeValue === 'OUT') {
      actionGuide.textContent = 'Use this when stock leaves a branch. The current balance is shown before you submit.';
    } else if (isTransfer) {
      actionGuide.textContent = 'Moves stock from one branch to another. This is not counted as sales.';
    } else {
      actionGuide.textContent = 'Use this when new stock arrives in a branch.';
    }
  }
  if (submitButton) {
    submitButton.textContent = isTransfer ? 'Transfer Stock' : getStockActionLabel(typeValue);
  }

  void refreshStockBalance();
}

function buildStockHistoryModalUrl() {
  const modalEl = document.getElementById('stockHistoryModal');
  if (!modalEl) return '/movement-data/';

  const params = new URLSearchParams();
  const branchId = modalEl.dataset.branchId || '';
  const productId = modalEl.dataset.productId || '';
  const typeValue = modalEl.dataset.typeValue || '';
  const dateFrom = modalEl.dataset.dateFrom || '';
  const dateTo = modalEl.dataset.dateTo || '';
  const groupId = modalEl.dataset.groupId || '';
  if (branchId) params.set('branch_id', branchId);
  if (productId) params.set('product_id', productId);
  if (typeValue) params.set('type', typeValue);
  if (dateFrom) params.set('date_from', dateFrom);
  if (dateTo) params.set('date_to', dateTo);
  if (groupId) params.set('group_id', groupId);

  return '/movement-data/' + (params.toString() ? '?' + params.toString() : '');
}

function ensureStockHistoryModalTable() {
  if (stockHistoryDt || !$('#stockHistoryModalTable').length) return;

  stockHistoryDt = $('#stockHistoryModalTable').DataTable({
    ajax: { url: buildStockHistoryModalUrl() },
    columns: [
      { data: 'date' },
      { data: 'transaction_id' },
      { data: 'balance_before', defaultContent: 0 },
      { data: 'quantity' },
      { data: 'balance_after', defaultContent: 0 },
      { data: 'handled_by__username', defaultContent: '' },
      { data: 'remarks', defaultContent: '' }
    ],
    columnDefs: [
      {
        targets: 0,
        render: function (d, type) {
          return formatDisplayDateTime(d, type);
        }
      },
      {
        targets: 2,
        render: function (d) {
          return '<span class="fw-semibold">' + (d ?? 0) + '</span>';
        }
      },
      {
        targets: 3,
        render: function (d, type, row) {
          return renderMovementActionMarkup(d, row);
        }
      },
      {
        targets: 4,
        render: function (d) {
          return '<span class="fw-semibold">' + (d ?? 0) + '</span>';
        }
      }
    ],
    order: [[0, 'desc']],
    pageLength: 10,
    lengthMenu: [10, 25, 50],
    dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-md-end"f>>t<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>'
  });
}

function openStockHistoryModal(options) {
  const modalEl = document.getElementById('stockHistoryModal');
  if (!modalEl) return;

  modalEl.dataset.branchId = options.branchId ? String(options.branchId) : '';
  modalEl.dataset.productId = options.productId ? String(options.productId) : '';
  modalEl.dataset.typeValue = options.typeValue ? String(options.typeValue) : '';
  modalEl.dataset.dateFrom = options.dateFrom ? String(options.dateFrom) : '';
  modalEl.dataset.dateTo = options.dateTo ? String(options.dateTo) : '';
  modalEl.dataset.groupId = options.groupId ? String(options.groupId) : '';

  const branchName = options.branchName || 'All Branches';
  const productName = options.productName || 'Selected Product';
  const subtitle = document.getElementById('stockHistoryModalSubtitle');
  const openTabLink = document.getElementById('stockHistoryModalOpenTab');

  if (subtitle) {
    subtitle.textContent = options.subtitle || (productName + ' in ' + branchName);
  }
  if (openTabLink) {
    const params = new URLSearchParams();
    if (options.branchId) params.set('branch_id', options.branchId);
    if (options.productId) params.set('product_id', options.productId);
    if (options.typeValue) params.set('type', options.typeValue);
    if (options.dateFrom) params.set('date_from', options.dateFrom);
    if (options.dateTo) params.set('date_to', options.dateTo);
    if (options.groupId) params.set('group_id', options.groupId);
    openTabLink.href = '/stock-history/' + (params.toString() ? '?' + params.toString() : '');
  }

  if (!stockHistoryModalInstance) {
    stockHistoryModalInstance = new bootstrap.Modal(modalEl);
  }

  ensureStockHistoryModalTable();
  if (stockHistoryDt) {
    stockHistoryDt.ajax.url(buildStockHistoryModalUrl()).load();
  }

  stockHistoryModalInstance.show();
  setTimeout(function () {
    if (stockHistoryDt) {
      stockHistoryDt.columns.adjust();
    }
  }, 150);
}

// Stock DataTable and Modal
if (document.getElementById('stockModal')) {
  document.getElementById('stockModal').addEventListener('hidden.bs.modal', function () {
    const stockForm = document.getElementById('stockForm');
    if (!stockForm) return;
    stockForm.reset();
    clearStockFormValidation();
    syncStockTransactionFields();
  });

  $(function () {
  stockModalInstance = new bootstrap.Modal(document.getElementById('stockModal'));
  syncStockTransactionFields();
  var dt_basic_table = $('.stock-datatables-basic'),
    dt_basic;

  // DataTable with buttons
  // --------------------------------------------------------------------

  if (dt_basic_table.length) {
    function buildStockUrl() {
      const branchId = window.currentBranchId ? String(window.currentBranchId) : '';
      const productId = $('#levelProduct').val() || '';
      let url = '/stock-data/' + (branchId ? branchId + '/' : '');
      if (productId) {
        url += (url.includes('?') ? '&' : '?') + 'product_id=' + encodeURIComponent(productId);
      }
      return url;
    }

    dt_basic = dt_basic_table.DataTable({
      ajax: { url: buildStockUrl() },
      columns: [
        { data: null, defaultContent: '' }, // Control column
        { data: 'id' }, // Checkbox column
        { data: 'id' },
        { data: 'product__product_name' },
        { data: 'product__brand__name' },
        { data: 'quantity' },
        { data: 'stock_level' },
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
        // Add custom render for Stock Level column
        {
          targets: 6, // Stock Level column index
          render: function (data, type, full, meta) {
            let value = data.toLowerCase();
            let colorClass = '';
            if (value === 'low') {
              colorClass = 'bg-danger text-white';
            } else if (value === 'medium') {
              colorClass = 'bg-warning text-dark';
            } else if (value === 'high') {
              colorClass = 'bg-success text-white';
            } else {
              colorClass = 'bg-secondary text-white';
            }
            return '<span class="badge ' + colorClass + '" style="font-size:1em;">' + data + '</span>';
          }
        },
          {
            targets: -1,
            title: 'Actions',
            orderable: false,
            searchable: false,
            render: function (data, type, full, meta) {
              return (
                '<div class="d-flex flex-wrap gap-1">' +
                  '<a href="javascript:;" class="btn btn-sm btn-primary item-adjust" data-bs-toggle="modal" data-bs-target="#stockModal" data-id="' + full.id + '"><i class="ti ti-adjustments"></i> Record Action</a>' +
                  '<button type="button" class="btn btn-sm btn-outline-primary item-view-log" data-id="' + full.id + '"><i class="ti ti-history me-1"></i>View Log</button>' +
                  '<button type="button" class="btn btn-sm btn-outline-danger delete-stock" data-id="' + full.id + '"><i class="ti ti-trash me-1"></i>Delete</button>' +
                '</div>'
              );
            }
          }
      ],
      order: [[2, 'desc']],
      dom: '<"card-header flex-column flex-md-row"<"head-label text-center"><"dt-action-buttons text-end pt-3 pt-md-0"B>><"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>>t<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
      displayLength: 10,
      lengthMenu: [7, 10, 25, 50, 75, 100],
      buttons: [
        {
          extend: 'collection',
          className: 'btn btn-label-primary dropdown-toggle me-2',
          text: '<i class="ti ti-file-export me-sm-1"></i>Download',
          buttons: [
            { extend: 'csv', className: 'dropdown-item', exportOptions: { columns: [2, 3, 4, 5, 6] } },
            { extend: 'excel', className: 'dropdown-item', exportOptions: { columns: [2, 3, 4, 5, 6] } },
            { extend: 'pdf', className: 'dropdown-item', exportOptions: { columns: [2, 3, 4, 5, 6] } },
            { extend: 'copy', className: 'dropdown-item', exportOptions: { columns: [2, 3, 4, 5, 6] } }
          ]
        },
        {
          text: '<i class="ti ti-plus me-sm-1"></i> <span class="d-none d-sm-inline-block">Record Stock Action</span>',
          className: 'create-new btn btn-primary',
          attr: {
            'data-bs-toggle': 'modal',
            'data-bs-target': '#stockModal'
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
              return 'Details of ' + data['stock_name'] + ' (' + data['stock_id'] + ')';
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

    // Prefill modal selects from current filters when creating a new transaction
    $(document).on('click', '.create-new[data-bs-target="#stockModal"]', function(){
      $('#stockModalLabel').text('Record Stock Action');
      $('#stockForm').attr('action', '/add-stock/');
      var b = window.currentBranchId ? String(window.currentBranchId) : '';
      var p = $('#levelProduct').val();
      if (b) $('#stockBranch').val(String(b));
      if (p) $('#stockProduct').val(String(p));
      $('#stockType').val('IN');
      $('#stockRelatedBranch').val('');
      $('#stockProductQuantity').val('');
      $('#stockRemarks').val('');
      syncStockTransactionFields();
    });

    $(document).on('click', '.stock-quick-action', function () {
      resetModalInputs('stockModal');
      const actionType = $(this).data('stockAction') || 'IN';
      const currentBranch = window.currentBranchId ? String(window.currentBranchId) : '';
      const currentProduct = $('#levelProduct').val() || '';

      $('#stockModalLabel').text(getStockActionLabel(actionType));
      $('#stockForm').attr('action', '/add-stock/');
      $('#stockType').val(actionType);
      $('#stockBranch').val(currentBranch);
      $('#stockProduct').val(currentProduct);
      $('#stockRelatedBranch').val('');
      $('#stockProductQuantity').val('');
      $('#stockRemarks').val('');
      syncStockTransactionFields();

      stockModalInstance.show();
    });

    // Filters: reload on change
    $(document).on('change', '#levelProduct', function(){
      dt_basic.ajax.url(buildStockUrl()).load();
    });
    $(document).on('click', '#levelClearFilters', function(){
      $('#levelProduct').val('');
      dt_basic.ajax.url(buildStockUrl()).load();
    });
  }

  // Handle adjust button click for Stock Level rows (creates a movement)
  $('.stock-datatables-basic tbody').on('click', '.item-adjust', function () {
    resetModalInputs('stockModal');
    var row = resolveTableRow(dt_basic, this);
    var data = row.data();

    // Fill modal defaults for quick adjust
    $('#stockModalLabel').text('Record Stock Action');
    $('#stockForm').attr('action', '/add-stock/');
    $('#stockForm select[name="product"]').val(String(data.product__id));
    $('#stockForm select[name="branch"]').val(String(data.branch__id));
    $('#stockForm input[name="quantity"]').val('');
    $('#stockForm select[name="transaction_type"]').val('IN');
    $('#stockForm select[name="related_branch"]').val('');
    syncStockTransactionFields();

    stockModalInstance.show();
  });

  $('.stock-datatables-basic tbody').on('click', '.item-view-log', function () {
    var row = resolveTableRow(dt_basic, this);
    var data = row.data();
    if (!data) return;

    openStockHistoryModal({
      branchId: data.branch__id,
      branchName: data.branch__name,
      productId: data.product__id,
      productName: data.product__product_name
    });
  });

  // Delete stock level
  $('.stock-datatables-basic tbody').on('click', '.delete-stock', function () {
    var tr = $(this).closest('tr');
    var row = dt_basic.row(tr);
    var data = row.data();

    if (confirm('Are you sure you want to delete this stock record?')) {
      fetch('/delete-stock/' + data.id, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
      })
        .then(response => response.json())
        .then(result => {
          if (result.success) {
            alert(result.message);
            row.remove().draw();
          } else {
            alert('Error deleting record: ' + result.message);
          }
        })
        .catch(error => {
          alert('Error: ' + error.message);
        });
    }
  });

  // Deleting stock levels is not supported from the aggregate table; movements can be edited/deleted separately if needed.
  // Delete stock level (soft delete with balancing movement)
  $('.stock-datatables-basic tbody').on('click', '.item-delete', function () {
    var id = $(this).data('id');
    var qty = Number($(this).data('qty') || 0);
    var msg = 'Archive this stock level?';
    if (qty > 0) {
      msg += ' Remaining quantity (' + qty + ') will be moved out before archiving.';
    }
    if (!confirm(msg)) return;

    var csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
    var csrf = csrfEl ? csrfEl.value : '';

    fetch('/delete-stock-level/' + id + '/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrf,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    })
      .then(resp => resp.json())
      .then(data => {
        if (data.success) {
          alert(data.message || 'Stock level archived.');
          dt_basic.ajax.reload(null, false);
        } else {
          alert(data.message || 'Failed to archive stock level.');
        }
      })
      .catch(err => {
        console.error(err);
        alert('Failed to archive stock level.');
      });
  });

  // After initializing the DataTable
  dt_basic_table.closest('.card').find('.head-label.text-center').html('<h5 class="card-title mb-0">Current Stocks</h5>');

  // Filter form control to default size
  setTimeout(() => {
    $('.dataTables_filter .form-control').removeClass('form-control-sm');
    $('.dataTables_length .form-select').removeClass('form-select-sm');
  }, 300);
});
}

function resetStockConversionForm() {
  const form = document.getElementById('stockConversionForm');
  const rowsContainer = document.getElementById('conversionInputRows');
  if (!form || !rowsContainer) return;

  form.reset();
  const rows = Array.from(rowsContainer.querySelectorAll('.conversion-input-row'));
  rows.forEach((row, index) => {
    if (index === 0) {
      const productSelect = row.querySelector('.conversion-input-product');
      const qtyInput = row.querySelector('.conversion-input-quantity');
      const remainingInput = row.querySelector('.conversion-input-remaining');
      if (productSelect) productSelect.value = '';
      if (qtyInput) qtyInput.value = '';
      if (remainingInput) remainingInput.value = '';
      row.dataset.availableQty = '';
      return;
    }
    row.remove();
  });

  const currentBranch = window.currentBranchId ? String(window.currentBranchId) : '';
  const branchField = document.getElementById('conversionBranch');
  if (branchField && currentBranch) {
    branchField.value = currentBranch;
  }

  const createNewOutputProduct = document.getElementById('createNewOutputProduct');
  if (createNewOutputProduct) {
    createNewOutputProduct.checked = false;
  }

  const newOutputFields = [
    'newOutputProductId',
    'newOutputProductName',
    'newOutputUnitPrice',
    'newOutputLowStockLimit',
    'newOutputCategory',
    'newOutputBrand',
    'newOutputSupplier'
  ];
  newOutputFields.forEach(function (fieldId) {
    const field = document.getElementById(fieldId);
    if (field) field.value = '';
  });

  resetStockConversionBalanceCache();
  syncStockConversionOutputProductMode();
}

function addStockConversionInputRow() {
  const rowsContainer = document.getElementById('conversionInputRows');
  if (!rowsContainer) return;
  const firstRow = rowsContainer.querySelector('.conversion-input-row');
  if (!firstRow) return;

  const cloned = firstRow.cloneNode(true);
  const productSelect = cloned.querySelector('.conversion-input-product');
  const qtyInput = cloned.querySelector('.conversion-input-quantity');
  const remainingInput = cloned.querySelector('.conversion-input-remaining');
  if (productSelect) productSelect.value = '';
  if (qtyInput) qtyInput.value = '';
  if (remainingInput) remainingInput.value = '';
  cloned.dataset.availableQty = '';
  rowsContainer.appendChild(cloned);
}

let stockConversionBalanceCache = {};

function resetStockConversionBalanceCache() {
  stockConversionBalanceCache = {};
}

function updateConversionInputRemainingFromAvailable(row) {
  if (!row) return;

  const qtyField = row.querySelector('.conversion-input-quantity');
  const remainingField = row.querySelector('.conversion-input-remaining');
  const availableRaw = row.dataset.availableQty;
  if (!remainingField) return;

  if (availableRaw === undefined || availableRaw === null || availableRaw === '') {
    remainingField.value = '';
    return;
  }

  const available = Number(availableRaw);
  const used = Number(qtyField && qtyField.value ? qtyField.value : 0);
  const safeUsed = Number.isFinite(used) && used > 0 ? used : 0;
  remainingField.value = String(available - safeUsed);
}

async function fetchConversionInputAvailableQty(branchId, productId) {
  const key = String(branchId) + ':' + String(productId);
  if (Object.prototype.hasOwnProperty.call(stockConversionBalanceCache, key)) {
    return stockConversionBalanceCache[key];
  }

  const response = await fetch(
    '/stock-data/?branch_id=' + encodeURIComponent(branchId) + '&product_id=' + encodeURIComponent(productId)
  );
  if (!response.ok) {
    throw new Error('Unable to load stock balance.');
  }

  const payload = await response.json();
  const firstRow = Array.isArray(payload.data) && payload.data.length ? payload.data[0] : null;
  const available = firstRow && firstRow.quantity != null ? Number(firstRow.quantity) : 0;
  stockConversionBalanceCache[key] = available;
  return available;
}

async function refreshConversionInputRowRemaining(row) {
  if (!row) return;

  const branchField = document.getElementById('conversionBranch');
  const productField = row.querySelector('.conversion-input-product');
  const remainingField = row.querySelector('.conversion-input-remaining');
  if (!remainingField) return;

  const branchId = branchField && branchField.value ? String(branchField.value) : '';
  const productId = productField && productField.value ? String(productField.value) : '';
  if (!branchId || !productId) {
    row.dataset.availableQty = '';
    remainingField.value = '';
    return;
  }

  remainingField.value = '...';
  try {
    const available = await fetchConversionInputAvailableQty(branchId, productId);
    const currentBranchId = branchField && branchField.value ? String(branchField.value) : '';
    const currentProductId = productField && productField.value ? String(productField.value) : '';
    if (currentBranchId !== branchId || currentProductId !== productId) {
      return;
    }
    row.dataset.availableQty = String(available);
    updateConversionInputRemainingFromAvailable(row);
  } catch (error) {
    row.dataset.availableQty = '';
    remainingField.value = '';
  }
}

function refreshAllConversionInputRowsRemaining() {
  const rows = Array.from(document.querySelectorAll('#conversionInputRows .conversion-input-row'));
  rows.forEach(function (row) {
    void refreshConversionInputRowRemaining(row);
  });
}

function syncStockConversionOutputProductMode() {
  const createCheckbox = document.getElementById('createNewOutputProduct');
  const outputSelect = document.getElementById('conversionOutputProduct');
  const newFieldsWrapper = document.getElementById('newOutputProductFields');
  const createNew = !!(createCheckbox && createCheckbox.checked);

  if (outputSelect) {
    outputSelect.disabled = createNew;
    outputSelect.required = !createNew;
    if (createNew) {
      outputSelect.value = '';
    }
  }

  if (newFieldsWrapper) {
    newFieldsWrapper.classList.toggle('d-none', !createNew);
  }
}

if (document.getElementById('stockConversionModal')) {
  const modalEl = document.getElementById('stockConversionModal');
  stockConversionModalInstance = new bootstrap.Modal(modalEl);

  modalEl.addEventListener('hidden.bs.modal', function () {
    resetStockConversionForm();
  });

  $(document).on('click', '.stock-convert-quick-action', function () {
    resetStockConversionForm();
    stockConversionModalInstance.show();
  });

  $(document).on('click', '#addConversionInputRow', function () {
    addStockConversionInputRow();
  });
  $(document).on('change', '#createNewOutputProduct', function () {
    syncStockConversionOutputProductMode();
  });
  $(document).on('change', '#conversionBranch', function () {
    resetStockConversionBalanceCache();
    refreshAllConversionInputRowsRemaining();
  });
  $(document).on('change', '.conversion-input-product', function () {
    const row = this.closest('.conversion-input-row');
    if (!row) return;
    row.dataset.availableQty = '';
    void refreshConversionInputRowRemaining(row);
  });
  $(document).on('input', '.conversion-input-quantity', function () {
    const row = this.closest('.conversion-input-row');
    if (!row) return;
    if (row.dataset.availableQty === undefined || row.dataset.availableQty === null || row.dataset.availableQty === '') {
      void refreshConversionInputRowRemaining(row);
      return;
    }
    updateConversionInputRemainingFromAvailable(row);
  });

  $(document).on('click', '.remove-conversion-input-row', function () {
    const rowsContainer = document.getElementById('conversionInputRows');
    if (!rowsContainer) return;
    const rows = rowsContainer.querySelectorAll('.conversion-input-row');
    if (rows.length <= 1) {
      const row = rowsContainer.querySelector('.conversion-input-row');
      if (!row) return;
      const productSelect = row.querySelector('.conversion-input-product');
      const qtyInput = row.querySelector('.conversion-input-quantity');
      const remainingInput = row.querySelector('.conversion-input-remaining');
      if (productSelect) productSelect.value = '';
      if (qtyInput) qtyInput.value = '';
      if (remainingInput) remainingInput.value = '';
      row.dataset.availableQty = '';
      return;
    }
    const row = this.closest('.conversion-input-row');
    if (row) row.remove();
  });
}

if (document.getElementById('stockConversionForm')) {
  document.getElementById('stockConversionForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const branchField = document.getElementById('conversionBranch');
    const outputProductField = document.getElementById('conversionOutputProduct');
    const outputQuantityField = document.getElementById('conversionOutputQuantity');
    const createNewOutputProductField = document.getElementById('createNewOutputProduct');
    const remarksField = document.getElementById('conversionRemarks');
    const rows = Array.from(document.querySelectorAll('#conversionInputRows .conversion-input-row'));
    const createNewOutputProduct = !!(createNewOutputProductField && createNewOutputProductField.checked);

    if (!branchField || !branchField.value) {
      alert('Branch is required.');
      return;
    }
    if (!createNewOutputProduct) {
      if (!outputProductField || !outputProductField.value) {
        alert('Output product is required.');
        return;
      }
    } else {
      const newProductId = document.getElementById('newOutputProductId');
      const newProductName = document.getElementById('newOutputProductName');
      const newUnitPrice = document.getElementById('newOutputUnitPrice');
      const unitPriceValue = Number(newUnitPrice && newUnitPrice.value ? newUnitPrice.value : NaN);

      if (!newProductId || !newProductId.value.trim()) {
        alert('New output product code is required.');
        return;
      }
      if (!newProductName || !newProductName.value.trim()) {
        alert('New output product name is required.');
        return;
      }
      if (Number.isNaN(unitPriceValue) || unitPriceValue < 0) {
        alert('New output unit price must be zero or greater.');
        return;
      }
    }

    const outputQty = Number(outputQuantityField && outputQuantityField.value ? outputQuantityField.value : 0);
    if (outputQty <= 0) {
      alert('Produced quantity must be greater than zero.');
      return;
    }

    const inputRows = [];
    const seenProducts = new Set();
    for (const row of rows) {
      const productField = row.querySelector('.conversion-input-product');
      const quantityField = row.querySelector('.conversion-input-quantity');
      const productId = productField ? productField.value : '';
      const quantity = Number(quantityField && quantityField.value ? quantityField.value : 0);

      if (!productId && !quantity) {
        continue;
      }
      if (!productId || quantity <= 0) {
        alert('Each input row must include a product and a quantity greater than zero.');
        return;
      }
      if (seenProducts.has(productId)) {
        alert('Input products must not be duplicated.');
        return;
      }
      seenProducts.add(productId);
      inputRows.push({ productId, quantity });
    }

    if (!inputRows.length) {
      alert('At least one input product is required.');
      return;
    }

    const formData = new FormData();
    formData.append('branch', branchField.value);
    formData.append('output_quantity', String(outputQty));
    formData.append('remarks', remarksField ? remarksField.value : '');
    if (createNewOutputProduct) {
      formData.append('create_output_product', '1');
      formData.append('new_output_product_id', document.getElementById('newOutputProductId') ? document.getElementById('newOutputProductId').value.trim() : '');
      formData.append('new_output_product_name', document.getElementById('newOutputProductName') ? document.getElementById('newOutputProductName').value.trim() : '');
      formData.append('new_output_unit_price', document.getElementById('newOutputUnitPrice') ? document.getElementById('newOutputUnitPrice').value : '');
      formData.append('new_output_low_stock_limit', document.getElementById('newOutputLowStockLimit') ? document.getElementById('newOutputLowStockLimit').value : '');
      formData.append('new_output_category', document.getElementById('newOutputCategory') ? document.getElementById('newOutputCategory').value : '');
      formData.append('new_output_brand', document.getElementById('newOutputBrand') ? document.getElementById('newOutputBrand').value : '');
      formData.append('new_output_supplier', document.getElementById('newOutputSupplier') ? document.getElementById('newOutputSupplier').value : '');
    } else {
      formData.append('output_product', outputProductField.value);
    }
    for (const row of inputRows) {
      formData.append('input_product', row.productId);
      formData.append('quantity_used', String(row.quantity));
    }

    const csrfTokenElement = document.querySelector('#stockConversionForm [name=csrfmiddlewaretoken]');
    const csrfToken = csrfTokenElement ? csrfTokenElement.value : '';

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
          location.reload();
          return;
        }
        alert(data.message || 'Failed to create stock conversion.');
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to create stock conversion.');
      });
  });
}

// Low Stock Alerts DataTable
$(function () {
  var low_table = $('.low-stock-datatables-basic');
  if (!low_table.length) return;

  function buildLowStockUrl() {
    const params = new URLSearchParams();
    const branchId = window.currentBranchId ? String(window.currentBranchId) : '';
    const productId = $('#lowProduct').val() || '';

    params.set('low_only', '1');
    if (branchId) params.set('branch_id', branchId);
    if (productId) params.set('product_id', productId);

    return '/stock-data/?' + params.toString();
  }

  var low_dt = low_table.DataTable({
    ajax: { url: buildLowStockUrl() },
    columns: [
      { data: null, defaultContent: '' },
      { data: 'product__product_name' },
      { data: 'product__brand__name' },
      { data: 'quantity' },
      { data: 'product__low_stock_limit' },
      { data: 'short_by' },
      { data: 'stock_level' },
      { data: null, defaultContent: '' }
    ],
    columnDefs: [
      {
        className: 'control',
        orderable: false,
        searchable: false,
        responsivePriority: 1,
        targets: 0,
        render: function () {
          return '';
        }
      },
      {
        targets: 3,
        render: function (data) {
          return '<span class="fw-semibold text-danger">' + data + '</span>';
        }
      },
      {
        targets: 5,
        render: function (data) {
          return '<span class="badge bg-label-danger">' + data + '</span>';
        }
      },
      {
        targets: 6,
        render: function (data) {
          return '<span class="badge bg-danger text-white">' + data + '</span>';
        }
      },
      {
        targets: -1,
        title: 'Actions',
        orderable: false,
        searchable: false,
        render: function (data, type, full) {
          return (
            '<div class="d-flex flex-wrap gap-1">' +
              '<button type="button" class="btn btn-sm btn-primary low-item-adjust" data-id="' + full.id + '">' +
                '<i class="ti ti-plus me-1"></i>Refill Stock' +
              '</button>' +
              '<button type="button" class="btn btn-sm btn-outline-primary low-item-view-log" data-id="' + full.id + '">' +
                '<i class="ti ti-history me-1"></i>View Log' +
              '</button>' +
            '</div>'
          );
        }
      }
    ],
    order: [[5, 'desc'], [3, 'asc']],
    dom: '<"card-header flex-column flex-md-row"<"head-label text-center"><"dt-action-buttons text-end pt-3 pt-md-0"B>><"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>>t<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
    displayLength: 10,
    lengthMenu: [7, 10, 25, 50, 75, 100],
    buttons: [
      {
        extend: 'collection',
        className: 'btn btn-label-primary dropdown-toggle me-2',
        text: '<i class="ti ti-file-export me-sm-1"></i> <span class="d-none d-sm-inline-block">Export</span>',
        buttons: [
          { extend: 'csv', className: 'dropdown-item', exportOptions: { columns: [1, 2, 3, 4, 5, 6] } },
          { extend: 'excel', className: 'dropdown-item', exportOptions: { columns: [1, 2, 3, 4, 5, 6] } },
          { extend: 'pdf', className: 'dropdown-item', exportOptions: { columns: [1, 2, 3, 4, 5, 6] } },
          { extend: 'copy', className: 'dropdown-item', exportOptions: { columns: [1, 2, 3, 4, 5, 6] } }
        ]
      },
      {
        text: '<i class="ti ti-plus me-sm-1"></i> <span class="d-none d-sm-inline-block">Record Stock Action</span>',
        className: 'low-stock-create-new btn btn-primary',
        attr: {
          'data-bs-toggle': 'modal',
          'data-bs-target': '#stockModal'
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
            return 'Low stock details for ' + data['product__product_name'];
          }
        }),
        type: 'column',
        renderer: function (api, rowIdx, columns) {
          var data = $.map(columns, function (col) {
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

  $(document).on('change', '#lowProduct', function () {
    low_dt.ajax.url(buildLowStockUrl()).load();
  });

  $(document).on('click', '#lowClearFilters', function () {
    $('#lowProduct').val('');
    low_dt.ajax.url(buildLowStockUrl()).load();
  });

  $(document).on('click', '.low-stock-create-new[data-bs-target="#stockModal"]', function () {
    resetModalInputs('stockModal');
    $('#stockModalLabel').text('Record Stock Action');
    $('#stockForm').attr('action', '/add-stock/');
    $('#stockType').val('IN');
    $('#stockBranch').val(window.currentBranchId ? String(window.currentBranchId) : '');
    $('#stockProduct').val($('#lowProduct').val() || '');
    $('#stockRelatedBranch').val('');
    $('#stockProductQuantity').val('');
    $('#stockRemarks').val('');
    syncStockTransactionFields();
  });

  $('.low-stock-datatables-basic tbody').on('click', '.low-item-adjust', function () {
    resetModalInputs('stockModal');
    var row = resolveTableRow(low_dt, this);
    var data = row.data();

    $('#stockModalLabel').text('Refill Low Stock');
    $('#stockForm').attr('action', '/add-stock/');
    $('#stockType').val('IN');
    $('#stockBranch').val(String(data.branch__id));
    $('#stockProduct').val(String(data.product__id));
    $('#stockRelatedBranch').val('');
    $('#stockProductQuantity').val('');
    $('#stockRemarks').val('Low stock replenishment');
    syncStockTransactionFields();

    stockModalInstance.show();
  });

  $('.low-stock-datatables-basic tbody').on('click', '.low-item-view-log', function () {
    var row = resolveTableRow(low_dt, this);
    var data = row.data();
    if (!data) return;

    openStockHistoryModal({
      branchId: data.branch__id,
      branchName: data.branch__name,
      productId: data.product__id,
      productName: data.product__product_name
    });
  });

  low_table.closest('.card').find('.head-label.text-center').html('<h5 class="card-title mb-0">Low Stock Items</h5>');

  setTimeout(() => {
    $('.dataTables_filter .form-control').removeClass('form-control-sm');
    $('.dataTables_length .form-select').removeClass('form-select-sm');
  }, 300);
});

function formatPhpAmount(value) {
  var amount = Number.parseFloat(value || 0);
  if (Number.isNaN(amount)) amount = 0;
  return 'PHP ' + amount.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

function formatMomentDisplayValue(value, type, format) {
  if (!value) return '';

  var renderType = type || 'display';
  if (renderType !== 'display' && renderType !== 'filter') {
    return value;
  }

  var parsed = moment(value);
  return parsed.isValid() ? parsed.format(format) : value;
}

function formatDisplayDate(value, type) {
  return formatMomentDisplayValue(value, type, 'MMM D, YYYY');
}

function formatDisplayDateTime(value, type) {
  return formatMomentDisplayValue(value, type, 'MMM D, YYYY h:mm A');
}

function buildFlatpickrDisplayConfig(overrides) {
  return Object.assign({
    altInput: true,
    altFormat: 'M j, Y',
    dateFormat: 'Y-m-d'
  }, overrides || {});
}

function setFlatpickrInputValue(selector, value) {
  var element = document.querySelector(selector);
  if (!element) return;

  if (!element._flatpickr) {
    $(selector).val(value || '');
    return;
  }

  if (value) {
    element._flatpickr.setDate(value, false, 'Y-m-d');
    return;
  }

  element._flatpickr.clear();
}

function buildReportToolbarDom(includeFilters) {
  return (
    '<"card-header report-inline-toolbar d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2"' +
    '<"report-toolbar-actions d-flex flex-column flex-md-row align-items-md-center gap-2"<"dt-action-buttons"B><"report-toolbar-search"f>>>' +
    't' +
    '<"row align-items-center"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7 d-flex justify-content-center justify-content-md-end"p>>'
  );
}

function mountReportToolbarFilters(sourceSelector, wrapperSelector) {
  var source = $(sourceSelector);
  var target = $(wrapperSelector + ' .report-toolbar-filters');
  if (!source.length || !target.length) return;

  target.empty().append(source.removeClass('d-none'));
}

function normalizeReportToolbarControls(wrapperSelector) {
  $(wrapperSelector + ' .dataTables_filter .form-control').removeClass('form-control-sm');
  $(wrapperSelector + ' .dataTables_length .form-select').removeClass('form-select-sm');
}

// Summary Reports
$(function () {
  var brandTableEl = $('#brandSummaryTable');
  var categoryTableEl = $('#categorySummaryTable');
  var itemTableEl = $('#itemSummaryTable');
  if (!brandTableEl.length || !categoryTableEl.length || !itemTableEl.length) return;

  function currentSummaryBranch() {
    return $('#summaryBranch').val() || '';
  }

  function buildSummaryUrl(groupBy) {
    const params = new URLSearchParams();
    params.set('group_by', groupBy);
    if (currentSummaryBranch()) params.set('branch_id', currentSummaryBranch());
    return '/summary-report-data/?' + params.toString();
  }

  function updateSummaryCards(rows) {
    const data = Array.isArray(rows) ? rows : [];
    const totalProducts = data.length;
    const totalQuantity = data.reduce((sum, row) => sum + Number(row.total_quantity || 0), 0);
    const lowStockCount = data.filter(row => String(row.stock_status || '').toLowerCase() === 'low').length;
    const totalValue = data.reduce((sum, row) => sum + Number(row.total_value || 0), 0);

    $('#summaryProductsCard').text(totalProducts);
    $('#summaryQuantityCard').text(totalQuantity);
    $('#summaryLowStockCard').text(lowStockCount);
    $('#summaryValueCard').text(formatPhpAmount(totalValue));
  }

  var summaryPrimaryDom = buildReportToolbarDom(true);
  var summarySecondaryDom = buildReportToolbarDom(false);

  var brandDt = brandTableEl.DataTable({
    ajax: { url: buildSummaryUrl('brand') },
    columns: [
      { data: 'group_name' },
      { data: 'item_count' },
      { data: 'total_quantity' },
      { data: 'total_value' }
    ],
    columnDefs: [
      {
        targets: 3,
        render: function (d) {
          return formatPhpAmount(d);
        }
      }
    ],
    order: [[2, 'desc']],
    dom: summaryPrimaryDom,
    buttons: [
      {
        extend: 'collection',
        className: 'btn btn-label-primary dropdown-toggle me-2',
        text: '<i class="ti ti-file-export me-sm-1"></i>Download',
        buttons: [
          { extend: 'csv', className: 'dropdown-item' },
          { extend: 'excel', className: 'dropdown-item' },
          { extend: 'pdf', className: 'dropdown-item' },
          { extend: 'copy', className: 'dropdown-item' }
        ]
      }
    ]
  });

  var categoryDt = categoryTableEl.DataTable({
    ajax: { url: buildSummaryUrl('category') },
    columns: [
      { data: 'group_name' },
      { data: 'item_count' },
      { data: 'total_quantity' },
      { data: 'total_value' }
    ],
    columnDefs: [
      {
        targets: 3,
        render: function (d) {
          return formatPhpAmount(d);
        }
      }
    ],
    order: [[2, 'desc']],
    dom: summarySecondaryDom,
    buttons: [
      {
        extend: 'collection',
        className: 'btn btn-label-primary dropdown-toggle me-2',
        text: '<i class="ti ti-file-export me-sm-1"></i>Download',
        buttons: [
          { extend: 'csv', className: 'dropdown-item' },
          { extend: 'excel', className: 'dropdown-item' },
          { extend: 'pdf', className: 'dropdown-item' },
          { extend: 'copy', className: 'dropdown-item' }
        ]
      }
    ]
  });

  var itemDt = itemTableEl.DataTable({
    ajax: { url: buildSummaryUrl('item') },
    columns: [
      { data: 'product_name' },
      { data: 'total_quantity' },
      { data: 'low_stock_limit' },
      { data: 'stock_status' },
      { data: 'brand_name' },
      { data: 'category_name' },
      { data: 'unit_price' },
      { data: 'total_value' },
      { data: null, defaultContent: '' }
    ],
    columnDefs: [
      {
        targets: 6,
        render: function (d) {
          return formatPhpAmount(d);
        }
      },
      {
        targets: 7,
        render: function (d) {
          return formatPhpAmount(d);
        }
      },
      {
        targets: 3,
        render: function (d) {
          const value = String(d || '').toLowerCase();
          if (value === 'low') return '<span class="badge bg-danger text-white">Low</span>';
          if (value === 'medium') return '<span class="badge bg-warning text-dark">Medium</span>';
          return '<span class="badge bg-success text-white">High</span>';
        }
      },
      {
        targets: [4, 5, 6, 7],
        visible: false
      },
      {
        targets: -1,
        orderable: false,
        searchable: false,
        render: function (data, type, row) {
          return '<button type="button" class="btn btn-sm btn-outline-primary summary-view-log"><i class="ti ti-history me-1"></i>View History</button>';
        }
      }
    ],
    order: [[1, 'desc']],
    dom: summarySecondaryDom,
    buttons: [
      {
        extend: 'collection',
        className: 'btn btn-label-primary dropdown-toggle me-2',
        text: '<i class="ti ti-file-export me-sm-1"></i>Download',
        buttons: [
          { extend: 'csv', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6, 7] } },
          { extend: 'excel', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6, 7] } },
          { extend: 'pdf', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6, 7] } },
          { extend: 'copy', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6, 7] } }
        ]
      }
    ]
  });

  itemTableEl.on('xhr.dt', function (e, settings, json) {
    updateSummaryCards(json && json.data ? json.data : []);
  });

  mountReportToolbarFilters('#summaryReportFilters', '#brandSummaryTable_wrapper');

  itemTableEl.on('click', '.summary-view-log', function () {
    var row = resolveTableRow(itemDt, this);
    var data = row.data();
    if (!data) return;

    const branchId = currentSummaryBranch();
    const branchName = $('#summaryBranch option:selected').text() || 'All Branches';
    openStockHistoryModal({
      branchId: branchId,
      branchName: branchName,
      productId: data.product_id,
      productName: data.product_name,
      subtitle: data.product_name + ' in ' + branchName
    });
  });

  function reloadSummaryTables() {
    brandDt.ajax.url(buildSummaryUrl('brand')).load();
    categoryDt.ajax.url(buildSummaryUrl('category')).load();
    itemDt.ajax.url(buildSummaryUrl('item')).load();
  }

  $(document).on('change', '#summaryBranch', reloadSummaryTables);
  $(document).on('click', '#summaryClearFilters', function () {
    $('#summaryBranch').val('');
    reloadSummaryTables();
  });

  setTimeout(() => {
    normalizeReportToolbarControls('#brandSummaryTable_wrapper');
    normalizeReportToolbarControls('#categorySummaryTable_wrapper');
    normalizeReportToolbarControls('#itemSummaryTable_wrapper');
  }, 300);
});

// Daily Stock Out Report
$(function () {
  var salesTableEl = $('#dailySalesTable');
  if (!salesTableEl.length) return;

  if (document.getElementById('salesDateRange')) {
    flatpickr('#salesDateRange', buildFlatpickrDisplayConfig({ mode: 'range' }));
  }

  function buildDailySalesUrl() {
    const params = new URLSearchParams();
    const branchId = $('#salesBranch').val() || '';
    const productId = $('#salesProduct').val() || '';
    const dateRange = $('#salesDateRange').val() || '';
    if (branchId) params.set('branch_id', branchId);
    if (productId) params.set('product_id', productId);
    if (dateRange && dateRange.includes(' to ')) {
      const parts = dateRange.split(' to ');
      if (parts[0]) params.set('date_from', parts[0]);
      if (parts[1]) params.set('date_to', parts[1]);
    } else if (dateRange) {
      params.set('date_from', dateRange);
      params.set('date_to', dateRange);
    }
    return '/daily-sales-data/?' + params.toString();
  }

  function updateDailySalesCards(rows) {
    const data = Array.isArray(rows) ? rows : [];
    const totalRows = data.length;
    const totalQuantity = data.reduce((sum, row) => sum + Number(row.total_quantity || 0), 0);
    const totalValue = data.reduce((sum, row) => sum + Number(row.estimated_value || 0), 0);
    const uniqueProducts = new Set(data.map(row => row.product_id).filter(Boolean)).size;

    $('#salesRowsCard').text(totalRows);
    $('#salesQuantityCard').text(totalQuantity);
    $('#salesValueCard').text(formatPhpAmount(totalValue));
    $('#salesProductsCard').text(uniqueProducts);
  }

  var salesDt = salesTableEl.DataTable({
    ajax: { url: buildDailySalesUrl() },
    columns: [
      { data: 'sale_date' },
      { data: 'branch_name' },
      { data: 'product_name' },
      { data: 'brand_name' },
      { data: 'total_quantity' },
      { data: 'estimated_value' },
      { data: 'current_balance' },
      { data: null, defaultContent: '' }
    ],
    columnDefs: [
      {
        targets: 0,
        render: function (d, type) {
          return formatDisplayDate(d, type);
        }
      },
      {
        targets: 5,
        render: function (d) {
          return formatPhpAmount(d);
        }
      },
      {
        targets: -1,
        orderable: false,
        searchable: false,
        render: function (data, type, row) {
          return '<button type="button" class="btn btn-sm btn-outline-primary sales-view-log"><i class="ti ti-history me-1"></i>View History</button>';
        }
      }
    ],
    order: [[0, 'desc'], [1, 'asc'], [2, 'asc']],
    dom: buildReportToolbarDom(true),
    buttons: [
      {
        extend: 'collection',
        className: 'btn btn-label-primary dropdown-toggle me-2',
        text: '<i class="ti ti-file-export me-sm-1"></i>Download',
        buttons: [
          { extend: 'csv', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6] } },
          { extend: 'excel', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6] } },
          { extend: 'pdf', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6] } },
          { extend: 'copy', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6] } }
        ]
      }
    ]
  });

  salesTableEl.on('xhr.dt', function (e, settings, json) {
    updateDailySalesCards(json && json.data ? json.data : []);
  });

  mountReportToolbarFilters('#dailySalesReportFilters', '#dailySalesTable_wrapper');

  salesTableEl.on('click', '.sales-view-log', function () {
    var row = resolveTableRow(salesDt, this);
    var data = row.data();
    if (!data) return;

    openStockHistoryModal({
      branchId: data.branch_id,
      branchName: data.branch_name,
      productId: data.product_id,
      productName: data.product_name,
      typeValue: 'OUT',
      dateFrom: data.sale_date,
      dateTo: data.sale_date,
      subtitle: data.product_name + ' in ' + data.branch_name + ' on ' + formatDisplayDate(data.sale_date)
    });
  });

  function reloadDailySales() {
    salesDt.ajax.url(buildDailySalesUrl()).load();
  }

  $(document).on('change', '#salesBranch,#salesProduct', reloadDailySales);
  $(document).on('change', '#salesDateRange', function () {
    setTimeout(reloadDailySales, 50);
  });
  $(document).on('click', '#salesClearFilters', function () {
    $('#salesBranch').val('');
    $('#salesProduct').val('');
    setFlatpickrInputValue('#salesDateRange', '');
    reloadDailySales();
  });

  setTimeout(() => {
    normalizeReportToolbarControls('#dailySalesTable_wrapper');
  }, 300);
});

// Transfer Reports
$(function () {
  var transferTableEl = $('#transferReportTable');
  if (!transferTableEl.length) return;

  if (document.getElementById('transferDateRange')) {
    flatpickr('#transferDateRange', buildFlatpickrDisplayConfig({ mode: 'range' }));
  }

  function buildTransferReportUrl() {
    const params = new URLSearchParams();
    const branchId = $('#transferBranch').val() || '';
    const productId = $('#transferProduct').val() || '';
    const dateRange = $('#transferDateRange').val() || '';
    if (branchId) params.set('branch_id', branchId);
    if (productId) params.set('product_id', productId);
    if (dateRange && dateRange.includes(' to ')) {
      const parts = dateRange.split(' to ');
      if (parts[0]) params.set('date_from', parts[0]);
      if (parts[1]) params.set('date_to', parts[1]);
    } else if (dateRange) {
      params.set('date_from', dateRange);
      params.set('date_to', dateRange);
    }
    return '/transfer-report-data/?' + params.toString();
  }

  function updateTransferCards(rows) {
    const data = Array.isArray(rows) ? rows : [];
    const transferCount = data.length;
    const totalQuantity = data.reduce((sum, row) => sum + Number(row.quantity || 0), 0);
    const uniqueRoutes = new Set(
      data.map(row => (row.source_branch_name || '') + '|' + (row.destination_branch_name || '')).filter(Boolean)
    ).size;
    const uniqueProducts = new Set(data.map(row => row.product_id).filter(Boolean)).size;

    $('#transferCountCard').text(transferCount);
    $('#transferQuantityCard').text(totalQuantity);
    $('#transferRoutesCard').text(uniqueRoutes);
    $('#transferProductsCard').text(uniqueProducts);
  }

  var transferDt = transferTableEl.DataTable({
    ajax: { url: buildTransferReportUrl() },
    columns: [
      { data: 'transfer_date' },
      { data: 'source_branch_name' },
      { data: 'destination_branch_name' },
      { data: 'product_name' },
      { data: 'brand_name' },
      { data: 'quantity' },
      { data: 'handled_by_name' },
      { data: null, defaultContent: '' }
    ],
    columnDefs: [
      {
        targets: 0,
        render: function (d, type) {
          return formatDisplayDateTime(d, type);
        }
      },
      {
        targets: -1,
        orderable: false,
        searchable: false,
        render: function (data, type, row) {
          if (!row.transaction_group_id) {
            return '<button type="button" class="btn btn-sm btn-outline-primary" disabled><i class="ti ti-history me-1"></i>View History</button>';
          }
          return '<button type="button" class="btn btn-sm btn-outline-primary transfer-view-log"><i class="ti ti-history me-1"></i>View History</button>';
        }
      }
    ],
    order: [[0, 'desc'], [1, 'asc'], [3, 'asc']],
    dom: buildReportToolbarDom(true),
    buttons: [
      {
        extend: 'collection',
        className: 'btn btn-label-primary dropdown-toggle me-2',
        text: '<i class="ti ti-file-export me-sm-1"></i>Download',
        buttons: [
          { extend: 'csv', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6] } },
          { extend: 'excel', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6] } },
          { extend: 'pdf', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6] } },
          { extend: 'copy', className: 'dropdown-item', exportOptions: { columns: [0, 1, 2, 3, 4, 5, 6] } }
        ]
      }
    ]
  });

  transferTableEl.on('xhr.dt', function (e, settings, json) {
    updateTransferCards(json && json.data ? json.data : []);
  });

  mountReportToolbarFilters('#transferReportFilters', '#transferReportTable_wrapper');

  transferTableEl.on('click', '.transfer-view-log', function () {
    var row = resolveTableRow(transferDt, this);
    var data = row.data();
    if (!data || !data.transaction_group_id) return;

    openStockHistoryModal({
      productId: data.product_id,
      productName: data.product_name,
      groupId: data.transaction_group_id,
      subtitle: data.product_name + ': ' + data.source_branch_name + ' to ' + data.destination_branch_name
    });
  });

  function reloadTransferReports() {
    transferDt.ajax.url(buildTransferReportUrl()).load();
  }

  $(document).on('change', '#transferBranch,#transferProduct', reloadTransferReports);
  $(document).on('change', '#transferDateRange', function () {
    setTimeout(reloadTransferReports, 50);
  });
  $(document).on('click', '#transferClearFilters', function () {
    $('#transferBranch').val('');
    $('#transferProduct').val('');
    setFlatpickrInputValue('#transferDateRange', '');
    reloadTransferReports();
  });

  setTimeout(() => {
    normalizeReportToolbarControls('#transferReportTable_wrapper');
  }, 300);
});

// Stock Movements DataTable
$(function () {
  var mv_table = $('.movement-datatables-basic');
  if (!mv_table.length) return;

  // Initialize date range picker
  if (document.getElementById('mvDateRange')) {
    flatpickr('#mvDateRange', buildFlatpickrDisplayConfig({ mode: 'range' }));
  }

  function buildMovementUrl() {
    const params = new URLSearchParams();
    const b = window.currentBranchId ? String(window.currentBranchId) : '';
    const p = $('#mvProduct').val() || '';
    const t = $('#mvType').val() || '';
    const g = $('#mvGroupId').val() || '';
    const dr = $('#mvDateRange').val() || '';
    if (b) params.set('branch_id', b);
    if (p) params.set('product_id', p);
    if (t) params.set('type', t);
    if (g) params.set('group_id', g);
    if (dr && dr.includes(' to ')) {
      const parts = dr.split(' to ');
      if (parts[0]) params.set('date_from', parts[0]);
      if (parts[1]) params.set('date_to', parts[1]);
    } else if (dr) {
      params.set('date_from', dr);
      params.set('date_to', dr);
    }
    return '/movement-data/?' + params.toString();
  }

  var mv_dt = mv_table.DataTable({
    ajax: { url: buildMovementUrl() },
    columns: [
      { data: null, defaultContent: '' },
      { data: 'date' },
      { data: 'transaction_id' },
      { data: 'product__product_name', render: function (data, type, row) { return data + ' (' + (row['product__brand__name'] || '') + ')'; } },
      { data: 'balance_before', defaultContent: 0 },
      { data: 'quantity' },
      { data: 'balance_after' },
      { data: 'handled_by__username', defaultContent: '' },
      { data: 'remarks', defaultContent: '' }
    ],
    columnDefs: [
      { className: 'control', orderable: false, searchable: false, targets: 0, render: function () { return ''; } },
      { targets: 1, render: function (d, type) { return formatDisplayDateTime(d, type); } },
      {
        targets: 4,
        render: function (d) {
          return '<span class="fw-semibold">' + (d ?? 0) + '</span>';
        }
      },
      {
        targets: 5,
        render: function (d, type, row) {
          return renderMovementActionMarkup(d, row);
        }
      },
      {
        targets: 6,
        render: function (d) {
          return '<span class="fw-semibold">' + (d ?? 0) + '</span>';
        }
      }
    ],
    order: [[1, 'desc']],
    dom: '<"card-header flex-column flex-md-row"<"head-label text-center"><"dt-action-buttons text-end pt-3 pt-md-0"B>><"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>>t<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
    buttons: [
      {
        extend: 'collection',
        className: 'btn btn-label-primary dropdown-toggle me-2',
        text: '<i class="ti ti-file-export me-sm-1"></i> <span class="d-none d-sm-inline-block">Export</span>',
        buttons: [
          { extend: 'csv', className: 'dropdown-item' },
          { extend: 'excel', className: 'dropdown-item' },
          { extend: 'pdf', className: 'dropdown-item' },
          { extend: 'copy', className: 'dropdown-item' }
        ]
      }
    ]
  });

  function reloadMovements() {
    mv_dt.ajax.url(buildMovementUrl()).load();
  }

  function clearMovementFocus() {
    if ($('#mvGroupId').length) {
      $('#mvGroupId').val('');
    }
  }

  $(document).on('change', '#mvProduct,#mvType', function () {
    clearMovementFocus();
    reloadMovements();
  });
  $(document).on('change', '#mvDateRange', function () {
    clearMovementFocus();
    setTimeout(reloadMovements, 50);
  });
});

// Daily Transactions DataTable
$(function () {
  var dailyMvTable = $('.daily-movement-datatables-basic');
  if (!dailyMvTable.length) return;

  const todayIso = moment().format('YYYY-MM-DD');
  if (document.getElementById('dailyMvDate')) {
    flatpickr('#dailyMvDate', buildFlatpickrDisplayConfig());
    if (!$('#dailyMvDate').val()) {
      setFlatpickrInputValue('#dailyMvDate', todayIso);
    }
  }

  function buildDailyMovementUrl() {
    const params = new URLSearchParams();
    const branchId = window.currentBranchId ? String(window.currentBranchId) : '';
    const productId = $('#dailyMvProduct').val() || '';
    const typeValue = $('#dailyMvType').val() || '';
    const selectedDate = $('#dailyMvDate').val() || todayIso;

    if (branchId) params.set('branch_id', branchId);
    if (productId) params.set('product_id', productId);
    if (typeValue) params.set('type', typeValue);
    if (selectedDate) {
      params.set('date_from', selectedDate);
      params.set('date_to', selectedDate);
    }

    return '/movement-data/?' + params.toString();
  }

  var dailyMvDt = dailyMvTable.DataTable({
    ajax: { url: buildDailyMovementUrl() },
    columns: [
      { data: null, defaultContent: '' },
      { data: 'date' },
      { data: 'transaction_id' },
      { data: 'product__product_name', render: function (data, type, row) { return data + ' (' + (row['product__brand__name'] || '') + ')'; } },
      { data: 'balance_before', defaultContent: 0 },
      { data: 'quantity' },
      { data: 'balance_after' },
      { data: 'handled_by__username', defaultContent: '' },
      { data: 'remarks', defaultContent: '' }
    ],
    columnDefs: [
      { className: 'control', orderable: false, searchable: false, targets: 0, render: function () { return ''; } },
      { targets: 1, render: function (d, type) { return formatDisplayDateTime(d, type); } },
      {
        targets: 4,
        render: function (d) {
          return '<span class="fw-semibold">' + (d ?? 0) + '</span>';
        }
      },
      {
        targets: 5,
        render: function (d, type, row) {
          return renderMovementActionMarkup(d, row);
        }
      },
      {
        targets: 6,
        render: function (d) {
          return '<span class="fw-semibold">' + (d ?? 0) + '</span>';
        }
      }
    ],
    order: [[1, 'desc']],
    dom: '<"card-header flex-column flex-md-row"<"head-label text-center"><"dt-action-buttons text-end pt-3 pt-md-0"B>><"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>>t<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
    buttons: [
      {
        extend: 'collection',
        className: 'btn btn-label-primary dropdown-toggle me-2',
        text: '<i class="ti ti-file-export me-sm-1"></i> <span class="d-none d-sm-inline-block">Export</span>',
        buttons: [
          { extend: 'csv', className: 'dropdown-item' },
          { extend: 'excel', className: 'dropdown-item' },
          { extend: 'pdf', className: 'dropdown-item' },
          { extend: 'copy', className: 'dropdown-item' }
        ]
      }
    ]
  });

  dailyMvTable.closest('.card').find('.head-label.text-center').html('<h5 class="card-title mb-0">Daily Transactions</h5>');

  function reloadDailyMovements() {
    dailyMvDt.ajax.url(buildDailyMovementUrl()).load();
  }

  $(document).on('change', '#dailyMvProduct,#dailyMvType', reloadDailyMovements);
  $(document).on('change', '#dailyMvDate', function () {
    setTimeout(reloadDailyMovements, 50);
  });
  $(document).on('click', '#dailyMvClearFilters', function () {
    $('#dailyMvProduct').val('');
    $('#dailyMvType').val('');
    setFlatpickrInputValue('#dailyMvDate', todayIso);
    reloadDailyMovements();
  });
});
$(document).on('shown.bs.tab shown.bs.collapse', '#stocksWorkspaceTabs [data-bs-toggle="tab"], #reportsWorkspaceTabs [data-bs-toggle="tab"], .report-detail-accordion .accordion-collapse', function () {
  setTimeout(function () {
    if ($.fn.dataTable) {
      $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
    }
  }, 100);
});
$(document).on('change', '#stockType', syncStockTransactionFields);
$(document).on('change', '#stockBranch,#stockProduct', function () {
  clearStockFieldError(this);
  void refreshStockBalance();
});
$(document).on('change', '#stockRelatedBranch', function () {
  clearStockFieldError(this);
});
$(document).on('input', '#stockProductQuantity', function () {
  clearStockFieldError(this);
});
if (document.getElementById('stockForm')) {
  document.getElementById('stockForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    clearStockFormValidation();

    const branchField = this.querySelector('[name="branch"]');
    const productField = this.querySelector('[name="product"]');
    const typeField = this.querySelector('[name="transaction_type"]');
    const relatedBranchField = this.querySelector('[name="related_branch"]');
    const quantityField = this.querySelector('[name="quantity"]');

    const typeValue = typeField ? typeField.value : 'IN';
    const quantityValue = Number(quantityField && quantityField.value ? quantityField.value : 0);
    let hasClientErrors = false;

    if (typeValue === 'BACKLOAD') {
      if (!relatedBranchField || !relatedBranchField.value) {
        setStockFieldError(relatedBranchField, 'Choose the destination branch for this transfer.');
        hasClientErrors = true;
      } else if (branchField && branchField.value && relatedBranchField.value === branchField.value) {
        setStockFieldError(relatedBranchField, 'Destination branch must be different from the source branch.');
        hasClientErrors = true;
      }
    }

    if ((typeValue === 'OUT' || typeValue === 'BACKLOAD') && branchField && branchField.value && productField && productField.value && quantityValue > 0) {
      const currentBalance = await refreshStockBalance();
      if (currentBalance !== null && quantityValue > currentBalance) {
        setStockFieldError(quantityField, 'Only ' + currentBalance + ' item(s) are currently available in this branch.');
        hasClientErrors = true;
      }
    }

    if (hasClientErrors) {
      return;
    }

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
          if (data.errors) {
            for (const [field, errors] of Object.entries(data.errors)) {
              const input = document.querySelector(`[name=${field}]`);
              if (input) {
                setStockFieldError(input, errors);
              }
            }
          } else if (data.message) {
            alert(data.message);
          }
        }
      })
      .catch(error => console.error('Error:', error));
  });
}

// ======================= SHARED FUNCTIONS =======================
// function to reset modal inputs readonly and error messages for all modals
function resetModalInputs(modalId) {
  // console.log('Resetting modal inputs for modal ID:', modalId);
  // Reset the form and remove error messages for the specified modal
  const modal = document.getElementById(modalId);
  if (modal) {
    const form = modal.querySelector('form');
    if (form) {
      form.reset();
      form.querySelectorAll('input').forEach(input => {
        // reset modal-title
        const modalTitle = modal.querySelector('.modal-title');
        if (modalTitle) {
          modalTitle.textContent = modalId === 'stockModal' ? 'Record Stock Action' : 'Add New Record'; // Reset to default title
        }
        input.classList.remove('is-invalid');
        input.removeAttribute('readonly');
        input.disabled = false;

        // Remove error messages
        const errorContainer = input.nextElementSibling;
        if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
          errorContainer.innerHTML = '';
        }
      });
      form.querySelectorAll('textarea').forEach(input => {
        input.classList.remove('is-invalid');
        input.removeAttribute('readonly');

        // Remove error messages
        const errorContainer = input.nextElementSibling;
        if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
          errorContainer.innerHTML = '';
        }
      });
      form.querySelectorAll('select').forEach(select => {
        select.classList.remove('is-invalid');
        select.removeAttribute('readonly');
        select.disabled = false; // Ensure select is enabled for add/edit

        // Remove error messages
        const errorContainer = select.nextElementSibling;
        if (errorContainer && errorContainer.classList.contains('fv-plugins-message-container')) {
          errorContainer.innerHTML = '';
        }
      });
      
      // Restore submit button if missing
      const submitBtn = form.querySelector('button[type="submit"]');
      const btnContainer = form.querySelector('.col-12.text-center');
      if (!submitBtn && btnContainer) {
        if (modalId === 'stockModal') {
          btnContainer.innerHTML = `
            <button type="submit" id="stockSubmitButton" class="btn btn-primary me-sm-3 me-1 waves-effect waves-light">Receive Stock</button>
            <button type="button" class="btn btn-label-secondary waves-effect" data-bs-dismiss="modal">Cancel</button>
          `;
        } else {
          btnContainer.innerHTML = `
            <button type="submit" class="btn btn-primary me-sm-3 me-1 waves-effect waves-light">Submit</button>
            <button type="button" class="btn btn-label-secondary waves-effect" data-bs-dismiss="modal">Cancel</button>
          `;
        }
      }
      syncStockTransactionFields();
    }
  } else {
    // If the modal is not found, log an error
    console.error('Modal not found:', modalId);
  }
}

// Attach reset function to all modals
document.querySelectorAll('.modal').forEach(modal => {
  modal.addEventListener('hidden.bs.modal', function () {
    resetModalInputs(modal.id);
  });
});
