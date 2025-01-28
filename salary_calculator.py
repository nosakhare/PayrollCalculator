import pandas as pd
import numpy as np
from datetime import datetime

class SalaryCalculator:
    def __init__(self, components):
        self.components = components

    def calculate_monthly_gross(self, annual_gross):
        """Calculate monthly gross from annual gross."""
        return annual_gross / 12

    def calculate_working_days_ratio(self, start_date, end_date):
        """Calculate the ratio of days worked in the month."""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        # Get the month range
        month_start = pd.Timestamp(end.year, end.month, 1)
        month_end = month_start + pd.offsets.MonthEnd(1)

        # Calculate total days in month and days worked
        total_days = (month_end - month_start).days + 1
        worked_days = min((end - start).days + 1, total_days)

        return worked_days / total_days

    def calculate_components(self, monthly_gross, working_days_ratio=1):
        """Calculate individual salary components."""
        return {
            component: (monthly_gross * (percentage / 100)) * working_days_ratio
            for component, percentage in self.components.items()
        }

    def calculate_pension(self, basic, transport, housing):
        """Calculate employee pension contribution."""
        return 0.08 * (basic + transport + housing)

    def calculate_cra(self, gross_pay, pension):
        """Calculate Consolidated Relief Allowance (CRA)."""
        # Gross pay after pension deduction
        gross_after_pension = gross_pay - pension

        # Calculate 20% of gross after pension
        cra_percentage = 0.2 * gross_after_pension

        # Calculate 1% of gross after pension and compare with monthly 200,000/12
        minimum_relief = max(0.01 * gross_after_pension, 200000 / 12)

        return cra_percentage + minimum_relief

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

        return total_tax / 12

    def process_employee(self, row):
        """Process salary calculations for a single employee."""
        # Calculate working days ratio
        working_ratio = self.calculate_working_days_ratio(row['START DATE'], row['END DATE'])

        # Calculate prorated monthly gross
        monthly_gross = self.calculate_monthly_gross(row['ANNUAL GROSS PAY'])
        prorated_monthly_gross = monthly_gross * working_ratio

        # Calculate prorated components
        components = self.calculate_components(monthly_gross, working_ratio)

        # Calculate pension from prorated components
        pension = self.calculate_pension(
            components['BASIC'],
            components['TRANSPORT'],
            components['HOUSING']
        )

        # Calculate CRA using prorated gross and pension
        cra = self.calculate_cra(prorated_monthly_gross, pension)

        # Calculate taxable pay
        taxable_pay = prorated_monthly_gross - cra - pension

        # Calculate PAYE tax
        paye_tax = self.calculate_paye(taxable_pay)

        # Calculate total deductions and net pay
        total_deductions = paye_tax + pension
        net_pay = prorated_monthly_gross - total_deductions

        return {
            **row,
            'WORKING_DAYS_RATIO': working_ratio,
            'MONTHLY_GROSS': monthly_gross,
            'PRORATED_MONTHLY_GROSS': prorated_monthly_gross,
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