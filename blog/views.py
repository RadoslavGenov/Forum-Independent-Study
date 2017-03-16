from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count
from .models import Post
from .forms import EmailPostForm, CommentForm, PostForm
from taggit.models import Tag


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_share(request, post_id):#
    #retrieve post by id
    post = get_object_or_404(Post, id=post_id)#, status='published')
    sent = False
    
    if request.method == 'POST':
        #Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recomments you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog', [cd['to']])
            sent = True
            #send email
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent,
                                                    'cd': cd, })

#post_list function
def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        #if page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        #if page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    paginator_flag = True
    return render(request, 'blog/post/list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag,
                                                   'paginator_flag': paginator_flag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    
    #list of active comments for this post
    comments = post.comments.filter(active=True)
    
    if request.method == 'POST':
        #a comment was posted 
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            #Create comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            #assign current post to the comment
            new_comment.post = post
            #now save comment to db
            new_comment.save()
    else:
        comment_form = CommentForm()
        
    #list of similar posts 
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments, 
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts })


def post(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            new_post = post_form.save()
            m_tags = post_form.cleaned_data['tags']
            for tag in m_tags:
                new_post.tags.add(tag)
            new_post.save()
            return redirect('/blog')
    else:
        post_form = PostForm()
    return render(request, 'blog/post/create_post.html', {'post_form': post_form})
