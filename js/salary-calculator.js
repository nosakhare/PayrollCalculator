/**
 * Salary Calculator class for Nigerian payroll processing
 */
class SalaryCalculator {
    constructor(components) {
        this.components = components;
    }

    /**
     * Calculate monthly gross from annual gross
     * @param {number} annualGross - Annual gross salary
     * @returns {number} Monthly gross salary
     */
    calculateMonthlyGross(annualGross) {
        return Number((annualGross / 12).toFixed(2));
    }

    /**
     * Calculate individual salary components
     * @param {number} monthlyGross - Monthly gross salary
     * @param {number} workingDaysRatio - Ratio of days worked
     * @returns {Object} Salary components
     */
    calculateComponents(monthlyGross, workingDaysRatio = 1) {
        const components = {};
        for (const [component, percentage] of Object.entries(this.components)) {
            components[component] = Number(
                (monthlyGross * (percentage / 100) * workingDaysRatio).toFixed(2)
            );
        }
        return components;
    }

    /**
     * Calculate pension contributions
     * @param {Object} params - Pension calculation parameters
     * @returns {Object} Pension details
     */
    calculatePension({
        basic,
        transport,
        housing,
        contractType,
        monthlyGross,
        voluntaryPension = 0
    }) {
        if (contractType.trim().toUpperCase() === 'CONTRACT' || monthlyGross < 30000) {
            return {
                employeePension: 0,
                employerPension: 0,
                voluntaryPension: 0,
                totalPension: 0
            };
        }

        const pensionableBase = basic + transport + housing;
        const employeePension = Number((0.08 * pensionableBase).toFixed(2));
        const employerPension = Number((0.10 * pensionableBase).toFixed(2));
        const voluntary = Number(voluntaryPension.toFixed(2));
        const totalPension = employeePension + employerPension + voluntary;

        return {
            employeePension,
            employerPension,
            voluntaryPension: voluntary,
            totalPension
        };
    }

    /**
     * Calculate Consolidated Relief Allowance (CRA)
     * @param {number} grossPay - Gross pay
     * @param {number} pension - Pension deduction
     * @returns {number} CRA amount
     */
    calculateCRA(grossPay, pension) {
        const grossAfterPension = grossPay - pension;
        const craPercentage = Number((0.2 * grossAfterPension).toFixed(2));
        const minimumRelief = Number(
            Math.max(0.01 * grossAfterPension, 200000 / 12).toFixed(2)
        );
        return Number((craPercentage + minimumRelief).toFixed(2));
    }

    /**
     * Calculate PAYE tax
     * @param {number} taxablePay - Taxable pay amount
     * @returns {number} PAYE tax amount
     */
    calculatePAYE(taxablePay) {
        const taxBands = [
            [300000, 0.07],
            [300000, 0.11],
            [500000, 0.15],
            [500000, 0.19],
            [1600000, 0.21],
            [Infinity, 0.24]
        ];

        const annualTaxable = taxablePay * 12;
        let totalTax = 0;
        let remainingIncome = annualTaxable;

        for (const [band, rate] of taxBands) {
            if (remainingIncome <= 0) break;
            const taxableInBand = Math.min(band, remainingIncome);
            totalTax += taxableInBand * rate;
            remainingIncome -= band;
        }

        return Number((totalTax / 12).toFixed(2));
    }

    /**
     * Process salary calculations for a single employee
     * @param {Object} employee - Employee data
     * @returns {Object} Calculated salary details
     */
    processEmployee(employee) {
        // Calculate working days ratio
        const workingRatio = utils.calculateWorkingDaysRatio(
            employee['START DATE'],
            employee['END DATE']
        );

        // Calculate monthly gross
        const monthlyGross = this.calculateMonthlyGross(employee['ANNUAL GROSS PAY']);
        const proratedMonthlyGross = Number((monthlyGross * workingRatio).toFixed(2));

        // Get reimbursements and other deductions
        const reimbursements = Number(employee['Reimbursements'] || 0);
        const otherDeductions = Number(employee['Other Deductions'] || 0);

        // Calculate prorated components
        const components = this.calculateComponents(monthlyGross, workingRatio);

        // Calculate pension contributions
        const pensionDetails = this.calculatePension({
            basic: components.BASIC,
            transport: components.TRANSPORT,
            housing: components.HOUSING,
            contractType: employee['Contract Type'],
            monthlyGross: proratedMonthlyGross,
            voluntaryPension: Number(employee['VOLUNTARY_PENSION'] || 0)
        });

        // Calculate adjusted gross income for CRA
        const statutoryDeductions = pensionDetails.employeePension + pensionDetails.voluntaryPension;
        const adjustedGross = proratedMonthlyGross - statutoryDeductions;

        // Calculate CRA
        const cra = this.calculateCRA(adjustedGross, 0);

        // Calculate taxable pay
        const taxablePay = Number((adjustedGross - cra).toFixed(2));

        // Calculate PAYE tax
        const payeTax = this.calculatePAYE(taxablePay);

        // Calculate total deductions and net pay
        const totalDeductions = Number((
            payeTax +
            pensionDetails.employeePension +
            pensionDetails.voluntaryPension +
            otherDeductions
        ).toFixed(2));

        const netPay = Number((
            proratedMonthlyGross - totalDeductions + reimbursements
        ).toFixed(2));

        // Calculate total tax relief
        const totalTaxRelief = Number((
            cra +
            pensionDetails.employeePension +
            pensionDetails.voluntaryPension
        ).toFixed(2));

        return {
            'Account Number': employee['Account Number'],
            'STAFF ID': employee['STAFF ID'],
            'Email': employee['Email'],
            'NAME': employee['NAME'],
            'DEPARTMENT': employee['DEPARTMENT'],
            'JOB TITLE': employee['JOB TITLE'],
            'Contract Type': employee['Contract Type'],
            'ANNUAL GROSS PAY': employee['ANNUAL GROSS PAY'],
            'MONTHLY_GROSS': monthlyGross,
            'START DATE': employee['START DATE'],
            'END DATE': employee['END DATE'],
            'WORKING_DAYS_RATIO': workingRatio,
            'PRORATED_MONTHLY_GROSS': proratedMonthlyGross,
            'COMP_BASIC': components.BASIC,
            'COMP_TRANSPORT': components.TRANSPORT,
            'COMP_HOUSING': components.HOUSING,
            'COMP_UTILITY': components.UTILITY,
            'CRA': cra,
            'MANDATORY_PENSION': pensionDetails.employeePension,
            'VOLUNTARY_PENSION': pensionDetails.voluntaryPension,
            'EMPLOYER_PENSION': pensionDetails.employerPension,
            'TAX_RELIEF': totalTaxRelief,
            'TAXABLE_PAY': taxablePay,
            'PAYE_TAX': payeTax,
            'OTHER_DEDUCTIONS': otherDeductions,
            'REIMBURSEMENTS': reimbursements,
            'TOTAL_DEDUCTIONS': totalDeductions,
            'NET_PAY': netPay
        };
    }

    /**
     * Process salary calculations for multiple employees
     * @param {Object[]} employees - Array of employee data
     * @returns {Object[]} Array of calculated salary details
     */
    processDataframe(employees) {
        return employees.map(employee => this.processEmployee(employee));
    }
}

// Make SalaryCalculator available globally
window.SalaryCalculator = SalaryCalculator;
