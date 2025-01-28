import pandas as pd
import numpy as np
from datetime import datetime

class SalaryCalculator:
    def __init__(self, components):
        self.components = components
        
    def calculate_monthly_gross(self, annual_gross):
        """Calculate monthly gross from annual gross."""
        return annual_gross / 12

    def calculate_components(self, monthly_gross):
        """Calculate individual salary components."""
        return {
            component: monthly_gross * (percentage / 100)
            for component, percentage in self.components.items()
        }

    def calculate_cra(self, gross_for_cra):
        """Calculate Consolidated Relief Allowance."""
        return (0.2 * gross_for_cra) + 200000

    def calculate_pension(self, basic, transport, housing):
        """Calculate employee pension contribution."""
        return 0.08 * (basic + transport + housing)

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
        monthly_gross = self.calculate_monthly_gross(row['ANNUAL GROSS PAY'])
        components = self.calculate_components(monthly_gross)
        
        # Calculate pension
        pension = self.calculate_pension(
            components['BASIC'],
            components['TRANSPORT'],
            components['HOUSING']
        )
        
        # Calculate CRA and taxable pay
        gross_for_cra = monthly_gross
        cra = self.calculate_cra(gross_for_cra)
        taxable_pay = gross_for_cra - cra - pension
        
        # Calculate PAYE tax
        paye_tax = self.calculate_paye(taxable_pay)
        
        # Calculate total deductions and net pay
        total_deductions = paye_tax + pension
        net_pay = monthly_gross - total_deductions
        
        return {
            **row,
            'MONTHLY_GROSS': monthly_gross,
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
