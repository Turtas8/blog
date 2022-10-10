from rest_framework import serializers
from .models import Category, Post, Comment, PostImages, Like, Favorites


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostListSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Post
        fields = ('id', 'title', 'owner', 'preview')

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['likes_count'] = instance.likes.count()
        return repr


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        exclude = ('id', 'title')


class PostCreateSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = Post
        fields = ('title', 'body', 'category', 'preview', 'images')

    def create(self, validated_data):
        request = self.context.get('request')
        post = Post.objects.create(**validated_data)
        images_data = request.FILES.getlist('images')
        images_objects = [PostImages(post=post, image=image) for image in images_data]
        PostImages.objects.bulk_create(images_objects)
        return post


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Comment
        fields = ('id', 'body', 'post', 'owner')


class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    images = PostImageSerializer(many=True)
    comments = CommentSerializer(many=True)

    class Meta:
        model = Post
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Like
        fields = ('owner', 'post')


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = ('post',)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['posts'] = PostListSerializer(instance.post).data
        return repr
