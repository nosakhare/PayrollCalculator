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

    def calculate_pension(self, basic, transport, housing, contract_type):
        """Calculate employee pension contribution based on contract type."""
        if contract_type.strip().upper() == 'CONTRACT':
            return 0.00
        return round(0.08 * (basic + transport + housing), 2)

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

        # Apply reimbursements and other deductions
        reimbursements = float(row.get('Reimbursements', 0))
        other_deductions = float(row.get('Other Deductions', 0))
        adjusted_monthly_gross = round(prorated_monthly_gross - reimbursements - other_deductions, 2)

        # Calculate prorated components
        components = self.calculate_components(monthly_gross, working_ratio)

        # Calculate pension based on contract type
        pension = self.calculate_pension(
            components['BASIC'],
            components['TRANSPORT'],
            components['HOUSING'],
            row['Contract Type']
        )

        # Calculate CRA using adjusted gross and pension
        cra = self.calculate_cra(adjusted_monthly_gross, pension)

        # Calculate taxable pay
        taxable_pay = round(adjusted_monthly_gross - cra - pension, 2)

        # Calculate PAYE tax
        paye_tax = self.calculate_paye(taxable_pay)

        # Calculate total deductions and net pay
        total_deductions = round(paye_tax + pension + other_deductions, 2)
        net_pay = round(prorated_monthly_gross - total_deductions + reimbursements, 2)

        return {
            **row,
            'WORKING_DAYS_RATIO': working_ratio,
            'MONTHLY_GROSS': monthly_gross,
            'PRORATED_MONTHLY_GROSS': prorated_monthly_gross,
            'REIMBURSEMENTS': reimbursements,
            'OTHER_DEDUCTIONS': other_deductions,
            'ADJUSTED_MONTHLY_GROSS': adjusted_monthly_gross,
            **{f'COMP_{k}': v for k, v in components.items()},
            'CRA': cra,
            'PENSION': pension,
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