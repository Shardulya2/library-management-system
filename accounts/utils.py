from django.shortcuts import redirect

def verified_required(view_func):
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('/accounts/user-login/')

        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

       
        if not request.user.is_verified:
            return redirect('/accounts/user-login/')

        return view_func(request, *args, **kwargs)

    return wrapper