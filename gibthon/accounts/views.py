from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from gibthon.views import redirect_home


def login(request, redirect_field_name=REDIRECT_FIELD_NAME):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	redirect_to = request.REQUEST.get(redirect_field_name, '')
	
	if request.method == "POST":
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			if not redirect_to or ' ' in redirect_to:
				redirect_to = settings.LOGIN_REDIRECT_URL
			elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
				redirect_to = settings.LOGIN_REDIRECT_URL
			auth_login(request, form.get_user())
	
		if request.session.test_cookie_worked():
			request.session.delete_test_cookie()
    		return HttpResponseRedirect(redirect_to)
	else:
		form = AuthenticationForm(request)
	request.session.set_test_cookie()
	t = loader.get_template('user/login.html')
	c = RequestContext(request, {
		'form':form,
		'title':'Login',
		redirect_field_name:redirect_to,
	})
	return HttpResponse(t.render(c))

def logout(request):
	auth_logout(request)
	return HttpResponseRedirect('/')

@login_required
def profile(request):
	t = loader.get_template('user/profile.html')
	c = RequestContext(request, {
		'title':'Profile',
	})
	return HttpResponse(t.render(c))

def create(request, email_hash):
	t = loader.get_template('user/register.html')
	if request.method == "POST":
		f = UserRegisterForm2(request.POST)
		if f.is_valid(email_hash):
			user = f.save()
			auth_login(request, user)
			return HttpResponseRedirect('/user/profile/')
		else:
			c = RequestContext(request, {
				'title:':'Register',
				'form':f,
				'stage':2,
			})
		return HttpResponse(t.render(c))
	else:
		f = UserRegisterForm2()
		c = RequestContext(request, {
			'title':'Register',
			'form':f,
			'stage':2,
		})
		return HttpResponse(t.render(c))
		

def register(request):
	if request.method == "POST":
		f = UserRegisterForm1(request.POST)
		if f.is_valid():
			RegisterEmail1(f.cleaned_data['email'])
			c = RequestContext(request, {
				'title':'Register',
				'message': 'Thank you for registering - please check your emails for a link to create your account.',
			})
		else:
			c = RequestContext(request, {
				'title':'Register',
				'form':UserRegisterForm1(request.POST),
				'stage':1,
			})
		t = loader.get_template('user/register.html')
		
	else:
		f = UserRegisterForm1()
		t = loader.get_template('user/register.html')
		c = RequestContext(request, {
			'title':'Register',
			'form':f,
			'stage':1,
		})
	return HttpResponse(t.render(c))

@login_required
def inbox(request):
	t = loader.get_template('user/inbox.html')
	c = RequestContext(request, {
		'title':'Inbox',
	})
	return HttpResponse(t.render(c))
