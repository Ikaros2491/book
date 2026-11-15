#!/usr/bin/env python3
"""Generate ATS-optimized single-column DOCX resumes for Corey Wagner."""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def set_run_font(run, name="Calibri", size=11, bold=False, color=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def set_paragraph_spacing(paragraph, before=0, after=4, line=1.08):
    pf = paragraph.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE


def add_horizontal_line(paragraph):
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "12")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "1E3A5F")
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_heading_line(doc, text):
    p = doc.add_paragraph()
    set_paragraph_spacing(p, before=10, after=4, line=1.0)
    run = p.add_run(text.upper())
    set_run_font(run, size=11, bold=True, color=(30, 58, 95))
    add_horizontal_line(p)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    set_paragraph_spacing(p, before=0, after=2, line=1.08)
    p.clear()
    run = p.add_run(text)
    set_run_font(run, size=10.5)
    return p


def add_job_header(doc, title, dates):
    p = doc.add_paragraph()
    set_paragraph_spacing(p, before=8, after=0, line=1.05)
    run = p.add_run(title)
    set_run_font(run, size=11, bold=True)
    tab = p.add_run("\t")
    set_run_font(tab, size=10)
    # right-align dates via tab stop
    tab_stops = p.paragraph_format.tab_stops
    tab_stops.add_tab_stop(Inches(7.0), alignment=2)  # right
    run2 = p.add_run(dates)
    set_run_font(run2, size=10.5, color=(74, 85, 104))
    return p


def add_employer(doc, text):
    p = doc.add_paragraph()
    set_paragraph_spacing(p, before=0, after=2, line=1.05)
    run = p.add_run(text)
    set_run_font(run, size=10.5)
    run.italic = True
    return p


def base_doc():
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)
    return doc


def add_contact_block(doc, subtitle):
    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(name, before=0, after=2, line=1.0)
    run = name.add_run("COREY WAGNER")
    set_run_font(run, size=18, bold=True, color=(30, 58, 95))

    role = doc.add_paragraph()
    role.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(role, before=0, after=2, line=1.0)
    run = role.add_run(subtitle)
    set_run_font(run, size=11, bold=True, color=(74, 85, 104))

    contact = doc.add_paragraph()
    contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(contact, before=0, after=6, line=1.0)
    run = contact.add_run(
        "(352) 673-9027 | CoreyW2491@gmail.com | 7278 N Gibraltar Dr."
    )
    set_run_font(run, size=10.5)
    add_horizontal_line(contact)


