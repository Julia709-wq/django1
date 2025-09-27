from django.forms import CheckboxInput
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView

from blogging.models import BlogPost


class BlogPostCreateView(CreateView):
    model = BlogPost
    fields = ['header', 'content', 'tag']
    widgets = {
        'tag': CheckboxInput(attrs={'class': 'form-check-input'}),
    }
    template_name = 'blogging/blogpost_form.html'
    success_url = reverse_lazy('blogging:main_menu')

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.context_data['error_message'] = 'Ошибка при заполнении данных!'


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blogging/blogpost_list.html'

    def get_queryset(self):
        return BlogPost.objects.filter(tag=True)


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blogging/blogpost_detail.html'
    context_object_name = 'blogposts'

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.views += 1
        self.object.save()
        return self.object

class BlogPostUpdateView(UpdateView):
    model = BlogPost
    fields = ['header', 'content', 'tag']
    success_url = reverse_lazy('blogging:main_menu')

    def get_success_url(self):
        return reverse('blogging:blogpost_detail', args=[self.kwargs.get('pk')])

class BlogPostDeleteView(DeleteView):
    model = BlogPost
    success_url = reverse_lazy('blogging:main_menu')