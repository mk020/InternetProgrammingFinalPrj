from django.shortcuts import render, redirect
from .models import Item, Category, Company, Tag, Comment
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = Item
    fields = ['name', 'description', 'code', 'image', 'price', 'company', 'category']

    template_name = 'shop/item_update_form.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):
            form.instance.author = current_user
            response = super(ItemUpdate, self).form_valid(form)
            self.object.tags.clear()
            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')
                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response

    def get_context_data(self, **kwargs):
        context = super(ItemUpdate,self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = ';'.join(tags_str_list)
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Item.objects.filter(category=None).count
        context['companies'] = Company.objects.all()
        context['no_company_post_count'] = Item.objects.filter(company=None).count
        return context

class ItemCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Item
    fields = ['name','description','code','image','price','company','category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):
            form.instance.author = current_user
            response = super(ItemCreate, self).form_valid(form)
            tags_str = self.request.POST.get('tags_str')
            if tags_str :
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',',';')
                tags_list = tags_str.split(';')
                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response
        else:
            return redirect('/shop/')

    def get_context_data(self, **kwargs):
        context = super(ItemCreate,self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Item.objects.filter(category=None).count
        context['companies'] = Company.objects.all()
        context['no_company_post_count'] = Item.objects.filter(company=None).count
        return context

class ItemList(ListView):
    model = Item
    paginate_by = 8

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ItemList,self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Item.objects.filter(category=None).count
        context['companies'] = Company.objects.all()
        context['no_company_post_count'] = Item.objects.filter(company=None).count
        return context

class ItemSearch(ItemList): # ListView 상속, post_list, post_list.html
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']
        item_list = Item.objects.filter(
            Q(name__contains=q)
        ).distinct()
        return item_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ItemSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search : {q} ({self.get_queryset().count()})'
        return context

class ItemDetail(DetailView):
    model = Item

    def get_context_data(self, **kwargs):
        context = super(ItemDetail,self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Item.objects.filter(category=None).count
        context['companies'] = Company.objects.all()
        context['no_company_post_count'] = Item.objects.filter(company=None).count
        context['comment_form'] = CommentForm
        return context

def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Item,pk=pk)
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

def delete_comment(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        PermissionDenied

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

def category_page(request, slug):
    if slug == 'no_category' :
        category = '미분류'
        item_list = Item.objects.filter(category=None)
    else :
        category = Category.objects.get(slug=slug)
        item_list = Item.objects.filter(category=category)
    return render(request, 'shop/item_list.html', {
        'category' : category,
        'item_list' : item_list,
        'categories' : Category.objects.all(),
        'no_category_item_count' : Item.objects.filter(category=None).count,
        'companies': Company.objects.all(),
        'no_company_item_count': Item.objects.filter(company=None).count
    })

def company_page(request, slug):
    if slug == 'no_company':
        company = '미분류'
        item_list = Item.objects.filter(company=None)
    else:
        company = Company.objects.get(slug=slug)
        item_list = Item.objects.filter(company=company)
    return render(request, 'shop/item_list.html', {
        'company': company,
        'item_list': item_list,
        'companies': Company.objects.all(),
        'no_company_item_count': Item.objects.filter(company=None).count,
        'categories': Category.objects.all(),
        'no_category_item_count': Item.objects.filter(category=None).count
    })

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    item_list = tag.item_set.all()

    return render(request, 'shop/item_list.html', {
        'item_list' : item_list,
        'tag' : tag,
        'categories' : Category.objects.all(),
        'no_category_item_count' : Item.objects.filter(category=None).count,
        'companies': Company.objects.all(),
        'no_company_item_count': Item.objects.filter(company=None).count,
    })

class AccountDetailView(DetailView, LoginRequiredMixin, Comment):
    model = User
    context_object_name = 'target_user'
    template_name = 'shop/my_page.html'

@require_POST
def likes(request, item_pk):
        i = get_object_or_404(Item, pk=item_pk)
        if request.user in i.like_users.all():
            i.like_users.remove(request.user)
        else:
            i.like_users.add(request.user)
        return redirect('/shop/'+str(item_pk))