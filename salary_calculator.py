import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict

@dataclass
class PensionDetails:
    employee_pension: float
    employer_pension: float
    voluntary_pension: float
    total_pension: float

class SalaryComponents(TypedDict):
    BASIC: float
    TRANSPORT: float
    HOUSING: float
    UTILITY: float
    MEAL: float
    CLOTHING: float

class SalaryCalculator:
    # Class constants
    EMPLOYEE_PENSION_RATE: float = 0.08
    EMPLOYER_PENSION_RATE: float = 0.10
    MINIMUM_PENSION_SALARY: float = 30000
    CRA_RATE: float = 0.20
    MINIMUM_CRA_RATE: float = 0.01
    MINIMUM_CRA_AMOUNT: float = 200000

    TAX_BANDS = [
        (300000, 0.07),
        (300000, 0.11),
        (500000, 0.15),
        (500000, 0.19),
        (1600000, 0.21),
        (float('inf'), 0.24)
    ]

    def __init__(self, components: Dict[str, float]):
        self.validate_components(components)
        self.components = components

    @staticmethod
    def validate_components(components: Dict[str, float]) -> None:
        """Validate that component percentages sum to 100%."""
        if not isinstance(components, dict):
            raise ValueError("Components must be a dictionary")
        if sum(components.values()) != 100:
            raise ValueError("Component percentages must sum to 100%")

    def calculate_monthly_gross(self, annual_gross):
        """Calculate monthly gross from annual gross."""
        return round(annual_gross / 12, 2)

    def calculate_working_days_ratio(self, start_date: str, end_date: str) -> float:
        """Calculate the ratio of weekdays worked in the month."""
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)

            if start > end:
                raise ValueError("Start date must be before end date")

            # Get the month range
            month_start = pd.Timestamp(end.year, end.month, 1)
            month_end = month_start + pd.offsets.MonthEnd(1)

            # Optimize by using business day count
            worked_weekdays = len(pd.bdate_range(start, end))
            total_weekdays = len(pd.bdate_range(month_start, month_end))

            return round(worked_weekdays / total_weekdays, 2)
        except Exception as e:
            raise ValueError(f"Error calculating working days ratio: {str(e)}")

    def calculate_components(self, monthly_gross, working_days_ratio=1):
        """Calculate individual salary components."""
        return {
            component: round((monthly_gross * (percentage / 100)) * working_days_ratio, 2)
            for component, percentage in self.components.items()
        }

    def calculate_pension(self, basic: float, transport: float, housing: float, 
                         contract_type: str, monthly_gross: float, 
                         voluntary_pension: float = 0) -> PensionDetails:
        """Calculate pension contributions after proration."""
        if not isinstance(contract_type, str):
            raise ValueError("Contract type must be a string")

        if contract_type.strip().upper() == 'CONTRACT' or monthly_gross < self.MINIMUM_PENSION_SALARY:
            return PensionDetails(0.00, 0.00, 0.00, 0.00)

        try:
            pensionable_base = basic + transport + housing
            employee_pension = round(self.EMPLOYEE_PENSION_RATE * pensionable_base, 2)
            employer_pension = round(self.EMPLOYER_PENSION_RATE * pensionable_base, 2)
            voluntary = round(voluntary_pension, 2)

            return PensionDetails(
                employee_pension=employee_pension,
                employer_pension=employer_pension,
                voluntary_pension=voluntary,
                total_pension=employee_pension + employer_pension + voluntary
            )
        except Exception as e:
            raise ValueError(f"Error calculating pension: {str(e)}")

    def calculate_cra(self, gross_pay, pension):
        """Calculate Consolidated Relief Allowance (CRA)."""
        # Gross pay after pension deduction
        gross_after_pension = gross_pay - pension

        # Calculate 20% of gross after pension
        cra_percentage = round(self.CRA_RATE * gross_after_pension, 2)

        # Calculate 1% of gross after pension and compare with monthly 200,000/12
        minimum_relief = round(max(self.MINIMUM_CRA_RATE * gross_after_pension, self.MINIMUM_CRA_AMOUNT / 12), 2)

        return round(cra_percentage + minimum_relief, 2)

    def calculate_paye(self, taxable_pay):
        """Calculate PAYE tax using progressive tax bands."""
        tax_bands = self.TAX_BANDS

        annual_taxable = taxable_pay * 12
        total_tax = 0
        remaining_income = annual_taxable

        for band, rate in tax_bands:
            if remaining_income <= 0:
                break
            taxable_in_band = min(band, remaining_income)
            total_tax += taxable_in_band * rate
            remaining_income -= band

        return round(total_tax / 12, 2)

    def process_employee(self, row):
        """Process salary calculations for a single employee."""
        # Calculate working days ratio
        working_ratio = self.calculate_working_days_ratio(row['START DATE'], row['END DATE'])

        # Calculate prorated monthly gross
        monthly_gross = self.calculate_monthly_gross(row['ANNUAL GROSS PAY'])
        prorated_monthly_gross = round(monthly_gross * working_ratio, 2)

        # Get reimbursements and other deductions
        reimbursements = float(row.get('Reimbursements', 0))
        other_deductions = float(row.get('Other Deductions', 0))

        # Calculate prorated components
        components = self.calculate_components(monthly_gross, working_ratio)

        # Calculate pension contributions
        pension_details = self.calculate_pension(
            components['BASIC'],
            components['TRANSPORT'],
            components['HOUSING'],
            row['Contract Type'],
            prorated_monthly_gross,
            float(row.get('VOLUNTARY_PENSION', 0))
        )

        # Calculate adjusted gross income for CRA
        statutory_deductions = pension_details.employee_pension + pension_details.voluntary_pension
        adjusted_gross = prorated_monthly_gross - statutory_deductions

        # Calculate CRA using adjusted gross income
        cra = self.calculate_cra(adjusted_gross, 0)  # Pension already deducted from gross

        # Calculate taxable pay
        taxable_pay = round(adjusted_gross - cra, 2)

        # Calculate PAYE tax
        paye_tax = self.calculate_paye(taxable_pay)

        # Calculate total deductions and net pay
        total_deductions = round(
            paye_tax + 
            pension_details.employee_pension + 
            pension_details.voluntary_pension + 
            other_deductions, 2
        )
        net_pay = round(prorated_monthly_gross - total_deductions + reimbursements, 2)

        # Calculate total tax relief (sum of all tax-deductible amounts)
        total_tax_relief = round(cra + pension_details.employee_pension + pension_details.voluntary_pension, 2)

        ordered_result = {
            'Account Number': row['Account Number'],
            'STAFF ID': row['STAFF ID'],
            'Email': row['Email'],
            'NAME': row['NAME'],
            'DEPARTMENT': row['DEPARTMENT'],
            'JOB TITLE': row['JOB TITLE'],
            'Contract Type': row['Contract Type'],
            'ANNUAL GROSS PAY': row['ANNUAL GROSS PAY'],
            'MONTHLY_GROSS': monthly_gross,
            'START DATE': row['START DATE'],
            'END DATE': row['END DATE'],
            'WORKING_DAYS_RATIO': working_ratio,
            'PRORATED_MONTHLY_GROSS': prorated_monthly_gross,
            'COMP_BASIC': components['BASIC'],
            'COMP_TRANSPORT': components['TRANSPORT'],
            'COMP_HOUSING': components['HOUSING'],
            'COMP_UTILITY': components['UTILITY'],
            'COMP_MEAL': components['MEAL'],
            'COMP_CLOTHING': components['CLOTHING'],
            'CRA': cra,
            'MANDATORY_PENSION': pension_details.employee_pension,
            'VOLUNTARY_PENSION': pension_details.voluntary_pension,
            'EMPLOYER_PENSION': pension_details.employer_pension,
            'TAX_RELIEF': total_tax_relief,
            'TAXABLE_PAY': taxable_pay,
            'PAYE_TAX': paye_tax,
            'OTHER_DEDUCTIONS': other_deductions,
            'REIMBURSEMENTS': reimbursements,
            'TOTAL_DEDUCTIONS': total_deductions,
            'NET_PAY': net_pay
        }
        return ordered_result

    def process_dataframe(self, df):
        """Process entire dataframe of employees."""
        results = []
        for _, row in df.iterrows():
            results.append(self.process_employee(row.to_dict()))
        return pd.DataFrame(results)

