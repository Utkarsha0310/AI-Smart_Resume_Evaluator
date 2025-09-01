import os
import logging
from typing import Dict, List
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import uuid

class ReportGenerator:
    """Generate professional PDF reports for resume analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the report"""
        # Navy blue color scheme
        self.navy_dark = Color(0.039, 0.098, 0.184)  # #0A192F
        self.navy_medium = Color(0.122, 0.251, 0.408)  # #1F4068
        self.navy_light = Color(0.086, 0.141, 0.278)  # #162447
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=self.navy_dark,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.navy_medium,
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.navy_medium,
            spaceAfter=8,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Score style
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=48,
            textColor=self.navy_dark,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, analysis_results: Dict, filename: str) -> str:
        """Generate comprehensive PDF report"""
        try:
            # Create unique filename for report
            report_filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
            report_path = os.path.join('uploads', report_filename)
            
            # Create document
            doc = SimpleDocTemplate(
                report_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build story (content)
            story = []
            
            # Title page
            story.extend(self._create_title_page(analysis_results, filename))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self._create_executive_summary(analysis_results))
            story.append(PageBreak())
            
            # Detailed analysis
            story.extend(self._create_detailed_analysis(analysis_results))
            story.append(PageBreak())
            
            # Recommendations
            story.extend(self._create_recommendations(analysis_results))
            story.append(PageBreak())
            
            # Job role predictions
            story.extend(self._create_job_predictions(analysis_results))
            
            # Build PDF
            doc.build(story)
            
            logging.info(f"Report generated successfully: {report_path}")
            return report_path
            
        except Exception as e:
            logging.error(f"Report generation error: {e}")
            raise
    
    def _create_title_page(self, results: Dict, filename: str) -> List:
        """Create title page"""
        story = []
        
        # Title
        title = Paragraph("Resume Analysis Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Filename
        file_para = Paragraph(f"<b>File:</b> {filename}", self.styles['Normal'])
        story.append(file_para)
        story.append(Spacer(1, 0.2*inch))
        
        # Date
        date_para = Paragraph(f"<b>Analysis Date:</b> {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal'])
        story.append(date_para)
        story.append(Spacer(1, 0.5*inch))
        
        # Overall score (large)
        composite_score = results.get('scores', {}).get('composite', 0)
        score_para = Paragraph(f"{composite_score}/100", self.styles['ScoreStyle'])
        story.append(score_para)
        story.append(Spacer(1, 0.2*inch))
        
        # Performance tier
        tier = results.get('scores', {}).get('tier', 'Unknown')
        tier_para = Paragraph(f"<b>Performance Tier: {tier}</b>", self.styles['CustomSubheading'])
        story.append(tier_para)
        story.append(Spacer(1, 0.5*inch))
        
        # Analysis mode
        mode = "Heavy Mode" if results.get('heavy_mode', False) else "Light Mode"
        mode_para = Paragraph(f"<i>Analysis Mode: {mode}</i>", self.styles['Normal'])
        story.append(mode_para)
        
        return story
    
    def _create_executive_summary(self, results: Dict) -> List:
        """Create executive summary section"""
        story = []
        
        # Section title
        title = Paragraph("Executive Summary", self.styles['CustomHeading'])
        story.append(title)
        
        # Key metrics table
        scores = results.get('scores', {})
        data = [
            ['Metric', 'Score', 'Status'],
            ['Overall Score', f"{scores.get('composite', 0)}/100", self._get_status(scores.get('composite', 0))],
            ['Grammar', f"{scores.get('grammar', 0)}/100", self._get_status(scores.get('grammar', 0))],
            ['Readability', f"{scores.get('readability', 0)}/100", self._get_status(scores.get('readability', 0))],
            ['Formatting', f"{scores.get('formatting', 0)}/100", self._get_status(scores.get('formatting', 0))],
            ['ATS Compatibility', f"{scores.get('ats', 0)}/100", self._get_status(scores.get('ats', 0))],
            ['Keyword Strength', f"{scores.get('keywords', 0)}/100", self._get_status(scores.get('keywords', 0))]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.navy_medium),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), Color(0.95, 0.95, 0.95)),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Key findings
        story.append(Paragraph("Key Findings:", self.styles['CustomSubheading']))
        
        findings = []
        
        # Overall performance
        composite_score = scores.get('composite', 0)
        if composite_score >= 80:
            findings.append("• Excellent overall performance with strong fundamentals")
        elif composite_score >= 70:
            findings.append("• Good foundation with room for targeted improvements")
        elif composite_score >= 60:
            findings.append("• Average performance requiring focused enhancements")
        else:
            findings.append("• Significant improvements needed across multiple areas")
        
        # Specific strengths and weaknesses
        if scores.get('grammar', 0) >= 85:
            findings.append("• Strong grammar and language usage")
        elif scores.get('grammar', 0) < 70:
            findings.append("• Grammar improvements needed for professional presentation")
        
        if scores.get('ats', 0) >= 85:
            findings.append("• Excellent ATS compatibility for automated screening")
        elif scores.get('ats', 0) < 70:
            findings.append("• ATS compatibility issues may affect initial screening")
        
        if scores.get('keywords', 0) >= 80:
            findings.append("• Strong keyword usage for industry relevance")
        elif scores.get('keywords', 0) < 60:
            findings.append("• Limited keyword usage may reduce search visibility")
        
        for finding in findings:
            story.append(Paragraph(finding, self.styles['Normal']))
        
        return story
    
    def _create_detailed_analysis(self, results: Dict) -> List:
        """Create detailed analysis section"""
        story = []
        
        # Section title
        title = Paragraph("Detailed Analysis", self.styles['CustomHeading'])
        story.append(title)
        
        # Grammar Analysis
        story.append(Paragraph("Grammar Analysis", self.styles['CustomSubheading']))
        grammar = results.get('grammar', {})
        grammar_text = f"""
        Your resume has a grammar score of {grammar.get('score', 0)}/100 with {grammar.get('error_count', 0)} 
        potential issues detected. {self._get_grammar_advice(grammar.get('score', 0))}
        """
        story.append(Paragraph(grammar_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Structure Analysis
        story.append(Paragraph("Structure & Formatting", self.styles['CustomSubheading']))
        structure = results.get('structure', {})
        sections = structure.get('sections', {})
        found_sections = [section for section, count in sections.items() if count > 0]
        
        structure_text = f"""
        Your resume includes {len(found_sections)} key sections: {', '.join(found_sections)}. 
        Structure score: {structure.get('score', 0)}/100. 
        {self._get_structure_advice(structure.get('score', 0))}
        """
        story.append(Paragraph(structure_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Keyword Analysis
        story.append(Paragraph("Keyword Analysis", self.styles['CustomSubheading']))
        keywords = results.get('keywords', {})
        top_keywords = keywords.get('top_10', [])[:5]
        keyword_list = ', '.join([kw[0] for kw in top_keywords])
        
        keyword_text = f"""
        Identified {keywords.get('count', 0)} relevant keywords. Top keywords: {keyword_list}. 
        Keyword strength score: {results.get('scores', {}).get('keywords', 0)}/100.
        """
        story.append(Paragraph(keyword_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # ATS Compatibility
        story.append(Paragraph("ATS Compatibility", self.styles['CustomSubheading']))
        ats = results.get('ats', {})
        ats_issues = ats.get('issues', [])
        
        if ats_issues:
            ats_text = f"ATS score: {ats.get('score', 0)}/100. Issues detected: " + '; '.join(ats_issues[:3])
        else:
            ats_text = f"ATS score: {ats.get('score', 0)}/100. No major compatibility issues detected."
        
        story.append(Paragraph(ats_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Readability
        story.append(Paragraph("Readability Analysis", self.styles['CustomSubheading']))
        readability = results.get('readability', {})
        readability_text = f"""
        Readability score: {readability.get('score', 0)}/100 
        (Flesch Reading Ease: {readability.get('flesch_ease', 0):.1f}). 
        {self._get_readability_advice(readability.get('score', 0))}
        """
        story.append(Paragraph(readability_text, self.styles['Normal']))
        
        return story
    
    def _create_recommendations(self, results: Dict) -> List:
        """Create recommendations section"""
        story = []
        
        # Section title
        title = Paragraph("Improvement Recommendations", self.styles['CustomHeading'])
        story.append(title)
        
        recommendations = results.get('recommendations', [])
        
        if not recommendations:
            story.append(Paragraph("No specific recommendations. Your resume performs well across all metrics!", self.styles['Normal']))
            return story
        
        # Group by priority
        high_priority = [r for r in recommendations if r['priority'] == 'High']
        medium_priority = [r for r in recommendations if r['priority'] == 'Medium']
        low_priority = [r for r in recommendations if r['priority'] == 'Low']
        
        # High priority recommendations
        if high_priority:
            story.append(Paragraph("High Priority Actions", self.styles['CustomSubheading']))
            for i, rec in enumerate(high_priority, 1):
                rec_text = f"""
                <b>{i}. {rec['category']}</b><br/>
                <i>Issue:</i> {rec['issue']}<br/>
                <i>Recommendation:</i> {rec['recommendation']}<br/>
                <i>Impact:</i> {rec['impact']}
                """
                story.append(Paragraph(rec_text, self.styles['Normal']))
                story.append(Spacer(1, 0.15*inch))
        
        # Medium priority recommendations
        if medium_priority:
            story.append(Paragraph("Medium Priority Actions", self.styles['CustomSubheading']))
            for i, rec in enumerate(medium_priority, 1):
                rec_text = f"""
                <b>{i}. {rec['category']}</b><br/>
                <i>Recommendation:</i> {rec['recommendation']}
                """
                story.append(Paragraph(rec_text, self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # Low priority recommendations
        if low_priority:
            story.append(Paragraph("Low Priority Actions", self.styles['CustomSubheading']))
            for i, rec in enumerate(low_priority, 1):
                rec_text = f"<b>{i}.</b> {rec['recommendation']}"
                story.append(Paragraph(rec_text, self.styles['Normal']))
        
        return story
    
    def _create_job_predictions(self, results: Dict) -> List:
        """Create job role predictions section"""
        story = []
        
        # Section title
        title = Paragraph("Recommended Job Roles", self.styles['CustomHeading'])
        story.append(title)
        
        predictions = results.get('job_predictions', [])
        
        if not predictions:
            story.append(Paragraph("No specific job role predictions available.", self.styles['Normal']))
            return story
        
        intro_text = """
        Based on your resume content and keyword analysis, here are the job roles 
        that best match your profile:
        """
        story.append(Paragraph(intro_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Create table for job predictions
        data = [['Job Role', 'Match Score', 'Confidence', 'Key Matches']]
        
        for pred in predictions[:5]:  # Top 5 predictions
            matched_keywords = ', '.join(pred.get('matched_keywords', [])[:3])
            data.append([
                pred['role'],
                f"{pred['match_score']}%",
                pred['confidence'],
                matched_keywords
            ])
        
        table = Table(data, colWidths=[2*inch, 1*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.navy_medium),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), Color(0.95, 0.95, 0.95)),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Additional advice
        if predictions:
            best_match = predictions[0]
            advice_text = f"""
            <b>Career Guidance:</b> Your strongest match is for {best_match['role']} roles 
            with a {best_match['match_score']}% compatibility score. Focus on developing 
            skills and experience in this area for the best career prospects.
            """
            story.append(Paragraph(advice_text, self.styles['Normal']))
        
        return story
    
    def _get_status(self, score: float) -> str:
        """Get status based on score"""
        if score >= 85:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 65:
            return "Average"
        else:
            return "Needs Work"
    
    def _get_grammar_advice(self, score: float) -> str:
        """Get grammar advice based on score"""
        if score >= 90:
            return "Excellent grammar with minimal issues."
        elif score >= 80:
            return "Good grammar with minor improvements needed."
        elif score >= 70:
            return "Some grammar issues detected. Consider proofreading."
        else:
            return "Multiple grammar issues found. Professional editing recommended."
    
    def _get_structure_advice(self, score: float) -> str:
        """Get structure advice based on score"""
        if score >= 85:
            return "Well-structured resume with all essential sections."
        elif score >= 70:
            return "Good structure with minor improvements possible."
        else:
            return "Consider adding missing sections for better organization."
    
    def _get_readability_advice(self, score: float) -> str:
        """Get readability advice based on score"""
        if score >= 80:
            return "Excellent readability for professional audience."
        elif score >= 60:
            return "Good readability with minor adjustments possible."
        else:
            return "Consider simplifying language for better clarity."
