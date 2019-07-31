from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *
# Create your views here.
@login_required
def index(request):
    # user = request.user
    # roles = user.userprofile.role.all
    # print(user)

    return render(request, 'crm/index.html')