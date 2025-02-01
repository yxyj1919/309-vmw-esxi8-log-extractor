import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import jinja2
import pdfkit
import os

class ReportGenerator:
    """Generate analysis report in HTML/PDF format"""
    
    def __init__(self, log_type):
        """Initialize report generator"""
        self.log_type = log_type  # vmkernel, vmkwarning, or vobd
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir)
        )
    
    def generate_plots(self, df):
        """Generate plotly figures for the report"""
        plots = {}
        
        # Time distribution plot
        if 'Time' in df.columns:
            fig = px.histogram(df, x='Time', title='Log Distribution Over Time')
            plots['time_dist'] = fig.to_html(full_html=False)
        
        # Module distribution plot
        if 'Module' in df.columns:
            module_counts = df['Module'].value_counts()
            fig = px.bar(x=module_counts.index, y=module_counts.values,
                        title='Module Distribution')
            plots['module_dist'] = fig.to_html(full_html=False)
            
        return plots
    
    def generate_stats(self, df):
        """Generate statistics for the report"""
        stats = {
            'total_logs': len(df),
            'time_range': {
                'start': df['Time'].min().strftime('%Y-%m-%d %H:%M:%S'),
                'end': df['Time'].max().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        if 'Module' in df.columns:
            stats['module_stats'] = df['Module'].value_counts().to_dict()
            
        return stats
    
    def generate_html(self, df, filtered_df=None, category_dfs=None):
        """Generate HTML report"""
        template = self.env.get_template(f'{self.log_type}_report.html')
        
        # Generate basic statistics
        stats = self.generate_stats(df)
        plots = self.generate_plots(df)
        
        # Add filtered data statistics if available
        if filtered_df is not None:
            stats['filtered'] = self.generate_stats(filtered_df)
            plots['filtered'] = self.generate_plots(filtered_df)
        
        # Add category statistics if available
        if category_dfs:
            stats['categories'] = {}
            plots['categories'] = {}
            for category, cat_df in category_dfs.items():
                if not cat_df.empty:
                    stats['categories'][category] = self.generate_stats(cat_df)
                    plots['categories'][category] = self.generate_plots(cat_df)
        
        # Render template
        html = template.render(
            log_type=self.log_type,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            stats=stats,
            plots=plots
        )
        
        return html
    
    def generate_pdf(self, html_content, output_path):
        """Convert HTML to PDF"""
        try:
            pdfkit.from_string(html_content, output_path)
            return True
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return False 