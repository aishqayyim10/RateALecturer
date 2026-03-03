from django.shortcuts import render, get_object_or_404, redirect
from .models import Lecturer, Review, Comment, Faculty, Profile
from .forms import ReviewForm, CommentForm, LecturerForm, ProfileUpdateForm, CustomRegisterForm
from django.contrib.auth.forms import UserCreationForm, User 
from django.contrib.auth import login
from django.contrib import messages 
from django.db.models import Avg


def home(request):
    # Get the search term from the URL if it exists (e.g., ?q=smith)
    query = request.GET.get('q')
    
    if query:
        # Filter lecturers matching the search query
        lecturers = Lecturer.objects.filter(name__icontains=query).order_by('faculty__name', 'name')
    else:
        # If no search query, show all lecturers
        lecturers = Lecturer.objects.all().order_by('faculty__name', 'name')
        
    return render(request, 'forum/home.html', {
        'lecturers': lecturers,
        'query': query # Pass the query back to the template so we can display it
    })

def lecturer_detail(request, lecturer_id):
    lecturer = get_object_or_404(Lecturer, id=lecturer_id)
    reviews = lecturer.reviews.all().order_by('-created_at')
    
    if request.method == 'POST':
        # Security check: Make sure they are actually logged in before processing
        if not request.user.is_authenticated:
            return redirect('home') # Kick them back to the home page if not logged in

        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.lecturer = lecturer
            
            # ATTACH THE LOGGED-IN USER HERE:
            new_review.user = request.user 
            
            new_review.save()
            return redirect('lecturer_detail', lecturer_id=lecturer.id)
    else:
        form = ReviewForm()
        
    return render(request, 'forum/lecturer_detail.html', {
        'lecturer': lecturer,
        'reviews': reviews,
        'form': form,
        'comment_form': CommentForm()
    })

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # Load both forms with the submitted data (and FILES for the picture!)
        user_form = CustomRegisterForm(request.POST)
        profile_form = ProfileUpdateForm(request.POST, request.FILES)

        # Only proceed if BOTH forms are filled out correctly
        if user_form.is_valid() and profile_form.is_valid():
            # 1. Save the new user account
            user = user_form.save()
            
            # 2. Save the profile data, but pause before committing to the database
            profile = profile_form.save(commit=False)
            # 3. Attach the profile to the newly created user, then save it!
            profile.user = user
            profile.save()

            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.username}!")
            return redirect('home')
    else:
        user_form = CustomRegisterForm()
        profile_form = ProfileUpdateForm()
        
    # Pass both forms to the template
    return render(request, 'forum/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def add_comment(request, review_id):
    if request.method == 'POST' and request.user.is_authenticated:
        review = get_object_or_404(Review, id=review_id)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.review = review
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, "Your reply was posted!")
            
        # Redirect back to the lecturer page after commenting
        return redirect('lecturer_detail', lecturer_id=review.lecturer.id)
        
    return redirect('home')

# Add this at the bottom of forum/views.py
def delete_review(request, review_id):
    # Fetch the review or return 404
    review = get_object_or_404(Review, id=review_id)
    
    # SECURITY CHECK: Is the person making this request the author of the review?
    if request.user == review.user:
        # Save the lecturer's ID before we delete the review so we know where to redirect
        lecturer_id = review.lecturer.id
        
        # Delete it from the database
        review.delete()
        
        # Trigger a green success message
        messages.success(request, "Your review has been deleted.")
        
        # Send them back to that lecturer's page
        return redirect('lecturer_detail', lecturer_id=lecturer_id)
    else:
        # If they try to delete someone else's review, hit them with an error
        messages.error(request, "You do not have permission to delete this review.")
        return redirect('home')

# Add this at the bottom of forum/views.py
def add_lecturer(request):
    # Security check: only logged-in users can add a lecturer
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add a lecturer.")
        return redirect('login')

    if request.method == 'POST':
        form = LecturerForm(request.POST)
        if form.is_valid():
            new_lecturer = form.save()
            messages.success(request, f"{new_lecturer.name} has been added successfully!")
            # Send them directly to the new lecturer's profile page so they can be the first to review!
            return redirect('lecturer_detail', lecturer_id=new_lecturer.id)
    else:
        # Show an empty form
        form = LecturerForm()

    return render(request, 'forum/add_lecturer.html', {'form': form})

