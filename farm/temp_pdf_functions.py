# ===== PDF EXPORT VIEWS =====

@login_required
def export_animal_pdf(request, animal_id):
    """Export individual animal data to PDF"""
    animal = get_object_or_404(Animal, id=animal_id)

    # Get recent mortality and activity data
    recent_mortality = Mortality.objects.filter(animal=animal).order_by('-date')[:10]
    activities = ActivityLog.objects.filter(animal=animal).exclude(activity_type='egg_collection').order_by('-date', '-time')[:20]

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{animal.name}_report.pdf"'

    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    elements.append(Paragraph(f"Animal Report - {animal.name}", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Animal Overview
    elements.append(Paragraph("Animal Overview", styles['Heading2']))
    overview_data = [
        ['Animal Type', animal.get_category_display()],
        ['Total Count', str(animal.total_count)],
        ['Created', animal.created_at.strftime('%Y-%m-%d')],
    ]
    overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 20))

    # Recent Mortality
    elements.append(Paragraph("Recent Mortality Records", styles['Heading2']))
    if recent_mortality:
        mortality_data = [['Date', 'Count', 'Reason', 'Reported By']]
        for mortality in recent_mortality:
            mortality_data.append([
                mortality.date.strftime('%Y-%m-%d'),
                str(mortality.count),
                mortality.reason or 'N/A',
                mortality.reported_by.get_full_name() if mortality.reported_by else 'N/A'
            ])
        mortality_table = Table(mortality_data, colWidths=[1.5*inch, 1*inch, 2.5*inch, 2*inch])
        mortality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(mortality_table)
    else:
        elements.append(Paragraph("No mortality records found.", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Activity History
    elements.append(Paragraph("Activity History", styles['Heading2']))
    if activities:
        activity_data = [['Date', 'Time', 'Activity Type', 'Details', 'Recorded By']]
        for activity in activities:
            detail = activity.notes or f"{activity.quantity or ''} {activity.unit or ''}".strip() or 'N/A'
            activity_data.append([
                activity.date.strftime('%Y-%m-%d'),
                activity.time.strftime('%H:%M'),
                activity.get_activity_type_display(),
                detail,
                activity.employee.name or activity.employee.user.username
            ])
        activity_table = Table(activity_data, colWidths=[1.2*inch, 0.8*inch, 1.5*inch, 2*inch, 1.5*inch])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(activity_table)
    else:
        elements.append(Paragraph("No activity records found.", styles['Normal']))

    doc.build(elements)
    return response

@login_required
def export_feed_pdf(request):
    """Export feed inventory to PDF"""
    feeds = Feed.objects.all().order_by('name')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="feed_inventory_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    elements.append(Paragraph("Feed Inventory Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    if feeds:
        feed_data = [['Feed Name', 'Type', 'Current Stock', 'Unit', 'Status']]
        for feed in feeds:
            status = "Low Stock" if feed.current_stock <= feed.low_stock_threshold else "Normal"
            feed_data.append([
                feed.name,
                feed.type,
                f"{feed.current_stock}",
                feed.unit,
                status
            ])

        feed_table = Table(feed_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch, 1*inch])
        feed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(feed_table)
    else:
        elements.append(Paragraph("No feed records found.", styles['Normal']))

    doc.build(elements)
    return response

@login_required
def export_mortality_pdf(request):
    """Export mortality records to PDF"""
    mortality_records = Mortality.objects.select_related('animal', 'reported_by').order_by('-date')[:50]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mortality_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    elements.append(Paragraph("Mortality Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    if mortality_records:
        mortality_data = [['Date', 'Animal', 'Count', 'Reason', 'Reported By']]
        for record in mortality_records:
            mortality_data.append([
                record.date.strftime('%Y-%m-%d'),
                record.animal.name,
                str(record.count),
                record.reason or 'N/A',
                record.reported_by.get_full_name() if record.reported_by else 'N/A'
            ])

        mortality_table = Table(mortality_data, colWidths=[1.2*inch, 2*inch, 0.8*inch, 2.5*inch, 1.5*inch])
        mortality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(mortality_table)
    else:
        elements.append(Paragraph("No mortality records found.", styles['Normal']))

    doc.build(elements)
    return response

@login_required
def export_activity_pdf(request):
    """Export activity summary to PDF"""
    activities = ActivityLog.objects.select_related('animal', 'employee').order_by('-date', '-time')[:50]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="activity_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    elements.append(Paragraph("Activity Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    if activities:
        activity_data = [['Date', 'Time', 'Animal', 'Activity Type', 'Details', 'Employee']]
        for activity in activities:
            detail = activity.notes or f"{activity.quantity or ''} {activity.unit or ''}".strip() or 'N/A'
            activity_data.append([
                activity.date.strftime('%Y-%m-%d'),
                activity.time.strftime('%H:%M'),
                activity.animal.name if activity.animal else 'N/A',
                activity.get_activity_type_display(),
                detail,
                activity.employee.name or activity.employee.user.username
            ])

        activity_table = Table(activity_data, colWidths=[1*inch, 0.8*inch, 1.5*inch, 1.5*inch, 2*inch, 1.2*inch])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(activity_table)
    else:
        elements.append(Paragraph("No activity records found.", styles['Normal']))

    doc.build(elements)
    return response

@login_required
def export_reports_pdf(request):
    """Export comprehensive system reports to PDF"""
    # Get summary data
    total_animals = Animal.objects.aggregate(total=Sum('total_count'))['total'] or 0
    total_feeds = Feed.objects.aggregate(total=Sum('current_stock'))['total'] or 0
    recent_mortality = Mortality.objects.filter(date__gte=timezone.now().date() - timedelta(days=30)).aggregate(total=Sum('count'))['total'] or 0
    recent_activities = ActivityLog.objects.filter(date__gte=timezone.now().date() - timedelta(days=30)).count()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="system_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    elements.append(Paragraph("Farm Management System Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # System Overview
    elements.append(Paragraph("System Overview (Last 30 Days)", styles['Heading2']))
    overview_data = [
        ['Total Animals', str(total_animals)],
        ['Total Feed Stock', f"{total_feeds} kg"],
        ['Recent Mortality', str(recent_mortality)],
        ['Recent Activities', str(recent_activities)],
    ]
    overview_table = Table(overview_data, colWidths=[3*inch, 3*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 20))

    # Animals by Category
    elements.append(Paragraph("Animals by Category", styles['Heading2']))
    animal_categories = Animal.objects.values('category').annotate(total=Sum('total_count')).order_by('category')
    if animal_categories:
        category_data = [['Category', 'Total Count']]
        for category in animal_categories:
            category_data.append([
                dict(Animal.CATEGORY_CHOICES)[category['category']],
                str(category['total'])
            ])
        category_table = Table(category_data, colWidths=[3*inch, 3*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(category_table)
    else:
        elements.append(Paragraph("No animal records found.", styles['Normal']))

    doc.build(elements)
    return response