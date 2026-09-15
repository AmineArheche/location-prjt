import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
    KeepTogether,
)

from app.models.booking import Booking


def format_dt(dt: datetime) -> str:
    """Format datetime object into clean French string."""
    if not dt:
        return "-"
    return dt.strftime("%d/%m/%Y à %H:%M")


def generate_contract_pdf(booking: Booking) -> bytes:
    """
    Generates a professional styled 2-page Moroccan Rental Agreement PDF document in French.
    Returns PDF content as raw bytes stream.
    """
    buffer = io.BytesIO()

    # Document setup (A4 size with 1.5cm margins)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette (Navy, Emerald & Charcoal)
    PRIMARY = colors.HexColor("#0f172a")     # Slate 900
    SECONDARY = colors.HexColor("#0284c7")   # Sky 600
    ACCENT = colors.HexColor("#059669")      # Emerald 600
    DARK_TEXT = colors.HexColor("#1e293b")   # Slate 800
    LIGHT_BG = colors.HexColor("#f8fafc")    # Slate 50
    BORDER_COLOR = colors.HexColor("#cbd5e1")# Slate 300

    # Custom Typography Styles
    style_header_title = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
    )
    style_header_sub = ParagraphStyle(
        "HeaderSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=DARK_TEXT,
    )
    style_doc_title = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        alignment=1, # Center
        textColor=PRIMARY,
    )
    style_section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.white,
    )
    style_cell_label = ParagraphStyle(
        "CellLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=PRIMARY,
    )
    style_cell_val = ParagraphStyle(
        "CellVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=DARK_TEXT,
    )
    style_legal_title = ParagraphStyle(
        "LegalTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=PRIMARY,
    )
    style_legal_body = ParagraphStyle(
        "LegalBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=DARK_TEXT,
    )

    story = []

    # Extract Entities with Fallbacks
    agency = booking.agency
    customer = booking.customer
    vehicle = booking.vehicle

    agency_name = agency.name if agency else "AGENCE DE LOCATION DE VÉHICULES"
    agency_city = agency.city if agency else "Casablanca"
    agency_phone = agency.phone if agency else "+212 522 000 000"
    agency_rc = agency.rc_number if agency else "RC-00000"
    agency_patente = agency.patente_number if agency else "PAT-00000"

    # =========================================================================
    # PAGE 1: HEADER & CONTRACT DETAILS
    # =========================================================================

    # 1. TOP HEADER (Agency Info & Contract Ref)
    header_left = f"""
    <b>{agency_name.upper()}</b><br/>
    Siège Social: {agency_city}, Maroc<br/>
    Tél: {agency_phone} | Email: contact@{agency_name.lower().replace(' ', '')}.ma<br/>
    R.C. N°: <b>{agency_rc}</b> | Patente N°: <b>{agency_patente}</b>
    """

    booking_short_id = str(booking.id)[:8].upper()
    header_right = f"""
    <font color="#0284c7"><b>CONTRAT N°: CT-{booking_short_id}</b></font><br/>
    Date de création: <b>{datetime.now().strftime("%d/%m/%Y")}</b><br/>
    Statut: <b>{booking.status.value}</b><br/>
    Agent: <b>{booking.agent.email if booking.agent else 'Système'}</b>
    """

    header_table_data = [
        [Paragraph(header_left, style_header_sub), Paragraph(header_right, style_header_sub)]
    ]
    header_table = Table(header_table_data, colWidths=[11.5 * cm, 6.5 * cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    # 2. DOCUMENT TITLE BANNER
    story.append(Paragraph("CONTRAT DE LOCATION VÉHICULE DE TOURISME", style_doc_title))
    story.append(Spacer(1, 0.15 * inch))

    # Helper function for section headers
    def make_section_header(title_text: str) -> Table:
        t = Table([[Paragraph(title_text.upper(), style_section_heading)]], colWidths=[18 * cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return t

    # 3. SECTION 1: INFORMATIONS SUR LE CLIENT (LE LOCATAIRE)
    story.append(make_section_header("1. INFORMATIONS DU LOCATAIRE (CLIENT)"))
    cust_data = [
        [
            Paragraph("Nom & Prénom:", style_cell_label),
            Paragraph(customer.full_name if customer else "-", style_cell_val),
            Paragraph("CIN / Passeport N°:", style_cell_label),
            Paragraph(customer.cin_or_passport if customer else "-", style_cell_val),
        ],
        [
            Paragraph("Permis de Conduire N°:", style_cell_label),
            Paragraph(customer.driver_license_number if customer else "-", style_cell_val),
            Paragraph("Téléphone:", style_cell_label),
            Paragraph(customer.phone_number if customer else "-", style_cell_val),
        ],
    ]
    t_cust = Table(cust_data, colWidths=[4 * cm, 5 * cm, 4 * cm, 5 * cm])
    t_cust.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_cust)
    story.append(Spacer(1, 0.15 * inch))

    # 4. SECTION 2: INFORMATIONS SUR LE VÉHICULE
    story.append(make_section_header("2. INFORMATIONS SUR LE VÉHICULE"))
    veh_data = [
        [
            Paragraph("Marque & Modèle:", style_cell_label),
            Paragraph(vehicle.make_model if vehicle else "-", style_cell_val),
            Paragraph("Immatriculation:", style_cell_label),
            Paragraph(f"<b>{vehicle.matriculation}</b>" if vehicle else "-", style_cell_val),
        ],
        [
            Paragraph("Kilométrage Départ:", style_cell_label),
            Paragraph(f"{booking.start_mileage:,} km".replace(',', ' '), style_cell_val),
            Paragraph("Année du Véhicule:", style_cell_label),
            Paragraph(str(vehicle.year) if vehicle else "-", style_cell_val),
        ],
    ]
    t_veh = Table(veh_data, colWidths=[4 * cm, 5 * cm, 4 * cm, 5 * cm])
    t_veh.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_veh)
    story.append(Spacer(1, 0.15 * inch))

    # 5. SECTION 3: CONDITIONS & TARIFICATION DE LA LOCATION
    story.append(make_section_header("3. DUREE, TARIFICATION ET CAUTION"))
    
    # Calculate days duration
    start_dt = booking.start_datetime
    end_dt = booking.end_datetime
    duration_days = 1
    if start_dt and end_dt:
        diff_hours = (end_dt - start_dt).total_seconds() / 3600.0
        duration_days = max(1, int(round(diff_hours / 24.0)))

    daily_rate = float(booking.total_price) / duration_days if duration_days > 0 else float(booking.total_price)

    terms_data = [
        [
            Paragraph("Date & Heure Début:", style_cell_label),
            Paragraph(format_dt(start_dt), style_cell_val),
            Paragraph("Date & Heure Fin:", style_cell_label),
            Paragraph(format_dt(end_dt), style_cell_val),
        ],
        [
            Paragraph("Durée Totale:", style_cell_label),
            Paragraph(f"{duration_days} Jour(s)", style_cell_val),
            Paragraph("Tarif Journalier:", style_cell_label),
            Paragraph(f"{daily_rate:.2f} MAD / jour", style_cell_val),
        ],
        [
            Paragraph("<b>MONTANT TOTAL:</b>", style_cell_label),
            Paragraph(f"<font color='#059669'><b>{float(booking.total_price):,.2f} MAD</b></font>", style_cell_val),
            Paragraph("<b>DÉPÔT CAUTION:</b>", style_cell_label),
            Paragraph(f"<font color='#0284c7'><b>{float(booking.deposit_amount):,.2f} MAD</b></font>", style_cell_val),
        ],
    ]
    t_terms = Table(terms_data, colWidths=[4 * cm, 5 * cm, 4 * cm, 5 * cm])
    t_terms.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_terms)
    story.append(Spacer(1, 0.2 * inch))

    # Note at bottom of Page 1
    p_note = Paragraph(
        "<i>En signant ce contrat au verso, le locataire reconnaît avoir reçu le véhicule décrit ci-dessus en parfait état de marche et de propreté et s'engage à respecter l'ensemble des conditions générales énoncées à la page 2.</i>",
        style_header_sub
    )
    story.append(p_note)

    # Force PageBreak to ensure clean 2-page document structure
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CONDITIONS GENERALES DE LOCATION AU MAROC & SIGNATURES
    # =========================================================================

    story.append(Paragraph("CONDITIONS GÉNÉRALES DE LOCATION (ROYAUME DU MAROC)", style_doc_title))
    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=10))

    # Legal Clauses in French (Compliant with Moroccan Commercial Code & Highway Code Law 52-05)
    clauses = [
        ("ARTICLE 1 : UTILISATION ET CONDUITE DU VÉHICULE",
         "Le locataire s'engage à conduire le véhicule sous réserve d'être titulaire d'un permis de conduire valide depuis plus de 2 ans. "
         "Le véhicule doit être conduit exclusivement par le locataire désigné au contrat. Il est strictement interdit d'utiliser le véhicule pour le transport "
         "de marchandises dangereuses, de sous-louer le véhicule, ou de participer à des courses ou essais automobiles. "
         "Le locataire doit se conformer au Code de la Route marocain (Loi 52-05)."),

        ("ARTICLE 2 : ASSURANCE ET RESPONSABILITÉ",
         "Le véhicule est couvert par une assurance Tous Risques avec franchise réglementaire. En cas d'accident responsable ou sans tiers identifié, "
         "le locataire reste redevable du montant de la franchise stipulée. L'assurance ne couvre pas la conduite en état d'ivresse, sous l'emprise de stupéfiants, "
         "ou en cas de délit de fuite. Les dégâts matériels causés aux pneumatiques, jantes, bas de caisse et garnitures intérieures restent à la charge exclusive du locataire."),

        ("ARTICLE 3 : ENTRETIEN, PANNES ET ACCIDENTS",
         "L'usure mécanique normale est à la charge de l'agence. En cas de panne mécanique ou d'accident, le locataire doit en informer l'agence immédiatement "
         "dans un délai maximum de 24 heures et établir un constat amiable. Aucune réparation ne peut être effectuée sans l'accord préalable écrit de l'agence. "
         "Toute intervention non autorisée ne sera pas remboursée."),

        ("ARTICLE 4 : RESTITUTION DU VÉHICULE ET PÉNALITÉS",
         "Le locataire s'engage à restituer le véhicule à l'agence à la date et heure convenues au contrat. Tout retard supérieur à 2 heures non autorisé par l'agence "
         "donnera lieu à la facturation d'une journée supplémentaire au tarif de pénalité (tarif journalier majoré de 50%). Le véhicule doit être rendu avec le même niveau de carburant qu'au départ."),

        ("ARTICLE 5 : AMENDES ET CONTRAVENTIONS",
         "Le locataire est pénalement et financièrement responsable de toutes les infractions au code de la route (radars fixes/mobiles, stationnement gênant, etc.) "
         "commises pendant la période de location. L'agence communiquera l'identité du locataire aux autorités compétentes en cas de procès-verbal."),

        ("ARTICLE 6 : JURIDICTION ET LITIGES",
         "Le présent contrat est régi par le droit marocain. En cas de contestation ou de litige relatif à la validité, l'interprétation ou l'exécution du présent contrat, "
         "les Tribunaux de Commerce de la ville du siège social de l'agence sont seuls compétents."),
    ]

    for title, text in clauses:
        story.append(Paragraph(title, style_legal_title))
        story.append(Spacer(1, 0.03 * inch))
        story.append(Paragraph(text, style_legal_body))
        story.append(Spacer(1, 0.08 * inch))

    story.append(Spacer(1, 0.15 * inch))

    # BOTTOM SIGNATURE BOXES
    sig_header = Paragraph("<b>ACCEPTATION ET SIGNATURES DES PARTIES</b>", style_cell_label)
    story.append(sig_header)
    story.append(Spacer(1, 0.05 * inch))

    date_str = datetime.now().strftime("%d/%m/%Y")
    sig_left_text = f"""
    <b>LE LOUEUR (L'AGENCE)</b><br/>
    Fait à {agency_city}, le {date_str}<br/><br/>
    <i>Signature & Cachet de l'Agence:</i><br/><br/><br/><br/>
    __________________________________
    """

    sig_right_text = f"""
    <b>LE LOCATAIRE (LE CLIENT)</b><br/>
    Mention manuscrite: <i>« Lu et approuvé »</i><br/><br/>
    <i>Signature du Client:</i><br/><br/><br/><br/>
    __________________________________
    """

    sig_table_data = [
        [Paragraph(sig_left_text, style_cell_val), Paragraph(sig_right_text, style_cell_val)]
    ]
    sig_table = Table(sig_table_data, colWidths=[9 * cm, 9 * cm])
    sig_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))

    story.append(sig_table)

    # Build PDF document into buffer
    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