def upvote_review(request, review_id):
    if not request.user.is_authenticated:
        return redirect('login')
        
    review = get_object_or_404(Review, id=review_id)
    
    # If the user already upvoted, clicking it again removes the vote (toggle)
    if review.upvotes.filter(id=request.user.id).exists():
        review.upvotes.remove(request.user)
    else:
        # Otherwise, add the upvote and remove any downvote they might have had
        review.upvotes.add(request.user)
        review.downvotes.remove(request.user)
        
    # Redirect back to the lecturer page
    return redirect('lecturer_detail', lecturer_id=review.lecturer.id)

def downvote_review(request, review_id):
    if not request.user.is_authenticated:
        return redirect('login')
        
    review = get_object_or_404(Review, id=review_id)
    
    if review.downvotes.filter(id=request.user.id).exists():
        review.downvotes.remove(request.user)
    else:
        review.downvotes.add(request.user)
        review.upvotes.remove(request.user)
        
    return redirect('lecturer_detail', lecturer_id=review.lecturer.id)

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile, created = Profile.objects.get_or_create(user=request.user)
    user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')

    # No forms here anymore! Just viewing data.
    return render(request, 'forum/profile.html', {
        'profile': user_profile,
        'reviews': user_reviews 
    })

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user_profile)

    return render(request, 'forum/edit_profile.html', {'form': form})

def leaderboard(request):
    # 'annotate' calculates the average rating for sorting
    # We exclude lecturers with no reviews, order them from highest to lowest, and grab the Top 10 ([:10])
    top_lecturers = Lecturer.objects.annotate(
        avg_rating=Avg('reviews__overall_rating')
    ).exclude(avg_rating__isnull=True).order_by('-avg_rating')[:10]

    return render(request, 'forum/leaderboard.html', {'top_lecturers': top_lecturers})

def delete_lecturer(request, lecturer_id):
    # SECURITY CHECK: Make sure the user is logged in AND is a superuser
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete lecturers.")
        return redirect('home')

    # Find the lecturer
    lecturer = get_object_or_404(Lecturer, id=lecturer_id)
    
    # We require a POST request for deletions so it can't be triggered by an accidental link click
    if request.method == 'POST':
        lecturer_name = lecturer.name
        lecturer.delete()
        messages.success(request, f"Lecturer '{lecturer_name}' and all their reviews were successfully deleted.")
        return redirect('home')
        
    return redirect('lecturer_detail', lecturer_id=lecturer.id)

def public_profile(request, username):
    # Find the user by their username, or return a 404 error if they don't exist
    profile_user = get_object_or_404(User, username=username)
    
    # Grab their profile backpack (safely, in case an old test account doesn't have one)
    user_profile = getattr(profile_user, 'profile', None)
    
    # Grab all the reviews they have written
    user_reviews = Review.objects.filter(user=profile_user).order_by('-created_at')
    
    # If they have chosen to make some reviews anonymous, we should hide those from public view
    user_reviews = Review.objects.filter(user=profile_user, is_anonymous=False).order_by('-created_at')

    return render(request, 'forum/public_profile.html', {
        'profile_user': profile_user,
        'profile': user_profile,
        'reviews': user_reviews
    })

def edit_review(request, review_id):
    # Fetch the review
    review = get_object_or_404(Review, id=review_id)
    
    # SECURITY CHECK: Make sure the logged-in user is the author!
    if request.user != review.user:
        messages.error(request, "You can only edit your own reviews.")
        return redirect('lecturer_detail', lecturer_id=review.lecturer.id)
        
    if request.method == 'POST':
        # Pass the existing review as an 'instance' so the form knows it is updating, not creating new
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been successfully updated!")
            # Send them right back to the lecturer page!
            return redirect('lecturer_detail', lecturer_id=review.lecturer.id)
    else:
        # Pre-fill the form with their past ratings and comments
        form = ReviewForm(instance=review)
        
    return render(request, 'forum/edit_review.html', {'form': form, 'lecturer': review.lecturer})