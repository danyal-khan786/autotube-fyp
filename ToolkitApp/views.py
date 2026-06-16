from django.shortcuts import render

# Create your views here.
    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import VideoAnalysis
from .forms import VideoInputForm, VideoAnalysisCRUDForm
from .services import get_youtube_transcript, analyze_with_cohere, get_video_metadata

@login_required
def dashboard(request):
    """Renders the input form and the user's past analysis history."""
    form = VideoInputForm()
    history = VideoAnalysis.objects.filter(user=request.user)
    return render(request, 'ToolkitApp/dashboard.html', {'form': form, 'history': history})

@login_required
def process_video(request):
    """The hidden workhorse view: handles the POST request, triggers AI, and saves to DB."""
    if request.method == 'POST':
        form = VideoInputForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['youtube_url']
            
            # --- NEW: Fetch Title and Thumbnail ---
            title, thumbnail = get_video_metadata(url)
            
            # Step 1: Rip the Transcript
            transcript, t_error = get_youtube_transcript(url)
            if t_error:
                messages.error(request, f"Transcript Error: {t_error}")
                return redirect('dashboard')
                
            # Step 2: Send to Cohere
            ai_result, a_error = analyze_with_cohere(transcript)
            if a_error:
                messages.error(request, f"AI Error: {a_error}")
                return redirect('dashboard')
                
            # Step 3: Save to Database (Now including Title and Thumbnail)
            analysis = VideoAnalysis.objects.create(
                user=request.user,
                youtube_url=url,
                video_title=title,           # <-- Added
                thumbnail_url=thumbnail,     # <-- Added
                transcript=transcript,
                summary=ai_result.get('summary', ''),
                tone_analysis=ai_result.get('tone_analysis', ''),
                target_audience=ai_result.get('target_audience', ''),
                suggested_titles=ai_result.get('suggested_titles', []),
                seo_tags=ai_result.get('seo_tags', [])
            )
            
            messages.success(request, "Video analyzed successfully!")
            return redirect('results_detail', pk=analysis.pk)
            
    messages.error(request, "Invalid request.")
    return redirect('dashboard')
@login_required
def results_detail(request, pk):
    """Displays the final AI outputs using the read-only CRUD form."""
    analysis = get_object_or_404(VideoAnalysis, pk=pk, user=request.user)
    
    # We pass read_only=True so the user can see the form but can't edit it directly yet
    form = VideoAnalysisCRUDForm(instance=analysis, read_only=True)
    
    return render(request, 'ToolkitApp/results_detail.html', {'analysis': analysis, 'form': form})

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

@login_required
def download_pdf_report(request, pk):
    """Generates a formatted PDF report of the AI analysis."""
    analysis = get_object_or_404(VideoAnalysis, pk=pk, user=request.user)
    
    # Set up the HTTP response to trigger a file download
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="AutoTube_Analysis_{analysis.pk}.pdf"'
    
    # Initialize ReportLab document
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=14)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], spaceBefore=12, spaceAfter=6)
    body_style = styles['BodyText']
    
    story = []
    
    # Header
    story.append(Paragraph("AutoTube AI - Optimization Report", title_style))
    story.append(Paragraph(f"<b>Video Title:</b> {analysis.video_title or 'Unknown'}", body_style))
    story.append(Paragraph(f"<b>URL:</b> {analysis.youtube_url}", body_style))
    story.append(Spacer(1, 12))
    
    # Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(analysis.summary or "No summary generated.", body_style))
    
    # Tone & Audience
    story.append(Paragraph("Demographics & Tone", heading_style))
    story.append(Paragraph(f"<b>Target Audience:</b> {analysis.target_audience or 'General'}", body_style))
    story.append(Paragraph(f"<b>Content Tone:</b> {analysis.tone_analysis or 'Standard'}", body_style))
    
    # Suggested Titles
    story.append(Paragraph("Optimized Titles", heading_style))
    if analysis.suggested_titles:
        title_items = [ListItem(Paragraph(title, body_style)) for title in analysis.suggested_titles]
        story.append(ListFlowable(title_items, bulletType='bullet'))
    
    # SEO Tags
    story.append(Paragraph("SEO Tags & Hashtags", heading_style))
    if analysis.seo_tags:
        tags_string = ", ".join(analysis.seo_tags)
        story.append(Paragraph(tags_string, body_style))
    
    # Build and return the PDF
    doc.build(story)
    return response

def home(request):
    return render(
        request,
        'ToolkitApp/index.html',
        {}
    )


















