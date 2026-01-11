from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from qr_reader_django import crud
import json
from qr_reader_django.audit import log_action, get_client_ip
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib import messages
import datetime

# ============= MAGAZINE VIEWS =============

def magazine_dashboard(request):
    """Magazine dashboard - list all magazines for the company"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Please login as a company to access this page'))
        return redirect('company_login')
    
    from viewer.models import Magazine
    company_id = request.session['company_id']
    magazines = Magazine.objects.filter(company_id=company_id).order_by('-modified_at')
    
    context = {
        'magazines': magazines,
        'company_id': company_id,
    }
    return render(request, 'magazine_dashboard.html', context)


def magazine_editor(request, magazine_id=None):
    """Magazine editor - create or edit a magazine"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Please login as a company to access this page'))
        return redirect('company_login')
    
    from viewer.models import Magazine, MagazineArticle, User
    company_id = request.session['company_id']
    
    # Get or create magazine
    if magazine_id:
        magazine = Magazine.objects.filter(id=magazine_id, company_id=company_id).first()
        if not magazine:
            messages.error(request, _('Magazine not found'))
            return redirect('magazine_dashboard')
    else:
        # Create new magazine
        user = User.objects.filter(company_id=company_id).first()
        magazine = Magazine.objects.create(
            company_id=company_id,
            created_by=user,
            title="New Magazine",
            issue_number="1",
            publish_date=datetime.date.today()
        )
        
        MagazineArticle.objects.create(
            magazine=magazine,
            author=user,
            title="Article 1",
            category="News"
        )
        
        return redirect('magazine_editor', magazine_id=magazine.id)
    
    # Get articles
    articles = magazine.articles.all()
    users = User.objects.filter(company_id=company_id, is_active=True)
    
    context = {
        'magazine': magazine,
        'articles': articles,
        'users': users,
        'categories': magazine.get_categories_list(),
    }
    return render(request, 'magazine_editor.html', context)


