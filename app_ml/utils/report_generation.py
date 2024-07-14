import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter,landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib
matplotlib.use('agg')  # Configurar matplotlib para utilizar el backend 'agg'
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.units import inch
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer

def generate_report(results, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='CenteredTitle', parent=styles['Heading1'], alignment=1)
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    elements.append(Paragraph("Informe comparativo de aprendizaje automático", title_style))
    elements.append(Paragraph(f"Reporte generado el {now}", normal_style))

    for algorithm, metrics in results.items():
        elements.append(Paragraph(f"Results for {algorithm}", subtitle_style))
        
        data = [
            ["Metric", "Value"],
            ["Accuracy", f"{metrics['accuracy']:.4f}"],
            ["Precision", f"{metrics['precision']:.4f}"],
            ["Recall", f"{metrics['recall']:.4f}"],
            ["F1 Score", f"{metrics['f1_score']:.4f}"],
            ["AUC", f"{metrics['auc']:.4f}"],
            ["Uso CPU", f"{metrics['cpu_usage']:.2f}%"],
            ["Tiempo Ejecución", f"{metrics['execution_time']:.2f} seconds"]
        ]

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

    doc.build(elements)


def generate_comparison_report(results, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=landscape(letter))
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='CenteredTitle', parent=styles['Heading1'], alignment=1)
    subtitle_style = ParagraphStyle(name='CenteredSubtitle', parent=styles['Heading2'], alignment=1)
    normal_style = styles['Normal']

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    elements.append(Paragraph("Comparación de algoritmos de aprendizaje automático", title_style))
    elements.append(Paragraph(f"Reporte generado el {now}", normal_style))
    elements.append(Spacer(1, 20))

    # Tabla de comparación general (vertical)
    elements.append(Paragraph("Tabla 1", subtitle_style))
    elements.append(Paragraph("Comparación de métricas entre algoritmos", subtitle_style))
    elements.append(Spacer(1, 10))

    metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC', 'Uso CPU', 'Tiempo E.']
    data = [['Algoritmo'] + metrics]
    
    for algorithm in results:
        row = [algorithm]
        for metric in metrics:
            key = metric.lower().replace(' ', '_')
            if key == 'uso_cpu':
                key = 'cpu_usage'
            elif key == 'tiempo_e.':
                key = 'execution_time'
            value = results[algorithm][key]
            if metric in ['Uso CPU', 'Tiempo E.']:
                row.append(f"{value:.2f}{'%' if metric == 'Uso CPU' else 's'}")
            else:
                row.append(f"{value:.4f}")
        data.append(row)

    table = Table(data)
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Tablas individuales para cada algoritmo (horizontales con una sola fila)
    for i, (algorithm, metrics) in enumerate(results.items(), start=2):
        elements.append(Paragraph(f"Tabla {i}", subtitle_style))
        elements.append(Paragraph(f"Resultados para {algorithm}", subtitle_style))
        elements.append(Spacer(1, 10))
        
        data = [
            ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC', 'Uso CPU', 'Tiempo E.'],
            [f"{metrics['accuracy']:.4f}", f"{metrics['precision']:.4f}", f"{metrics['recall']:.4f}",
             f"{metrics['f1_score']:.4f}", f"{metrics['auc']:.4f}", f"{metrics['cpu_usage']:.2f}%",
             f"{metrics['execution_time']:.2f}s"]
        ]

        table = Table(data)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

    # Gráficos comparativos
    metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc', 'cpu_usage', 'execution_time']
    
    for metric in metrics:
        plt.figure(figsize=(8, 4))
        algorithms = list(results.keys())
        values = [results[alg][metric] for alg in algorithms]
        
        bars = plt.bar(algorithms, values)
        plt.title(f'Comparación de {metric.replace("_", " ").title()}')
        plt.xlabel('Algoritmos')
        plt.ylabel(metric.replace("_", " ").title())
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        for bar, value in zip(bars, values):
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, f'{value:.4f}', ha='center', va='bottom')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        img = Image(buf)
        img.drawHeight = 300
        img.drawWidth = 500
        elements.append(img)
        elements.append(Spacer(1, 20))
        
        plt.close()

    # Análisis del mejor algoritmo
    best_algorithm = max(results, key=lambda x: results[x]['f1_score'])
    best_metrics = results[best_algorithm]

    elements.append(Paragraph("Análisis del mejor algoritmo", subtitle_style))
    analysis = f"""
    Basado en los resultados obtenidos, el mejor algoritmo es {best_algorithm} con los siguientes resultados:
    
    - Accuracy: {best_metrics['accuracy']:.4f}
    - Precision: {best_metrics['precision']:.4f}
    - Recall: {best_metrics['recall']:.4f}
    - F1 Score: {best_metrics['f1_score']:.4f}
    - AUC: {best_metrics['auc']:.4f}
    - Uso de CPU: {best_metrics['cpu_usage']:.2f}%
    - Tiempo de ejecución: {best_metrics['execution_time']:.2f} segundos

    Este algoritmo ha demostrado el mejor rendimiento general, con un F1 Score de {best_metrics['f1_score']:.4f}, 
    lo que indica un buen equilibrio entre precisión y exhaustividad. 
    Además, su tiempo de ejecución y uso de CPU son {best_metrics['execution_time']:.2f} segundos y {best_metrics['cpu_usage']:.2f}% respectivamente, 
    lo que sugiere una buena eficiencia computacional.
    """
    elements.append(Paragraph(analysis, normal_style))

    doc.build(elements)