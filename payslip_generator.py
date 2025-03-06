from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os

class PayslipGenerator:
    def __init__(self):
        self.page_width, self.page_height = A4
        
    def _draw_header(self, c, company_info):
        """Draw company header section"""
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, 10*inch, company_info.get('name', 'Company Name'))
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, 9.7*inch, company_info.get('address', 'Company Address'))
        c.drawString(1*inch, 9.5*inch, f"RC Number: {company_info.get('rc_number', 'N/A')}")
        
    def _draw_employee_info(self, c, employee_info):
        """Draw employee information section"""
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, 8.5*inch, "Employee Information")
        c.setFont("Helvetica", 10)
        
        info_items = [
            f"Name: {employee_info.get('name', 'N/A')}",
            f"Employee ID: {employee_info.get('id', 'N/A')}",
            f"Department: {employee_info.get('department', 'N/A')}",
            f"Pay Period: {employee_info.get('pay_period', 'N/A')}"
        ]
        
        y_position = 8.2
        for item in info_items:
            c.drawString(1*inch, y_position*inch, item)
            y_position -= 0.2
            
    def _draw_salary_components(self, c, salary_data):
        """Draw earnings and deductions breakdown"""
        # Earnings Section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, 7*inch, "Earnings")
        
        y_position = 6.7
        c.setFont("Helvetica", 10)
        for item, amount in salary_data.get('earnings', {}).items():
            c.drawString(1*inch, y_position*inch, item)
            c.drawString(5*inch, y_position*inch, f"₦{amount:,.2f}")
            y_position -= 0.2
            
        # Deductions Section
        c.setFont("Helvetica-Bold", 12)
        y_position -= 0.3
        c.drawString(1*inch, y_position*inch, "Deductions")
        
        y_position -= 0.3
        c.setFont("Helvetica", 10)
        for item, amount in salary_data.get('deductions', {}).items():
            c.drawString(1*inch, y_position*inch, item)
            c.drawString(5*inch, y_position*inch, f"₦{amount:,.2f}")
            y_position -= 0.2
            
        # Net Pay
        c.setFont("Helvetica-Bold", 12)
        y_position -= 0.3
        c.drawString(1*inch, y_position*inch, "Net Pay:")
        c.drawString(5*inch, y_position*inch, f"₦{salary_data.get('net_pay', 0):,.2f}")
        
    def generate_payslip(self, employee_data, output_dir="payslips"):
        """Generate a payslip PDF for an employee"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = f"{output_dir}/{employee_data['id']}_{datetime.now().strftime('%Y%m')}_payslip.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        
        # Draw payslip sections
        self._draw_header(c, employee_data.get('company_info', {}))
        self._draw_employee_info(c, employee_data)
        self._draw_salary_components(c, employee_data.get('salary_data', {}))
        
        c.save()
        return filename
