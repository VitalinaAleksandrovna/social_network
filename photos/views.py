from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Photo, Comment
from .forms import PhotoForm, CommentForm


def photo_list(request):
    photos = Photo.objects.all().order_by('-created_at')
    return render(request, 'photos/photo_list.html', {'photos': photos})


def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    comments = photo.comments.all().order_by('-created_at')

    if request.method == 'POST' and request.user.is_authenticated:
        if 'like' in request.POST:
            if photo.likes.filter(id=request.user.id).exists():
                photo.likes.remove(request.user)
            else:
                photo.likes.add(request.user)
        elif 'comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.photo = photo
                comment.user = request.user
                comment.save()
                return redirect('photo_detail', photo_id=photo.id)

    comment_form = CommentForm()
    return render(request, 'photos/photo_detail.html', {
        'photo': photo,
        'comments': comments,
        'comment_form': comment_form
    })


@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            return redirect('photo_list')
    else:
        form = PhotoForm()
    return render(request, 'photos/upload_photo.html', {'form': form})
