from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os

class PayslipGenerator:
    def __init__(self):
        self.page_width, self.page_height = A4

    def _draw_header(self, c, employee_info):
        """Draw employee information header section"""
        # Employee Info - Left side
        c.setFont("Helvetica", 10)
        y_start = 10.5

        left_info = [
            ("Employee Name", employee_info.get('name', 'N/A')),
            ("Company", employee_info.get('company_info', {}).get('name', 'N/A')),
            ("Payment Date", datetime.now().strftime('%m/%d/%Y')),
        ]

        for label, value in left_info:
            c.drawString(1*inch, y_start*inch, f"{label}")
            c.drawString(2.5*inch, y_start*inch, value)
            y_start -= 0.3

        # Right side info
        y_start = 10.5
        right_info = [
            ("Job Description", employee_info.get('department', 'N/A')),
            ("Staff ID", employee_info.get('id', 'N/A')),
            ("Pay Period", f"{datetime.now().strftime('%m/01/%Y')} - {datetime.now().strftime('%m/%d/%Y')}")
        ]

        for label, value in right_info:
            c.drawString(4.5*inch, y_start*inch, f"{label}")
            c.drawString(6*inch, y_start*inch, value)
            y_start -= 0.3

    def _format_currency(self, amount):
        """Format amount in Nigerian Naira"""
        return f"₦{amount:,.2f}"

    def _draw_salary_components(self, c, salary_data):
        """Draw earnings and deductions breakdown"""
        # Earnings Section
        y_start = 9

        # Earnings table
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_start*inch, "Earnings")
        c.drawString(6*inch, y_start*inch, "Amount")

        # Draw earnings items
        c.setFont("Helvetica", 10)
        y_pos = y_start - 0.4

        # Define the order of earnings components
        earnings_order = ['Basic', 'Housing', 'Transport', 'Utility', 'Meal', 'Clothing']

        # Draw each earning component in order
        for item in earnings_order:
            amount = salary_data.get('earnings', {}).get(f'{item} Salary' if item == 'Basic' else item, 0)
            c.drawString(1*inch, y_pos*inch, item)
            c.drawString(6*inch, y_pos*inch, self._format_currency(amount))
            y_pos -= 0.3

        # No salary add-ons message
        y_pos -= 0.3
        c.setFillColorRGB(0.5, 0.5, 0.5)  # Gray color
        c.drawString(1*inch, y_pos*inch, "No salary add-ons this month.")
        c.setFillColorRGB(0, 0, 0)  # Reset to black

        # Total Earnings
        y_pos -= 0.4
        total_earnings = sum(salary_data.get('earnings', {}).values())
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_pos*inch, "Total Earnings (Gross)")
        c.drawString(6*inch, y_pos*inch, self._format_currency(total_earnings))

        # Statutory Deductions
        y_pos -= 0.6
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_pos*inch, "Statutory Deductions")
        c.drawString(6*inch, y_pos*inch, "Amount")

        # Draw statutory deductions
        c.setFont("Helvetica", 10)
        y_pos -= 0.4
        statutory_deductions = {
            'Pension': salary_data.get('deductions', {}).get('Pension', 0),
            'PAYE (Tax)': salary_data.get('deductions', {}).get('PAYE Tax', 0)
        }

        for item, amount in statutory_deductions.items():
            c.drawString(1*inch, y_pos*inch, item)
            c.drawString(6*inch, y_pos*inch, self._format_currency(amount))
            y_pos -= 0.3

        # Salary Deduction section
        y_pos -= 0.4
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_pos*inch, "Salary Deduction")
        c.drawString(6*inch, y_pos*inch, "Amount")

        # Other deductions
        c.setFont("Helvetica", 10)
        y_pos -= 0.4
        other_deductions = salary_data.get('deductions', {}).get('Other Deductions', 0)
        c.drawString(1*inch, y_pos*inch, "Other Deductions")
        c.drawString(6*inch, y_pos*inch, self._format_currency(other_deductions))

        # Total Deductions
        y_pos -= 0.5
        total_deductions = sum(salary_data.get('deductions', {}).values())
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y_pos*inch, "Total Deductions")
        c.drawString(6*inch, y_pos*inch, self._format_currency(total_deductions))

        # Final Net Pay in purple box
        y_pos -= 0.8
        c.setFillColorRGB(0.4, 0, 0.6)  # Purple color
        c.rect(0.9*inch, (y_pos-0.2)*inch, 6.2*inch, 0.5*inch, fill=1)
        c.setFillColorRGB(1, 1, 1)  # White text
        c.drawString(1*inch, y_pos*inch, "Salary Payout for September")
        c.drawString(6*inch, y_pos*inch, self._format_currency(salary_data.get('net_pay', 0)))

        # Formula explanation
        y_pos -= 0.5
        c.setFillColorRGB(0, 0, 0)  # Reset to black
        c.setFont("Helvetica", 8)
        c.drawString(1*inch, y_pos*inch, "Salary Payout = Total Earnings (Gross) - Total Deductions")

    def generate_payslip(self, employee_data, output_dir="payslips"):
        """Generate a payslip PDF for an employee"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = f"{output_dir}/{employee_data['id']}_{datetime.now().strftime('%Y%m')}_payslip.pdf"
        c = canvas.Canvas(filename, pagesize=A4)

        # Draw payslip sections
        self._draw_header(c, employee_data)
        self._draw_salary_components(c, employee_data.get('salary_data', {}))

        c.save()
        return filename