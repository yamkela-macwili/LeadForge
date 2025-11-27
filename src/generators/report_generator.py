from fpdf import FPDF
import pandas as pd
import os

class ReportGenerator:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_pdf(self, data, title="Lead Report"):
        """
        Generates a PDF report from the data.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Title
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, txt=title, ln=True, align='C')
        pdf.ln(10)
        
        # Table Header
        pdf.set_font("Arial", style="B", size=10)
        col_width = 40
        headers = ["Name", "Agency", "Area", "Phone"]
        
        for header in headers:
            pdf.cell(col_width, 10, header, border=1)
        pdf.ln()
        
        # Table Data
        pdf.set_font("Arial", size=10)
        if isinstance(data, pd.DataFrame):
            records = data.to_dict('records')
        else:
            records = data

        for row in records:
            pdf.cell(col_width, 10, str(row.get("name", "")), border=1)
            pdf.cell(col_width, 10, str(row.get("agency", "")), border=1)
            pdf.cell(col_width, 10, str(row.get("area", "")), border=1)
            pdf.cell(col_width, 10, str(row.get("phone", "")), border=1)
            pdf.ln()
            
        output_path = os.path.join(self.output_dir, f"{title.replace(' ', '_')}.pdf")
        pdf.output(output_path)
        print(f"PDF Report generated: {output_path}")
        return output_path

    def generate_excel(self, data, filename="leads.xlsx"):
        """
        Generates an Excel report.
        """
        output_path = os.path.join(self.output_dir, filename)
        if isinstance(data, pd.DataFrame):
            data.to_excel(output_path, index=False)
        else:
            pd.DataFrame(data).to_excel(output_path, index=False)
        print(f"Excel Report generated: {output_path}")
        return output_path
