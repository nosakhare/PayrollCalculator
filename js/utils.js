/**
 * Utility functions for salary calculations
 */

const utils = {
    /**
     * Validate CSV structure and data types
     * @param {Object[]} data - Array of objects representing CSV rows
     * @returns {Object} Validation result
     */
    validateCSV(data) {
        const requiredColumns = [
            'Account Number',
            'STAFF ID',
            'Email',
            'NAME',
            'DEPARTMENT',
            'JOB TITLE',
            'ANNUAL GROSS PAY',
            'START DATE',
            'END DATE',
            'Contract Type',
            'Reimbursements',
            'Other Deductions',
            'VOLUNTARY_PENSION'
        ];

        // Check for required columns
        const missingColumns = requiredColumns.filter(col => 
            !Object.keys(data[0]).includes(col)
        );

        if (missingColumns.length > 0) {
            return {
                valid: false,
                message: `Missing required columns: ${missingColumns.join(', ')}`
            };
        }

        try {
            // Validate data types and values
            for (const row of data) {
                // Convert numeric fields
                row['ANNUAL GROSS PAY'] = Number(row['ANNUAL GROSS PAY']);
                row['Reimbursements'] = Number(row['Reimbursements'] || 0);
                row['Other Deductions'] = Number(row['Other Deductions'] || 0);
                row['VOLUNTARY_PENSION'] = Number(row['VOLUNTARY_PENSION'] || 0);

                // Validate dates
                if (!Date.parse(row['START DATE']) || !Date.parse(row['END DATE'])) {
                    throw new Error('Invalid date format');
                }

                // Validate voluntary pension (not exceeding 1/3 of monthly salary)
                const monthlySalary = row['ANNUAL GROSS PAY'] / 12;
                if (row['VOLUNTARY_PENSION'] > monthlySalary / 3) {
                    return {
                        valid: false,
                        message: 'Voluntary pension cannot exceed 1/3 of monthly salary'
                    };
                }

                // Validate Contract Type
                const validContractTypes = ['Full Time', 'Contract'];
                if (!validContractTypes.includes(row['Contract Type'])) {
                    return {
                        valid: false,
                        message: `Invalid contract type: ${row['Contract Type']}. Must be either 'Full Time' or 'Contract'`
                    };
                }
            }
        } catch (error) {
            return {
                valid: false,
                message: `Data type validation failed: ${error.message}`
            };
        }

        return { valid: true, message: 'Validation successful' };
    },

    /**
     * Validate that component percentages sum to 100%
     * @param {number} total - Sum of all component percentages
     * @returns {boolean} Whether the total is valid
     */
    validatePercentages(total) {
        return Math.abs(total - 100.0) < 0.01;
    },

    /**
     * Generate a template CSV file with example data
     * @returns {string} CSV content
     */
    generateCSVTemplate() {
        const today = new Date();
        const lastYear = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());

        const exampleData = [
            {
                'Account Number': '1234567890',
                'STAFF ID': 'EMP001',
                'Email': 'john.doe@company.com',
                'NAME': 'John Doe',
                'DEPARTMENT': 'Engineering',
                'JOB TITLE': 'Software Engineer',
                'ANNUAL GROSS PAY': '5000000',
                'START DATE': lastYear.toISOString().split('T')[0],
                'END DATE': today.toISOString().split('T')[0],
                'Contract Type': 'Full Time',
                'Reimbursements': '50000',
                'Other Deductions': '10000',
                'VOLUNTARY_PENSION': '0'
            },
            {
                'Account Number': '0987654321',
                'STAFF ID': 'CON001',
                'Email': 'jane.smith@company.com',
                'NAME': 'Jane Smith',
                'DEPARTMENT': 'Design',
                'JOB TITLE': 'UI Designer',
                'ANNUAL GROSS PAY': '4000000',
                'START DATE': new Date(today.getFullYear(), today.getMonth() - 6, today.getDate()).toISOString().split('T')[0],
                'END DATE': today.toISOString().split('T')[0],
                'Contract Type': 'Contract',
                'Reimbursements': '25000',
                'Other Deductions': '5000',
                'VOLUNTARY_PENSION': '0'
            }
        ];

        // Convert to CSV
        const headers = Object.keys(exampleData[0]);
        const csv = [
            headers.join(','),
            ...exampleData.map(row => 
                headers.map(header => 
                    typeof row[header] === 'string' && row[header].includes(',') 
                        ? `"${row[header]}"` 
                        : row[header]
                ).join(',')
            )
        ].join('\n');

        return csv;
    },

    /**
     * Format currency in Naira
     * @param {number} amount - Amount to format
     * @returns {string} Formatted amount
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-NG', {
            style: 'currency',
            currency: 'NGN',
            minimumFractionDigits: 2
        }).format(amount);
    },

    /**
     * Calculate the ratio of working days in a date range
     * @param {string} startDate - Start date in YYYY-MM-DD format
     * @param {string} endDate - End date in YYYY-MM-DD format
     * @returns {number} Ratio of working days
     */
    calculateWorkingDaysRatio(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        // Get the month range
        const monthStart = new Date(end.getFullYear(), end.getMonth(), 1);
        const monthEnd = new Date(end.getFullYear(), end.getMonth() + 1, 0);

        // Count weekdays in the worked period and total month
        const countWeekdays = (from, to) => {
            let count = 0;
            const current = new Date(from);
            while (current <= to) {
                if (current.getDay() !== 0 && current.getDay() !== 6) {
                    count++;
                }
                current.setDate(current.getDate() + 1);
            }
            return count;
        };

        const workedWeekdays = countWeekdays(start, end);
        const totalWeekdays = countWeekdays(monthStart, monthEnd);

        return Number((workedWeekdays / totalWeekdays).toFixed(2));
    }
};

// Make utils available globally
window.utils = utils;
