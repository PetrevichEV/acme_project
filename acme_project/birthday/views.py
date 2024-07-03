from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from .forms import BirthdayForm, CongratulationForm
from .models import Birthday, Congratulation

from .utils import calculate_birthday_countdown

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

class BirthdayListView(ListView):
    model = Birthday
    queryset = Birthday.objects.prefetch_related(
        'tags'
    ).select_related('author')
    ordering = 'id'
    paginate_by = 10


class BirthdayCreateView(LoginRequiredMixin, CreateView):
    model = Birthday
    form_class = BirthdayForm

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)


class BirthdayUpdateView(OnlyAuthorMixin, UpdateView):
    model = Birthday
    form_class = BirthdayForm


class BirthdayDeleteView(OnlyAuthorMixin, DeleteView):
    model = Birthday
    success_url = reverse_lazy('birthday:list')


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['birthday_countdown'] = calculate_birthday_countdown(
            self.object.birthday
        )
        # Записываем в переменную form пустой объект формы.
        context['form'] = CongratulationForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.congratulations.select_related('author')
        )
        return context
    

@login_required
def add_comment(request, pk):
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    birthday = get_object_or_404(Birthday, pk=pk)
    # Функция должна обрабатывать только POST-запросы.
    form = CongratulationForm(request.POST)
    if form.is_valid():
        # Создаём объект поздравления, но не сохраняем его в БД.
        congratulation = form.save(commit=False)
        # В поле author передаём объект автора поздравления.
        congratulation.author = request.user
        # В поле birthday передаём объект дня рождения.
        congratulation.birthday = birthday
        # Сохраняем объект в БД.
        congratulation.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    return redirect('birthday:detail', pk=pk)
 
# from django.shortcuts import get_object_or_404, redirect, render
# from django.core.paginator import Paginator
# from django.views.generic import (
#     CreateView, DeleteView, DetailView, ListView, UpdateView
# )
# from django.urls import reverse_lazy

# from .forms import BirthdayForm
# from .models import Birthday
# from .utils import calculate_birthday_countdown


# Добавим опциональный параметр pk.
# def birthday(request, pk=None):
#     if pk is not None:
#         instance = get_object_or_404(Birthday, pk=pk)
#     else:
#         instance = None
#     form = BirthdayForm(
#         request.POST or None,
#         # Файлы, переданные в запросе, указываются отдельно.
#         files=request.FILES or None,
#         instance=instance
#     )
#     context = {'form': form}
#     # Сохраняем данные, полученные из формы, и отправляем ответ:
#     if form.is_valid():
#         form.save()
#         birthday_countdown = calculate_birthday_countdown(
#             form.cleaned_data['birthday']
#         )
#         context.update({'birthday_countdown': birthday_countdown})
#     return render(request, 'birthday/birthday.html', context)

# class BirthdayMixin:
#     model = Birthday
#     success_url = reverse_lazy('birthday:list')


# class BirthdayFormMixin:
#     form_class = BirthdayForm
#     template_name = 'birthday/birthday.html'


# class BirthdayCreateView(BirthdayMixin, BirthdayFormMixin, CreateView):
#     pass


# class BirthdayUpdateView(BirthdayMixin, BirthdayFormMixin, UpdateView):
#     pass


# class BirthdayDeleteView(BirthdayMixin, DeleteView):
#     pass 


# class BirthdayDetailView(DetailView):
#     model = Birthday 

#     def get_context_data(self, **kwargs):
#         # Получаем словарь контекста:
#         context = super().get_context_data(**kwargs)
#         # Добавляем в словарь новый ключ:
#         context['birthday_countdown'] = calculate_birthday_countdown(
#             # Дату рождения берём из объекта в словаре context:
#             self.object.birthday
#         )
#         # Возвращаем словарь контекста.
#         return context

# class BirthdayMixin:
#     model = Birthday
#     form_class = BirthdayForm
#     template_name = 'birthday/birthday.html'
#     success_url = reverse_lazy('birthday:list')


# # Добавляем миксин первым по списку родительских классов.
# class BirthdayCreateView(BirthdayMixin, CreateView):
#     # Не нужно описывать атрибуты: все они унаследованы от BirthdayMixin.
#     pass


# class BirthdayUpdateView(BirthdayMixin, UpdateView):
#     # И здесь все атрибуты наследуются от BirthdayMixin.
#     pass   

# class BirthdayDeleteView(DeleteView):
#     model = Birthday
#     success_url = reverse_lazy('birthday:list') 

# def delete_birthday(request, pk):
#     # Получаем объект модели или выбрасываем 404 ошибку.
#     instance = get_object_or_404(Birthday, pk=pk)
#     # В форму передаём только объект модели;
#     # передавать в форму параметры запроса не нужно.
#     form = BirthdayForm(instance=instance)
#     context = {'form': form}
#     # Если был получен POST-запрос...
#     if request.method == 'POST':
#         # ...удаляем объект:
#         instance.delete()
#         # ...и переадресовываем пользователя на страницу со списком записей.
#         return redirect('birthday:list')
#     # Если был получен GET-запрос — отображаем форму.
#     return render(request, 'birthday/birthday.html', context)


# class BirthdayListView(ListView):
#     # Указываем модель, с которой работает CBV...
#     model = Birthday
#     # ...сортировку, которая будет применена при выводе списка объектов:
#     ordering = 'id'
#     # ...и даже настройки пагинации:
#     paginate_by = 10
