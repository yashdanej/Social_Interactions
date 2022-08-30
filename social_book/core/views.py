from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from . models import *
from django.contrib.auth.decorators import login_required
from itertools import chain
import random
# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    user_following_list = []
    feed = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)    
    for users in user_following:
        user_following_list.append(users.user)
    
    for username in user_following_list:
        feed_lists = Post.objects.filter(user=username)
        feed.append(feed_lists)
    
    feed_list = list(chain(*feed))
    
    # user suggetion
    all_user = User.objects.all()
    user_following_all = []
    
    for user in user_following:
        user_list = User.objects.get(username=user)
        user_following_all.append(user_list)
    
    new_suggetions_list = [x for x in list(all_user) if (x not in list(user_following_all))]# if this list is nnt in this list (except) feature
    current_user = User.objects.filter(username=request.user.username)
    final_suggetions_list = [x for x in list(new_suggetions_list) if (x not in list(current_user))]
    random.shuffle(final_suggetions_list)
    username_profile = []
    username_profile_list = []
    
    for users in final_suggetions_list:
        username_profile.append(users.id)
    
    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)
    
    suggetions_username_profile_list = list(chain(*username_profile_list))
    
    return render(request, 'core/index.html', {'user_profile': user_profile, 'feed_list': feed_list, 'suggetions_username_profile_list': suggetions_username_profile_list[:4]})

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken.')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken.')
                return redirect('signup')
            else:
                # Save user object
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                
                # Log user in and redirect to setting page
                user_login = authenticate(username=username, password=password)
                login(request, user_login)
                
                # Create profile object for new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching.')
            return redirect('signup')
    else:
        return render(request, 'core/signup.html')
    
def signin(request):
    if request.method == "POST":
        username= request.POST['username']
        password= request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('signin')
    return render(request, 'core/signin.html')

@login_required(login_url='signin')
def Logout(request):
    logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method=="POST":
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
        else:
            image = request.FILES.get('image')
        bio = request.POST['bio']
        location = request.POST['location']
        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect('settings')
    return render(request, 'core/setting.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def upload(request):
    if request.method=="POST":
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('index')
    else:
        return redirect('index')
    
@login_required(login_url='signin') 
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        if post.no_of_likes==0:
            return HttpResponse("No like")
        elif post.no_of_likes==1:
            return HttpResponse("Liked by 1 person")
        else:
            like=post.no_of_likes
            return HttpResponse(f"Liked by {like} person")
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        if post.no_of_likes==0:
            return HttpResponse("No like")
        elif post.no_of_likes==1:
            return HttpResponse("Liked by 1 person")
        else:
            like=post.no_of_likes
            return HttpResponse(f"Liked by {like} person")

@login_required(login_url='signin')     
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)
    
    follower = request.user.username
    user = pk
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
        
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'core/profile.html', context)

@login_required(login_url='signin') 
def follow(request):
    if request.method=="POST":
        follower = request.POST['follower']
        user = request.POST['user']
        
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('index')
    
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == "POST":
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)
        username_profile = []
        username_profile_list = []
        for users in username_object:
            username_profile.append(users.id)
            
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
            
        username_profile_list = list(chain(*username_profile_list))
        
    return render(request, 'core/search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})