def build_flight_attendant():
    doc = base_doc()
    add_contact_block(
        doc,
        "Executive Flight Attendant | Private Aviation Cabin Professional",
    )

    add_heading_line(doc, "Professional Summary")
    summary = doc.add_paragraph()
    set_paragraph_spacing(summary, before=2, after=4, line=1.12)
    run = summary.add_run(
        "Polished, discreet Part 121 Flight Attendant seeking a Part 91 Executive Flight Attendant "
        "role supporting company executives, principals, and high-net-worth guests. Experienced in "
        "cabin readiness, anticipatory service, catering and provisioning coordination, passenger "
        "preference awareness, and confidentiality. Calm judgment during irregular operations; "
        "effective coordination with pilots, operations, ground handlers, and vendors. Commercial "
        "Pilot and Certified Flight Instructor (CFI). CPR, First Aid, and ServSafe Food Handler. "
        "Associate of Arts in Language at Liberty University — 4.0 GPA, Dean's List."
    )
    set_run_font(run, size=10.5)

    add_heading_line(doc, "Skills")
    skills = doc.add_paragraph()
    set_paragraph_spacing(skills, before=2, after=2, line=1.12)
    run = skills.add_run(
        "Executive Flight Attendant service; Part 91 private aviation; cabin readiness and "
        "presentation; anticipatory hospitality; catering, provisioning, meals, and beverages; "
        "passenger preferences and dietary awareness; confidentiality and discretion; VIP / "
        "high-net-worth / ultra-high-net-worth client service; Federal Aviation Regulations (FAR) "
        "and safety compliance; irregular operations; coordination with pilots, dispatchers, "
        "ground handlers, and executive assistants; Microsoft Office; Windows"
    )
    set_run_font(run, size=10.5)

    add_heading_line(doc, "Certifications")
    certs = doc.add_paragraph()
    set_paragraph_spacing(certs, before=2, after=2, line=1.12)
    run = certs.add_run(
        "Part 121 Flight Attendant (American Eagle / Envoy Air); Commercial Pilot Certificate; "
        "Certified Flight Instructor (CFI); CPR; First Aid; ServSafe Food Handler; English; Spanish (A2)"
    )
    set_run_font(run, size=10.5)

    add_heading_line(doc, "Professional Experience")

    add_job_header(doc, "Flight Attendant", "August 2024 – Present")
    add_employer(doc, "American Eagle (Envoy Air)")
    for b in [
        "Ensure passenger safety, comfort, and well-being on Part 121 airline operations in accordance with company procedures and Federal Aviation Regulations (FAR).",
        "Prepare and maintain an immaculate, organized cabin environment before, during, and after each flight; manage galley readiness, catering handoffs, and service timing.",
        "Deliver professional, anticipatory service adapted to passenger needs while upholding confidentiality, grooming, and presentation standards expected in high-profile service environments.",
        "Demonstrate calm judgment and adaptability during schedule changes, delays, and irregular operations; communicate clearly with captains, operations, and passengers.",
        "Coordinate effectively with flight crew and support personnel to support efficient trip execution and on-time performance.",
    ]:
        add_bullet(doc, b)

    add_job_header(doc, "Funeral Services Associate", "February 2024 – July 2024")
    add_employer(doc, "Fero Funeral Home")
    for b in [
        "Provided discreet, high-touch service to families in sensitive situations requiring composure, empathy, confidentiality, and impeccable personal presentation.",
        "Coordinated service logistics, timing, and vendor communication under pressure — skills transferable to private aviation cabin and trip support roles.",
        "Maintained detailed follow-through on client requests and represented the organization with professionalism and discretion.",
    ]:
        add_bullet(doc, b)

    add_job_header(
        doc, "Airport Manager / Certified Flight Instructor", "January 2020 – January 2024"
    )
    add_employer(doc, "Right Rudder Aviation — Inverness, FL")
    for b in [
        "Delivered white-glove, anticipatory service for high-net-worth and ultra-high-net-worth clients, principals, and charter guests in a discreet private-aviation environment.",
        "Personally transported and escorted millionaire and high-net-worth clients; planned catering, ground transportation, and VIP staging to keep cabin and guest amenities presentation-ready.",
        "Maintained detailed awareness of client preferences and special requests; safeguarded confidential client travel and personal information.",
        "Ran day-to-day airport operations with limited supervision — hangars, ramp services, fuel restocking, facility readiness, safety oversight, and client experience.",
        "Sold and marketed multi-million-dollar Pipistrel Aircraft as the sole U.S. distributor; managed large client transactions from inquiry through closing.",
        "Managed aircraft parts ordering and inventory; coordinated aircraft and facility repairs by hiring repair crews and vendors and following work through to completion.",
        "Coordinated trip logistics with pilots, charter partners, and support personnel; applied FAA safety standards in a live flight-training and charter-support operation.",
    ]:
        add_bullet(doc, b)

    add_heading_line(doc, "Education")
    edu_items = [
        ("Liberty University — Associate of Arts, Language", "Expected Spring 2027"),
        ("GPA 4.0; Dean's List", ""),
        ("Right Rudder Aviation — Commercial Pilot Certificate; Certified Flight Instructor (CFI)", "2020 – 2024"),
        ("Penn Foster — High School Diploma", "2019"),
    ]
    for left, right in edu_items:
        p = doc.add_paragraph()
        set_paragraph_spacing(p, before=2, after=1, line=1.05)
        if right:
            tab_stops = p.paragraph_format.tab_stops
            tab_stops.add_tab_stop(Inches(7.0), alignment=2)
            run = p.add_run(left + "\t" + right)
        else:
            run = p.add_run(left)
        set_run_font(run, size=10.5)

    add_heading_line(doc, "References")
    ref = doc.add_paragraph()
    set_paragraph_spacing(ref, before=2, after=2, line=1.05)
    run = ref.add_run(
        "Charles Lawson — Chief Financial Officer (CFO), Right Rudder Aviation | (407) 734-1442 | Info@flyrra.com"
    )
    set_run_font(run, size=10.5)

    path = "/workspace/Corey_Wagner_Resume_ATS_Flight_Attendant.docx"
    doc.save(path)
    return path


