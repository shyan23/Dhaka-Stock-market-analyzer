import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import plotly.io as pio

class ExportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def export_transactions_to_csv(self, transactions: List[Any]) -> bytes:
        """Export transactions to CSV format"""
        data = []
        for transaction in transactions:
            data.append({
                'ID': transaction.id,
                'Symbol': transaction.symbol,
                'Type': transaction.transaction_type.value,
                'Quantity': transaction.quantity,
                'Price': transaction.price,
                'Total Amount': transaction.total_amount,
                'Timestamp': transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Notes': transaction.notes or ''
            })

        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')

    def export_portfolio_to_csv(self, portfolio_items: Dict[str, Any]) -> bytes:
        """Export portfolio to CSV format"""
        data = []
        for symbol, item in portfolio_items.items():
            if item.quantity > 0:
                data.append({
                    'Symbol': item.symbol,
                    'Quantity': item.quantity,
                    'Average Cost': item.average_cost,
                    'Current Price': item.current_price,
                    'Total Cost': item.total_cost,
                    'Current Value': item.current_value,
                    'Gain/Loss': item.gain_loss,
                    'Gain/Loss %': f"{item.gain_loss_percent:.2f}%",
                    'Last Updated': item.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                })

        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')

    def export_stock_data_to_csv(self, stocks: List[Any]) -> bytes:
        """Export stock data to CSV format"""
        data = []
        for stock in stocks:
            data.append({
                'Symbol': stock.symbol,
                'Name': stock.name,
                'Current Price': stock.current_price,
                'Previous Close': stock.previous_close,
                'Price Change': stock.price_change,
                'Price Change %': f"{stock.price_change_percent:.2f}%",
                'Volume': stock.volume,
                'High': stock.high or '',
                'Low': stock.low or '',
                'Open': stock.open_price or '',
                'Last Updated': stock.last_updated.strftime('%Y-%m-%d %H:%M:%S') if stock.last_updated else ''
            })

        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')

    def export_to_excel(self, data_dict: Dict[str, pd.DataFrame]) -> bytes:
        """Export multiple sheets to Excel format"""
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            for sheet_name, df in data_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        buffer.seek(0)
        return buffer.getvalue()

    def generate_portfolio_report_pdf(self,
                                    portfolio_items: Dict[str, Any],
                                    transactions: List[Any],
                                    total_value: float,
                                    total_cost: float,
                                    total_gain_loss: float) -> bytes:
        """Generate comprehensive portfolio PDF report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=1,  # Center alignment
            spaceAfter=30
        )
        elements.append(Paragraph("Portfolio Report", title_style))
        elements.append(Spacer(1, 12))

        # Report date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            alignment=1,  # Center alignment
            fontSize=12,
            spaceAfter=20
        )
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
        elements.append(Spacer(1, 12))

        # Portfolio Summary
        summary_style = ParagraphStyle(
            'SummaryStyle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.darkgreen,
            spaceAfter=12
        )
        elements.append(Paragraph("Portfolio Summary", summary_style))

        summary_data = [
            ['Metric', 'Value'],
            ['Total Portfolio Value', f"৳{total_value:,.2f}"],
            ['Total Cost Basis', f"৳{total_cost:,.2f}"],
            ['Total Gain/Loss', f"৳{total_gain_loss:,.2f}"],
            ['Total Gain/Loss %', f"{(total_gain_loss/total_cost*100) if total_cost > 0 else 0:.2f}%"],
            ['Number of Holdings', str(len([item for item in portfolio_items.values() if item.quantity > 0]))],
            ['Number of Transactions', str(len(transactions))]
        ]

        summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 24))

        # Portfolio Holdings
        elements.append(Paragraph("Current Holdings", summary_style))

        holdings_data = [['Symbol', 'Quantity', 'Avg Cost', 'Current Price', 'Market Value', 'Gain/Loss', 'Gain/Loss %']]

        for symbol, item in portfolio_items.items():
            if item.quantity > 0:
                holdings_data.append([
                    item.symbol,
                    str(item.quantity),
                    f"৳{item.average_cost:.2f}",
                    f"৳{item.current_price:.2f}",
                    f"৳{item.current_value:.2f}",
                    f"৳{item.gain_loss:.2f}",
                    f"{item.gain_loss_percent:.2f}%"
                ])

        holdings_table = Table(holdings_data, colWidths=[0.8*inch, 0.8*inch, 1*inch, 1*inch, 1.2*inch, 1*inch, 1*inch])
        holdings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        elements.append(holdings_table)
        elements.append(Spacer(1, 24))

        # Recent Transactions
        elements.append(Paragraph("Recent Transactions (Last 10)", summary_style))

        recent_transactions = sorted(transactions, key=lambda x: x.timestamp, reverse=True)[:10]
        trans_data = [['Date', 'Symbol', 'Type', 'Quantity', 'Price', 'Total']]

        for trans in recent_transactions:
            trans_data.append([
                trans.timestamp.strftime('%Y-%m-%d'),
                trans.symbol,
                trans.transaction_type.value,
                str(trans.quantity),
                f"৳{trans.price:.2f}",
                f"৳{trans.total_amount:.2f}"
            ])

        trans_table = Table(trans_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 1.2*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        elements.append(trans_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()