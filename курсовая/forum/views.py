import json

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Category, Topic, Message, MessageVote
from .forms import CategoryForm, TopicForm, MessageForm

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'forum/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        queryset = Category.objects.annotate(
            topics_count=Count('topics', distinct=True),
            messages_count=Count('topics__messages', distinct=True)
        )
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset.order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class TopicListView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'forum/topic_list.html'
    context_object_name = 'topics'
    paginate_by = 15

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])
        queryset = Topic.objects.filter(category=self.category).annotate(
            messages_count=Count('messages')
        )
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset.order_by('-is_pinned', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['search_query'] = self.request.GET.get('search', '')
        return context

class TopicDetailView(LoginRequiredMixin, DetailView):
    model = Topic
    template_name = 'forum/topic_detail.html'
    context_object_name = 'topic'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages = self.object.messages.filter(parent__isnull=True).select_related('author')
        paginator = Paginator(messages, 20)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context

@login_required
def create_topic(request, category_pk):
    category = get_object_or_404(Category, pk=category_pk)
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.category = category
            topic.author = request.user
            topic.save()
            return JsonResponse({
                'success': True,
                'redirect_url': topic.get_absolute_url()
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@login_required
def create_message(request, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.topic = topic
            message.author = request.user
            message.save()
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                    'author': {
                        'username': message.author.username,
                        'avatar_url': message.author.profile.avatar.url if hasattr(message.author, 'profile') and message.author.profile.avatar else '/static/default_avatar.png'
                    }
                }
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@login_required
def create_reply(request, message_pk):
    parent_message = get_object_or_404(Message, pk=message_pk)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            if parent_message.get_depth() >= 4:
                return JsonResponse({
                    'success': False,
                    'error': 'Максимальная глубина вложенности - 4 уровня'
                })
            reply = form.save(commit=False)
            reply.topic = parent_message.topic
            reply.author = request.user
            reply.parent = parent_message
            reply.save()
            return JsonResponse({
                'success': True,
                'reply': {
                    'id': reply.id,
                    'content': reply.content,
                    'created_at': reply.created_at.strftime('%d.%m.%Y %H:%M'),
                    'author': {
                        'username': reply.author.username,
                        'avatar_url': reply.author.profile.avatar.url if hasattr(reply.author, 'profile') and reply.author.profile.avatar else '/static/default_avatar.png'
                    },
                    'parent_content': parent_message.content[:100],
                    'parent_author': parent_message.author.username,
                    'depth': reply.get_depth()
                }
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@login_required
@require_POST
def vote_message(request, message_pk):
    message = get_object_or_404(Message, pk=message_pk)
    vote_value = int(request.POST.get('vote'))

    if vote_value not in [MessageVote.LIKE, MessageVote.DISLIKE]:
        return JsonResponse({'success': False, 'error': 'Invalid vote value'})

    vote, created = MessageVote.objects.get_or_create(
        message=message,
        user=request.user,
        defaults={'vote': vote_value}
    )

    if not created:
        if vote.vote == vote_value:
            vote.delete()
            vote_value = 0
        else:
            vote.vote = vote_value
            vote.save()

    likes = message.votes.filter(vote=MessageVote.LIKE).count()
    dislikes = message.votes.filter(vote=MessageVote.DISLIKE).count()

    return JsonResponse({
        'success': True,
        'message_id': message_pk,
        'likes': likes,
        'dislikes': dislikes,
        'user_vote': vote_value if created else (0 if vote_value == 0 else vote.vote)
    })

@login_required
def delete_topic(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.user == topic.author or request.user.is_staff:
        topic.delete()
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('forum:category_detail', kwargs={'pk': topic.category.pk})
        })
    return JsonResponse({
        'success': False,
        'error': 'Permission denied'
    })

@login_required
def delete_message(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.user == message.author or request.user.is_staff:
        message.delete()
        return JsonResponse({'success': True})
    return JsonResponse({
        'success': False,
        'error': 'Permission denied'
    })

# Админские функции
@login_required
@require_POST
def create_category(request):
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Permission denied'
        })

    form = CategoryForm(request.POST)
    if form.is_valid():
        category = form.save()
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'title': category.title,
                'description': category.description,
                'topics_count': 0,
                'messages_count': 0
            }
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors
    })

@login_required
@require_POST
def update_category(request, pk):
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Permission denied'
        })

    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST, instance=category)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({
        'success': False,
        'errors': form.errors
    })

@login_required
@require_POST
def delete_category(request, pk):
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Permission denied'
        })

    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return JsonResponse({'success': True})


@require_POST
def update_category_order(request):
    try:
        order_data = json.loads(request.body)
        order = order_data.get('order', [])
        for index, category_id in enumerate(order):
            Category.objects.filter(id=category_id).update(order=index)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})