def build_flight_coordinator():
    doc = base_doc()
    add_contact_block(doc, "Flight Coordinator | Aviation Operations and Trip Support")

    add_heading_line(doc, "Professional Summary")
    summary = doc.add_paragraph()
    set_paragraph_spacing(summary, before=2, after=4, line=1.12)
    run = summary.add_run(
        "Flight Coordinator–focused aviation professional with experience as a Part 121 Flight Attendant, "
        "Airport Manager, and trip-support coordinator for aircraft owners, charter customers, and "
        "high-net-worth clients. Skilled at receiving trip requests, aircraft and crew scheduling support, "
        "flight itinerary communication, crew travel arrangements, passenger services (catering and ground "
        "transportation), and confidential client preference tracking. Strong knowledge of Federal Aviation "
        "Regulations (FAR), airport operations, and safety. Microsoft Office and Windows proficient. "
        "Commercial Pilot and Certified Flight Instructor (CFI). Associate of Arts in Language at Liberty "
        "University — 4.0 GPA, Dean's List."
    )
    set_run_font(run, size=10.5)

    add_heading_line(doc, "Skills")
    skills = doc.add_paragraph()
    set_paragraph_spacing(skills, before=2, after=2, line=1.12)
    run = skills.add_run(
        "Flight coordination; aircraft scheduling support; trip requests and flight itineraries; "
        "communication with clients, client staff, flight crew, and maintenance personnel; crew travel "
        "arrangements (hotels, rental cars); passenger services (catering, ground transportation); "
        "flight following support; duty time and Federal Aviation Regulations (FAR) awareness; trip "
        "planning and feasibility analysis; client and crew contact databases / preference profiles; "
        "confidentiality; airport operations; aircraft dispatch principles; Microsoft Office; Windows; "
        "team collaboration; organization and prioritization with limited supervision"
    )
    set_run_font(run, size=10.5)

    add_heading_line(doc, "Certifications")
    certs = doc.add_paragraph()
    set_paragraph_spacing(certs, before=2, after=2, line=1.12)
    run = certs.add_run(
        "Commercial Pilot Certificate; Certified Flight Instructor (CFI); Part 121 Flight Attendant "
        "(American Eagle / Envoy Air); CPR; First Aid; ServSafe Food Handler; English; Spanish (A2)"
    )
    set_run_font(run, size=10.5)

    add_heading_line(doc, "Professional Experience")

    add_job_header(doc, "Flight Attendant", "August 2024 – Present")
    add_employer(doc, "American Eagle (Envoy Air)")
    for b in [
        "Communicate schedule and operational changes accurately to captains, operations, and passengers to keep itineraries and expectations aligned.",
        "Support aircraft trip execution with cabin readiness, catering handoffs, and service confirmation under irregular operations and time pressure.",
        "Uphold Federal Aviation Regulations (FAR), company policy, and strict confidentiality regarding passenger and schedule information.",
        "Collaborate as a team member with flight crew and support personnel to deliver safe, on-time operations.",
    ]:
        add_bullet(doc, b)

    add_job_header(doc, "Funeral Services Associate", "February 2024 – July 2024")
    add_employer(doc, "Fero Funeral Home")
    for b in [
        "Coordinated time-critical logistics with clients and vendors; maintained meticulous organization and confidentiality.",
        "Prioritized competing requests with limited supervision — transferable to flight coordination and trip support workloads.",
    ]:
        add_bullet(doc, b)

    add_job_header(
        doc, "Airport Manager / Certified Flight Instructor", "January 2020 – January 2024"
    )
    add_employer(doc, "Right Rudder Aviation — Inverness, FL")
    for b in [
        "Served as central point of contact for aircraft owners, charter customers, flight crew, and maintenance partners; received trip requests and coordinated aircraft scheduling support end-to-end.",
        "Performed dispatcher-style trip planning: flight itineraries, resource staging, charter company coordination, and accurate schedule communication to clients and crews.",
        "Arranged trip logistics and passenger/crew services including catering, ground transportation, hotels/staging support, and VIP amenities; confirmed support services against the schedule.",
        "Provided creative solutions to meet client travel needs while ensuring safety of the operation and adherence to regulations and policies.",
        "Maintained working familiarity with client and crew contact information and preferences for assigned accounts.",
        "Ran day-to-day airport operations with limited supervision — fuel restocking, hangars, ramp, parts ordering, facility readiness, and safety oversight.",
        "Sold multi-million-dollar Pipistrel Aircraft as sole U.S. distributor; coordinated aircraft and facility repairs by hiring repair crews and vendors.",
        "Personally transported high-net-worth clients and applied FAA regulatory knowledge, airport information, and operational constraints when assessing trip feasibility.",
    ]:
        add_bullet(doc, b)

    add_heading_line(doc, "Education")
    edu_items = [
        ("Liberty University — Associate of Arts, Language", "Expected Spring 2027"),
        ("GPA 4.0; Dean's List", ""),
        ("Right Rudder Aviation — Commercial Pilot Certificate; Certified Flight Instructor (CFI)", "2020 – 2024"),
        ("Penn Foster — High School Diploma", "2019"),
    ]
    for left, right in edu_items:
        p = doc.add_paragraph()
        set_paragraph_spacing(p, before=2, after=1, line=1.05)
        if right:
            tab_stops = p.paragraph_format.tab_stops
            tab_stops.add_tab_stop(Inches(7.0), alignment=2)
            run = p.add_run(left + "\t" + right)
        else:
            run = p.add_run(left)
        set_run_font(run, size=10.5)

    add_heading_line(doc, "References")
    ref = doc.add_paragraph()
    set_paragraph_spacing(ref, before=2, after=2, line=1.05)
    run = ref.add_run(
        "Charles Lawson — Chief Financial Officer (CFO), Right Rudder Aviation | (407) 734-1442 | Info@flyrra.com"
    )
    set_run_font(run, size=10.5)

    path = "/workspace/Corey_Wagner_Resume_ATS_Flight_Coordinator.docx"
    doc.save(path)
    return path


if __name__ == "__main__":
    fa = build_flight_attendant()
    fc = build_flight_coordinator()
    print("Wrote", fa)
    print("Wrote", fc)
