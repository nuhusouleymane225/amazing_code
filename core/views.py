from io import BytesIO
from django.shortcuts import render, HttpResponse, Http404
from django.views.generic import DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import get_template
from xhtml2pdf import pisa
from core.models import Foo, FeeRequest, FeeReason
from core.forms import FeeRequestForm


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class PdfViewPage(DetailView):
    template_name = 'core/pdf.html'
    model = Foo
    context_object_name = 'foo'

    def get(self, request, *args, **kwargs):

        foo = self.get_object()
        if self.request.user != foo.user:
            raise Http404

        data = {
            'id': foo.id,
            'username': foo.user.username,
            'amount': foo.amount,
        }
        pdf = render_to_pdf('core/pdf.html', data)
        if pdf is None:
            return Http404  # return meaningful error if you want
        else:
            return HttpResponse(pdf, content_type='application/pdf')


def pdf_view_page(request):
    if request.method == 'GET':
        return render(request, 'core/form.html')

    if request.method == 'POST':

        target_id = request.POST.get('id')

        try:
            foo = Foo.objects.get(id=target_id)
        except Foo.DoesNotExist:
            raise Http404

        if request.user != foo.user:  # Make sure the requesting user owns the object
            raise Http404

        data = {
            'id': foo.id,
            'username': foo.user.username,
            'amount': foo.amount,
        }
        pdf = render_to_pdf('core/pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class FeeRequestCreateView(LoginRequiredMixin, CreateView):

    login_url = '/admin/login/'

    model = FeeRequestForm
    form_class = FeeRequestForm
    template_name = 'core/fee_request_create.html'

    def post(self, request, *args, **kwargs):
        reasons_data = {
            'PSE': request.POST.get('PSE'),
            'PGE': request.POST.get('PGE'),
            'SBK': request.POST.get('SBK'),
            'TXI': request.POST.get('TXI'),
        }

        form = self.form_class(request.POST)
        form_reason = ReasonDataChecker(reasons_data)

        if form.is_valid() and form_reason.is_valid():
            print('can be saved')
            fee_request = form.save(commit=False)
            fee_request.driver = request.user
            fee_request.save()
            form_reason.save(fee_request)
        else:
            pass
            print('can not be saved')
        context = {'form': form, 'has_reason_error': not form_reason.is_valid()}
        return render(request, self.template_name, context)


class ReasonDataChecker:
    _data = None
    _cleaned_data = None

    def __init__(self, data):
        if not isinstance(data, dict):
            self._data = None
        else:
            self._data = data

    def is_valid(self):
        if self._data is None:
            return False
        # sanitize str to int if not can not convert to int force return of False
        for key, val in self._data.items():
            try:
                self._data[key] = int(val)
            except (TypeError, ValueError):
                self._data[key] = None

        is_valid = any(self._data.values())
        self._cleaned_data = self._data if is_valid else None
        return is_valid

    def save(self, fee_request):

        if self._cleaned_data is not None:
            for key, val in self._cleaned_data.items():
                if val is not None:
                    fee_reason = FeeReason(request=fee_request, label=key, quantity=val)
                    fee_reason.save(force_update=True)
                    # le prix est automatiquement defini à la creation grâce à la surcharge de la methode save dans le modele
