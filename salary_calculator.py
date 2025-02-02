import pandas as pd
import numpy as np
from datetime import datetime

class SalaryCalculator:
    def __init__(self, components):
        self.components = components

    def calculate_monthly_gross(self, annual_gross):
        """Calculate monthly gross from annual gross."""
        return round(annual_gross / 12, 2)

    def calculate_working_days_ratio(self, start_date, end_date):
        """Calculate the ratio of weekdays worked in the month."""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        # Get the month range
        month_start = pd.Timestamp(end.year, end.month, 1)
        month_end = month_start + pd.offsets.MonthEnd(1)

        # Create date ranges for worked days and total month days
        worked_days_range = pd.date_range(start=start, end=end)
        month_days_range = pd.date_range(start=month_start, end=month_end)

        # Count weekdays (Monday = 0, Sunday = 6)
        worked_weekdays = len([d for d in worked_days_range if d.weekday() < 5])
        total_weekdays = len([d for d in month_days_range if d.weekday() < 5])

        return round(worked_weekdays / total_weekdays, 2)

    def calculate_components(self, monthly_gross, working_days_ratio=1):
        """Calculate individual salary components."""
        return {
            component: round((monthly_gross * (percentage / 100)) * working_days_ratio, 2)
            for component, percentage in self.components.items()
        }

    def calculate_pension(self, basic, transport, housing, contract_type, monthly_gross, employer_rate=10, voluntary_pension=0):
        """Calculate pension contributions."""
        if contract_type.strip().upper() == 'CONTRACT' or monthly_gross < 30000:
            return {
                'employee_pension': 0.00,
                'employer_pension': 0.00,
                'voluntary_pension': 0.00
            }
        
        pensionable_base = basic + transport + housing
        employee_pension = round(0.08 * pensionable_base, 2)
        employer_pension = round((employer_rate / 100) * pensionable_base, 2)
        
        return {
            'employee_pension': employee_pension,
            'employer_pension': employer_pension,
            'voluntary_pension': round(voluntary_pension, 2)
        }

    def calculate_cra(self, gross_pay, pension):
        """Calculate Consolidated Relief Allowance (CRA)."""
        # Gross pay after pension deduction
        gross_after_pension = gross_pay - pension

        # Calculate 20% of gross after pension
        cra_percentage = round(0.2 * gross_after_pension, 2)

        # Calculate 1% of gross after pension and compare with monthly 200,000/12
        minimum_relief = round(max(0.01 * gross_after_pension, 200000 / 12), 2)

        return round(cra_percentage + minimum_relief, 2)

    def calculate_paye(self, taxable_pay):
        """Calculate PAYE tax using progressive tax bands."""
        tax_bands = [
            (300000, 0.07),
            (300000, 0.11),
            (500000, 0.15),
            (500000, 0.19),
            (1600000, 0.21),
            (float('inf'), 0.24)
        ]

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
            float(row.get('EMPLOYER_PENSION_RATE', 10)),
            float(row.get('VOLUNTARY_PENSION', 0))
        )

        # Calculate CRA using gross pay and mandatory pension
        total_mandatory_pension = pension_details['employee_pension']
        cra = self.calculate_cra(prorated_monthly_gross, total_mandatory_pension)

        # Calculate taxable pay (before other deductions)
        taxable_pay = round(prorated_monthly_gross - cra - pension_details['employee_pension'], 2)

        # Calculate PAYE tax
        paye_tax = self.calculate_paye(taxable_pay)

        # Calculate total deductions and net pay
        total_deductions = round(
            paye_tax + 
            pension_details['employee_pension'] + 
            pension_details['voluntary_pension'] + 
            other_deductions, 2
        )
        net_pay = round(prorated_monthly_gross - total_deductions + reimbursements, 2)

        return {
            **row,
            'WORKING_DAYS_RATIO': working_ratio,
            'MONTHLY_GROSS': monthly_gross,
            'PRORATED_MONTHLY_GROSS': prorated_monthly_gross,
            'REIMBURSEMENTS': reimbursements,
            'OTHER_DEDUCTIONS': other_deductions,
            **{f'COMP_{k}': v for k, v in components.items()},
            'CRA': cra,
            'MANDATORY_PENSION': pension_details['employee_pension'],
            'EMPLOYER_PENSION': pension_details['employer_pension'],
            'VOLUNTARY_PENSION': pension_details['voluntary_pension'],
            'TAXABLE_PAY': taxable_pay,
            'PAYE_TAX': paye_tax,
            'TOTAL_DEDUCTIONS': total_deductions,
            'NET_PAY': net_pay
        }

    def process_dataframe(self, df):
        """Process entire dataframe of employees."""
        results = []
        for _, row in df.iterrows():
            results.append(self.process_employee(row.to_dict()))
        return pd.DataFrame(results)