def magazine_preview(request, magazine_id):
    """Magazine preview - show print-ready preview"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Please login as a company to access this page'))
        return redirect('company_login')
    
    from viewer.models import Magazine
    company_id = request.session['company_id']
    
    magazine = Magazine.objects.filter(id=magazine_id, company_id=company_id).first()
    if not magazine:
        messages.error(request, _('Magazine not found'))
        return redirect('magazine_dashboard')
    
    articles = magazine.articles.all().order_by('order', 'page_number')
    
    context = {
        'magazine': magazine,
        'articles': articles,
    }
    return render(request, 'magazine_preview.html', context)

# ============= MAGAZINE API ENDPOINTS =============

@csrf_exempt
def api_magazine_update(request, magazine_id):
    """API: Update magazine configuration"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import Magazine
    company_id = request.session['company_id']
    
    magazine = Magazine.objects.filter(id=magazine_id, company_id=company_id).first()
    if not magazine:
        return JsonResponse({'error': str(_('Magazine not found'))}, status=404)
    
    try:
        data = json.loads(request.body)
        
        # Update fields
        if 'title' in data:
            magazine.title = data['title']
        if 'issue_number' in data:
            magazine.issue_number = data['issue_number']
        if 'tagline' in data:
            magazine.tagline = data['tagline']
        if 'publish_date' in data:
            magazine.publish_date = data['publish_date']
        if 'template_id' in data:
            magazine.template_id = data['template_id']
        if 'primary_color' in data:
            magazine.primary_color = data['primary_color']
        if 'secondary_color' in data:
            magazine.secondary_color = data['secondary_color']
        if 'background_color' in data:
            magazine.background_color = data['background_color']
        if 'categories' in data:
            magazine.categories = data['categories']
        if 'cover_background_image' in data:
            magazine.cover_background_image = data['cover_background_image']
        if 'cover_header_position' in data:
            magazine.cover_header_position = data['cover_header_position']
        if 'primary_font' in data:
            magazine.primary_font = data['primary_font']
        if 'secondary_font' in data:
            magazine.secondary_font = data['secondary_font']
        if 'text_color' in data:
            magazine.text_color = data['text_color']
        
        magazine.save()
        
        # Log the update
        company = crud.get_company_by_id(company_id)
        if company:
            log_action(
                actor_type='company',
                actor_email=company.email,
                actor_name=company.name,
                action='update',
                message=f'Magazine "{magazine.title}" updated',
                ip_address=get_client_ip(request)
            )
        
        return JsonResponse({'success': True, 'magazine': {
            'id': magazine.id,
            'title': magazine.title,
            'issue_number': magazine.issue_number,
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_magazine_delete(request, magazine_id):
    """API: Delete a magazine"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import Magazine
    company_id = request.session['company_id']
    
    magazine = Magazine.objects.filter(id=magazine_id, company_id=company_id).first()
    if not magazine:
        return JsonResponse({'error': str(_('Magazine not found'))}, status=404)
    
    magazine_title = magazine.title
    magazine.delete()
    
    # Log the deletion
    company = crud.get_company_by_id(company_id)
    if company:
        log_action(
            actor_type='company',
            actor_email=company.email,
            actor_name=company.name,
            action='delete',
            message=f'Magazine "{magazine_title}" deleted',
            ip_address=get_client_ip(request)
        )
    
    return JsonResponse({'success': True})


@csrf_exempt
def api_article_create(request, magazine_id):
    """API: Create a new article"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import Magazine, MagazineArticle, User
    company_id = request.session['company_id']
    
    magazine = Magazine.objects.filter(id=magazine_id, company_id=company_id).first()
    if not magazine:
        return JsonResponse({'error': str(_('Magazine not found'))}, status=404)
    
    try:
        data = json.loads(request.body)
        
        # Get author
        user = User.objects.filter(company_id=company_id).first()
        
        article = MagazineArticle.objects.create(
            magazine=magazine,
            author=user,
            title=data.get('title', 'New Article'),
            category=data.get('category', magazine.get_categories_list()[0])
        )
        
        # Log the creation
        company = crud.get_company_by_id(company_id)
        if company:
            log_action(
                actor_type='company',
                actor_email=company.email,
                actor_name=company.name,
                action='create',
                message=f'Article "{article.title}" created in magazine "{magazine.title}"',
                ip_address=get_client_ip(request)
            )
        
        return JsonResponse({'success': True, 'article': {
            'id': article.id,
            'title': article.title,
            'category': article.category,
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_article_update(request, article_id):
    """API: Update an article"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import MagazineArticle
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': str(_('Article not found'))}, status=404)
    
    try:
        data = json.loads(request.body)
        
        if 'title' in data:
            article.title = data['title']
        if 'teaser' in data:
            article.teaser = data['teaser']
        if 'category' in data:
            article.category = data['category']
        if 'is_main_story' in data:
            article.is_main_story = data['is_main_story']
        if 'is_secondary_story' in data:
            article.is_secondary_story = data['is_secondary_story']
        if 'order' in data:
            article.order = data['order']
        if 'status' in data:
            article.status = data['status']
        
        article.save()
        
        # Log the update
        company = crud.get_company_by_id(company_id)
        if company:
            log_action(
                actor_type='company',
                actor_email=company.email,
                actor_name=company.name,
                action='update',
                message=f'Article "{article.title}" updated',
                ip_address=get_client_ip(request)
            )
        
        return JsonResponse({'success': True, 'article': {
            'id': article.id,
            'title': article.title,
            'status': article.status,
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_article_delete(request, article_id):
    """API: Delete an article"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import MagazineArticle
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': str(_('Article not found'))}, status=404)
    
    article_title = article.title
    article.delete()
    
    # Log the deletion
    company = crud.get_company_by_id(company_id)
    if company:
        log_action(
            actor_type='company',
            actor_email=company.email,
            actor_name=company.name,
            action='delete',
            message=f'Article "{article_title}" deleted',
            ip_address=get_client_ip(request)
        )
    
    return JsonResponse({'success': True})


@csrf_exempt
def api_article_upload_header_image(request, article_id):
    """API: Upload header image for article"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import MagazineArticle
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': str(_('Article not found'))}, status=404)
    
    try:
        if not request.FILES.get('header_image'):
            return JsonResponse({'error': str(_('No image provided'))}, status=400)
        
        article.header_image = request.FILES['header_image']
        article.save()
        
        # Log the upload
        company = crud.get_company_by_id(company_id)
        if company:
            log_action(
                actor_type='company',
                actor_email=company.email,
                actor_name=company.name,
                action='update',
                message=f'Header image uploaded for article "{article.title}"',
                ip_address=get_client_ip(request)
            )
        
        return JsonResponse({'success': True, 'header_image': article.header_image.url})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_article_remove_header_image(request, article_id):
    """API: Remove header image from article"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import MagazineArticle
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': str(_('Article not found'))}, status=404)
    
    try:
        if article.header_image:
            article.header_image.delete()
        article.header_image = None
        article.save()
        
        # Log the removal
        company = crud.get_company_by_id(company_id)
        if company:
            log_action(
                actor_type='company',
                actor_email=company.email,
                actor_name=company.name,
                action='update',
                message=f'Header image removed from article "{article.title}"',
                ip_address=get_client_ip(request)
            )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_content_block_create(request, article_id):
    """API: Create a content block"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import MagazineArticle, ContentBlock
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': str(_('Article not found'))}, status=404)
    
    try:
        # Get next order
        max_order = article.content_blocks.aggregate(Max('order'))['order__max'] or 0
        
        # Check if it's a file upload (image)
        if request.FILES.get('image'):
            block = ContentBlock.objects.create(
                article=article,
                block_type='image',
                order=max_order + 1,
                image=request.FILES['image'],
                alignment='center'
            )
        else:
            # JSON data
            data = json.loads(request.body)
            
            block = ContentBlock.objects.create(
                article=article,
                block_type=data.get('block_type', 'text'),
                order=max_order + 1,
                text_content=data.get('text_content', ''),
                image_url=data.get('image_url', ''),
                alignment=data.get('alignment', 'left')
            )
        
        # Log the creation
        company = crud.get_company_by_id(company_id)
        if company:
            log_action(
                actor_type='company',
                actor_email=company.email,
                actor_name=company.name,
                action='create',
                message=f'Content block ({block.block_type}) created in article "{article.title}"',
                ip_address=get_client_ip(request)
            )
        
        return JsonResponse({'success': True, 'block': {
            'id': block.id,
            'block_type': block.block_type,
            'order': block.order,
        }})
    except json.JSONDecodeError as e:
        return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=400)


@csrf_exempt
def api_content_block_update(request, block_id):
    """API: Update a content block"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import ContentBlock
    company_id = request.session['company_id']
    
    block = ContentBlock.objects.filter(
        id=block_id,
        article__magazine__company_id=company_id
    ).first()
    
    if not block:
        return JsonResponse({'error': str(_('Block not found'))}, status=404)
    
    try:
        data = json.loads(request.body)
        
        if 'text_content' in data:
            block.text_content = data['text_content']
        if 'image_url' in data:
            block.image_url = data['image_url']
        if 'image_caption' in data:
            block.image_caption = data['image_caption']
        if 'alignment' in data:
            block.alignment = data['alignment']
        if 'font_size' in data:
            block.font_size = data['font_size']
        if 'order' in data:
            block.order = data['order']
        
        block.save()
        
        # Log the update
        company = crud.get_company_by_id(company_id)
        if company:
            log_action(
                actor_type='company',
                actor_email=company.email,
                actor_name=company.name,
                action='update',
                message=f'Content block updated in article "{block.article.title}"',
                ip_address=get_client_ip(request)
            )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_content_block_delete(request, block_id):
    """API: Delete a content block"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import ContentBlock
    company_id = request.session['company_id']
    
    block = ContentBlock.objects.filter(
        id=block_id,
        article__magazine__company_id=company_id
    ).first()
    
    if not block:
        return JsonResponse({'error': str(_('Block not found'))}, status=404)
    
    article_title = block.article.title
    block.delete()
    
    # Log the deletion
    company = crud.get_company_by_id(company_id)
    if company:
        log_action(
            actor_type='company',
            actor_email=company.email,
            actor_name=company.name,
            action='delete',
            message=f'Content block deleted from article "{article_title}"',
            ip_address=get_client_ip(request)
        )
    
    return JsonResponse({'success': True})


@csrf_exempt
def api_article_reorder_blocks(request, article_id):
    """API: Reorder content blocks"""
    if request.method != 'POST':
        return JsonResponse({'error': str(_('POST required'))}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import MagazineArticle, ContentBlock
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': str(_('Article not found'))}, status=404)
    
    try:
        data = json.loads(request.body)
        blocks = data.get('blocks', [])
        
        # Update each block's order
        for block_data in blocks:
            block = ContentBlock.objects.filter(
                id=block_data['id'],
                article=article
            ).first()
            if block:
                block.order = block_data['order']
                block.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def api_article_data(request, article_id):
    """API: Get article data with content blocks"""
    if 'company_id' not in request.session:
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    from viewer.models import MagazineArticle
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': str(_('Article not found'))}, status=404)
    
    # Get content blocks
    blocks = []
    for block in article.content_blocks.all():
        block_data = {
            'id': block.id,
            'block_type': block.block_type,
            'order': block.order,
            'alignment': block.alignment,
        }
        
        if block.block_type == 'text':
            block_data['text_content'] = block.text_content
            block_data['font_size'] = block.font_size
        elif block.block_type == 'image':
            block_data['image_url'] = block.image_url
            block_data['image_caption'] = block.image_caption
            if block.image:
                block_data['image'] = block.image.url
        
        blocks.append(block_data)
    
    return JsonResponse({
        'success': True,
        'article': {
            'id': article.id,
            'title': article.title,
            'teaser': article.teaser,
            'category': article.category,
            'is_main_story': article.is_main_story,
            'is_secondary_story': article.is_secondary_story,
            'status': article.status,
            'header_image': article.header_image.url if article.header_image else None,
            'content_blocks': blocks
        }
    })