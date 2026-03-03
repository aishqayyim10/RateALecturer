from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Faculty(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Profile(models.Model):
    # Link this profile to exactly one User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Year and Semester choices
    YEAR_CHOICES = [('1', 'Year 1'), ('2', 'Year 2'), ('3', 'Year 3'), ('4', 'Year 4'), ('Other', 'Other')]
    SEM_CHOICES = [('1', 'Semester 1'), ('2', 'Semester 2'), ('3', 'Semester 3')]
    
    year = models.CharField(max_length=10, choices=YEAR_CHOICES, default='1')
    semester = models.CharField(max_length=10, choices=SEM_CHOICES, default='1')
    
    # Upload profile pictures to an 'avatars' folder. Default to a blank image if none is provided.
    profile_picture = models.ImageField(upload_to='avatars/', default='avatars/default.jpg', null=True, blank=True)
    
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us a bit about yourself!")

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Lecturer(models.Model):
    name = models.CharField(max_length=200)
    # Put back the ForeignKey link
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=100, help_text="e.g., Data Structures, Operating Systems")
    def __str__(self):
        return self.name
    @property
    def average_rating(self):
        # Calculate the average of the 'overall_rating' from all related reviews
        avg = self.reviews.aggregate(Avg('overall_rating'))['overall_rating__avg']
        if avg is not None:
            return round(avg, 1) # Round it to 1 decimal place (e.g., 4.2)
        return 0 # Return 0 if nobody has reviewed them yet
    

class Review(models.Model):
    # Link the review to a specific lecturer and the user who wrote it
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    difficulty = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    would_take_again = models.BooleanField(default=True)
    comment = models.TextField()
    upvotes = models.ManyToManyField(User, related_name='upvoted_reviews', blank=True)
    downvotes = models.ManyToManyField(User, related_name='downvoted_reviews', blank=True)
    is_anonymous = models.BooleanField(default=False)
    
    # Automatically save the date and time the review was created
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    # Link to the specific review being discussed
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    # Link to the user who wrote the comment
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # The actual text of the discussion
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        # Check if the user exists before trying to get the username
        if self.user:
            return f"Comment on review for {self.review.lecturer.name} by {self.user.username}"
            return f"Comment on review for {self.review.lecturer.name} by Anonymous"