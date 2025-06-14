// Function to view project reports
function viewProjectReports(projectId) {
    const modal = new bootstrap.Modal(document.getElementById('projectReportsModal'));
    
    // Fetch reports for each type
    ['progress', 'damage', 'bills', 'supply'].forEach(type => {
        fetch(`/api/project/${projectId}/reports/${type}`)
            .then(response => response.json())
            .then(data => {
                const tabContent = document.getElementById(type);
                tabContent.innerHTML = generateReportHTML(data);
            })
            .catch(error => console.error('Error fetching reports:', error));
    });
    
    modal.show();
}

// Function to generate HTML for reports
function generateReportHTML(reports) {
    if (!reports.length) {
        return '<p class="text-muted">No reports available.</p>';
    }
    
    return reports.map(report => `
        <div class="card mb-3">
            <div class="card-body">
                <h6 class="card-subtitle mb-2 text-muted">
                    ${new Date(report.created_at).toLocaleDateString()}
                </h6>
                <p class="card-text">${report.description}</p>
                <p class="card-text"><strong>Coordinates:</strong> ${report.latitude || '-'}, ${report.longitude || '-'}</p>
                <div class="row">
                    ${report.photos.map(photo => `
                        <div class="col-md-3 mb-2">
                            <img src="/static/uploads/${photo.filename}" 
                                 class="img-thumbnail" 
                                 style="height: 150px; object-fit: cover;"
                                 onclick="showFullImage(this.src)">
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

// Function to show full-size image
function showFullImage(src) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-body p-0">
                    <button type="button" class="btn-close position-absolute top-0 end-0 m-2" 
                            data-bs-dismiss="modal"></button>
                    <img src="${src}" class="img-fluid">
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

// Function to assign engineers to a project
function assignEngineers(projectId) {
    fetch(`/api/project/${projectId}/available-engineers`)
        .then(response => response.json())
        .then(engineers => {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Assign Engineers</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="assignEngineersForm">
                                ${engineers.map(engineer => `
                                    <div class="form-check mb-2">
                                        <input class="form-check-input" type="checkbox" 
                                               name="engineers" value="${engineer.id}" 
                                               id="engineer${engineer.id}">
                                        <label class="form-check-label" for="engineer${engineer.id}">
                                            ${engineer.username}
                                        </label>
                                    </div>
                                `).join('')}
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary" onclick="saveEngineerAssignments(${projectId})">
                                Save Assignments
                            </button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
            modal.addEventListener('hidden.bs.modal', () => {
                document.body.removeChild(modal);
            });
        })
        .catch(error => console.error('Error fetching engineers:', error));
}

// Function to save engineer assignments
function saveEngineerAssignments(projectId) {
    const form = document.getElementById('assignEngineersForm');
    const selectedEngineers = Array.from(form.querySelectorAll('input[name="engineers"]:checked'))
        .map(input => input.value);
    
    fetch(`/api/project/${projectId}/assign-engineers`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ engineers: selectedEngineers })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error assigning engineers');
        }
    })
    .catch(error => console.error('Error saving assignments:', error));
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 