/**
 * Main JavaScript file for the Nigerian Salary Calculator
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const components = {
        BASIC: document.getElementById('basic'),
        TRANSPORT: document.getElementById('transport'),
        HOUSING: document.getElementById('housing'),
        UTILITY: document.getElementById('utility')
    };

    const totalPercentageDisplay = document.getElementById('totalPercentage');
    const percentageError = document.getElementById('percentageError');
    const calculateButton = document.getElementById('calculateButton');
    const singleEmployeeForm = document.getElementById('singleEmployeeForm');
    const resultsSection = document.getElementById('results');
    const resultsGrid = document.querySelector('.results-grid');
    const newCalculationBtn = document.getElementById('newCalculation');

    // Tab handling
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            
            // Update active states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            button.classList.add('active');
            document.getElementById(tabId === 'single' ? 'singleEmployee' : 'multipleEmployees').classList.add('active');
        });
    });

    // Component percentage handling
    Object.values(components).forEach(input => {
        input.addEventListener('input', updateTotalPercentage);
    });

    function updateTotalPercentage() {
        const total = Object.values(components)
            .reduce((sum, input) => sum + Number(input.value), 0);
        
        totalPercentageDisplay.textContent = `${total.toFixed(1)}%`;
        const isValid = utils.validatePercentages(total);
        
        percentageError.classList.toggle('hidden', isValid);
        calculateButton.disabled = !isValid || Number(document.getElementById('annualGross').value) <= 0;
    }

    // Annual gross input handling
    document.getElementById('annualGross').addEventListener('input', (e) => {
        calculateButton.disabled = !utils.validatePercentages(
            Object.values(components).reduce((sum, input) => sum + Number(input.value), 0)
        ) || Number(e.target.value) <= 0;
    });

    // Single employee form handling
    singleEmployeeForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const componentPercentages = Object.fromEntries(
            Object.entries(components).map(([key, input]) => [key, Number(input.value)])
        );

        const calculator = new SalaryCalculator(componentPercentages);
        const result = calculator.processEmployee({
            'Account Number': '',
            'STAFF ID': '',
            'Email': '',
            'NAME': '',
            'DEPARTMENT': '',
            'JOB TITLE': '',
            'ANNUAL GROSS PAY': Number(document.getElementById('annualGross').value),
            'Contract Type': document.getElementById('contractType').value,
            'START DATE': document.getElementById('startDate').value,
            'END DATE': document.getElementById('endDate').value,
            'Reimbursements': Number(document.getElementById('reimbursements').value),
            'Other Deductions': Number(document.getElementById('otherDeductions').value),
            'VOLUNTARY_PENSION': Number(document.getElementById('voluntaryPension').value)
        });

        displayResults(result);
    });

    function displayResults(result) {
        // Clear previous results
        resultsGrid.innerHTML = '';

        // Create and populate result sections
        const sections = [
            {
                title: 'Monthly Breakdown',
                items: [
                    ['Monthly Gross', result.MONTHLY_GROSS],
                    ['Prorated Monthly', result.PRORATED_MONTHLY_GROSS],
                    ['Working Days Ratio', `${(result.WORKING_DAYS_RATIO * 100).toFixed(1)}%`]
                ]
            },
            {
                title: 'Components',
                items: [
                    ['Basic', result.COMP_BASIC],
                    ['Transport', result.COMP_TRANSPORT],
                    ['Housing', result.COMP_HOUSING],
                    ['Utility', result.COMP_UTILITY]
                ]
            },
            {
                title: 'Deductions',
                items: [
                    ['Employee Pension', result.MANDATORY_PENSION],
                    ['Voluntary Pension', result.VOLUNTARY_PENSION],
                    ['PAYE Tax', result.PAYE_TAX],
                    ['Other Deductions', result.OTHER_DEDUCTIONS],
                    ['Total Deductions', result.TOTAL_DEDUCTIONS]
                ]
            },
            {
                title: 'Tax Details',
                items: [
                    ['CRA', result.CRA],
                    ['Taxable Pay', result.TAXABLE_PAY],
                    ['Tax Relief', result.TAX_RELIEF],
                    ['PAYE Tax', result.PAYE_TAX]
                ]
            }
        ];

        sections.forEach(section => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'result-section';
            
            const title = document.createElement('h3');
            title.textContent = section.title;
            sectionDiv.appendChild(title);

            const list = document.createElement('div');
            list.className = 'result-list';

            section.items.forEach(([label, value]) => {
                const item = document.createElement('div');
                item.className = 'result-item';
                
                const labelSpan = document.createElement('span');
                labelSpan.className = 'result-label';
                labelSpan.textContent = label;

                const valueSpan = document.createElement('span');
                valueSpan.className = 'result-value';
                valueSpan.textContent = typeof value === 'number' ? 
                    utils.formatCurrency(value) : value;

                item.appendChild(labelSpan);
                item.appendChild(valueSpan);
                list.appendChild(item);
            });

            sectionDiv.appendChild(list);
            resultsGrid.appendChild(sectionDiv);
        });

        // Show results section
        resultsSection.classList.remove('hidden');
        singleEmployeeForm.classList.add('hidden');
    }

    // New calculation button handling
    newCalculationBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        singleEmployeeForm.classList.remove('hidden');
        singleEmployeeForm.reset();
        updateTotalPercentage();
    });

    // File upload handling
    const csvUpload = document.getElementById('csvUpload');
    const preview = document.getElementById('preview');
    const previewTable = document.querySelector('.preview-table');
    const calculateAllBtn = document.getElementById('calculateAll');
    const bulkResults = document.getElementById('bulkResults');
    const resultsTable = document.querySelector('.results-table');
    const downloadResultsBtn = document.getElementById('downloadResults');
    const newBulkCalculationBtn = document.getElementById('newBulkCalculation');

    csvUpload.addEventListener('change', handleFileUpload);

    function handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            const csv = e.target.result;
            const results = parseCSV(csv);
            
            if (results.valid) {
                displayPreview(results.data);
                preview.classList.remove('hidden');
            } else {
                alert(results.message);
                csvUpload.value = '';
            }
        };
        reader.readAsText(file);
    }

    function parseCSV(csv) {
        try {
            // Basic CSV parsing (consider using a library like Papa Parse for production)
            const lines = csv.split('\n');
            const headers = lines[0].split(',').map(h => h.trim());
            const data = lines.slice(1)
                .filter(line => line.trim())
                .map(line => {
                    const values = line.split(',');
                    return headers.reduce((obj, header, i) => {
                        obj[header] = values[i].trim();
                        return obj;
                    }, {});
                });

            const validation = utils.validateCSV(data);
            return validation.valid ? { valid: true, data } : validation;
        } catch (error) {
            return { valid: false, message: `Error parsing CSV: ${error.message}` };
        }
    }

    function displayPreview(data) {
        // Display first few rows
        const previewData = data.slice(0, 5);
        
        // Create table
        const table = document.createElement('table');
        
        // Add headers
        const headers = Object.keys(previewData[0]);
        const headerRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);
        
        // Add data rows
        previewData.forEach(row => {
            const tr = document.createElement('tr');
            headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = row[header];
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });
        
        // Clear and update preview
        previewTable.innerHTML = '';
        previewTable.appendChild(table);
    }

    // Download template handling
    document.getElementById('downloadTemplate').addEventListener('click', () => {
        const csv = utils.generateCSVTemplate();
        downloadCSV(csv, 'employee_template.csv');
    });

    function downloadCSV(csv, filename) {
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (navigator.msSaveBlob) {
            navigator.msSaveBlob(blob, filename);
            return;
        }
        link.href = URL.createObjectURL(blob);
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // Calculate all button handling
    calculateAllBtn.addEventListener('click', () => {
        const componentPercentages = Object.fromEntries(
            Object.entries(components).map(([key, input]) => [key, Number(input.value)])
        );

        const calculator = new SalaryCalculator(componentPercentages);
        const results = calculator.processDataframe(parseCSV(csvUpload.files[0]).data);
        
        displayBulkResults(results);
        preview.classList.add('hidden');
        bulkResults.classList.remove('hidden');
    });

    function displayBulkResults(results) {
        // Create table
        const table = document.createElement('table');
        
        // Add headers
        const headers = Object.keys(results[0]);
        const headerRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);
        
        // Add data rows
        results.forEach(row => {
            const tr = document.createElement('tr');
            headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = typeof row[header] === 'number' ? 
                    utils.formatCurrency(row[header]) : row[header];
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });
        
        // Clear and update results
        resultsTable.innerHTML = '';
        resultsTable.appendChild(table);
        
        // Store results for download
        downloadResultsBtn.onclick = () => {
            const csv = [
                headers.join(','),
                ...results.map(row => 
                    headers.map(header => 
                        typeof row[header] === 'string' && row[header].includes(',') ?
                            `"${row[header]}"` : row[header]
                    ).join(',')
                )
            ].join('\n');
            
            downloadCSV(csv, 'salary_results.csv');
        };
    }

    // New bulk calculation button handling
    newBulkCalculationBtn.addEventListener('click', () => {
        bulkResults.classList.add('hidden');
        preview.classList.add('hidden');
        csvUpload.value = '';
    });

    // Initialize component percentages
    updateTotalPercentage();
});
